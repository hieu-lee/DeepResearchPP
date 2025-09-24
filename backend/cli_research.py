from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple

from .solver import Solver
from .judge import Judge
from .research import ResearchPipeline, ResearchConfig
from .result_refiner import ResultRefiner
from .cli_helpers import _append_correct_result_json, _write_seed_file


def request_proof(question: str, model: str = "gpt-5") -> tuple[bool, str]:
    """Run one or more prover/judge pairs in parallel and return the result.

    If the environment variable DEEPRESEARCH_SOLVER_PAIRS is set to an integer > 1,
    we launch that many Solver instances in parallel (each with its own Prover and Judges),
    and return the first success if any, else the most informative failure (longest feedback).
    """
    try:
        pairs = int(os.getenv("DEEPRESEARCH_SOLVER_PAIRS", "1") or "1")
    except Exception:
        pairs = 1

    if pairs <= 1:
        solver = Solver(model=model)
        return solver.solve(problem=question)

    def _run_one() -> tuple[bool, str]:
        s = Solver(model=model)
        return s.solve(problem=question)

    results: list[tuple[bool, str]] = []
    first_success: tuple[bool, str] | None = None
    with ThreadPoolExecutor(max_workers=pairs) as ex:
        futs = [ex.submit(_run_one) for _ in range(pairs)]
        for fut in as_completed(futs):
            ok, payload = fut.result()
            results.append((ok, payload))
            if ok and first_success is None:
                first_success = (ok, payload)
                # Note: we don't cancel other runs to ensure logs are created; they will finish soon enough.
    if first_success is not None:
        return first_success
    # Choose the failure with the longest feedback to be more informative
    if results:
        return max(results, key=lambda x: len(x[1] or ""))
    return False, "No result produced."


def _map_model(name: str, *, has_tools: bool = False, is_prover: bool = False) -> str:
    if name == "gpt-oss-120b":
        if is_prover:
            return "openai/gpt-oss-120b"
        return "o4-mini" if has_tools else "openai/gpt-oss-120b"
    return name


def run_automate_math_research(
    seed_result: str | list[str],
    model: str = "gpt-5",
    research_guideline: str | None = None,
) -> tuple[list[tuple[str, str]], str]:
    logger = logging.getLogger("backend.research_flow")
    try:
        seed_len = len(seed_result) if isinstance(seed_result, list) else len(str(seed_result or ""))
    except Exception:
        seed_len = 0
    logger.info(
        "[Phase] Start research pipeline (model=%s, guideline=%s, seeds_len=%s)",
        model,
        bool(research_guideline),
        seed_len,
    )
    # Literature review
    logger.info("[Phase] Literature review: begin")

    pipeline = ResearchPipeline(
        ResearchConfig(
            lit_model=_map_model(model, has_tools=True),
            predict_model=_map_model(model, has_tools=True),
            prove_model=_map_model(model, has_tools=True),
            reporter_model=(
                "o4-mini" if model == "gpt-oss-120b" else _map_model(model, has_tools=False)
            ),
            novelty_model=_map_model(model, has_tools=True),
            research_guideline=research_guideline,
        )
    )
    lit = pipeline.literature_review(seed_result)
    try:
        logger.info("[Phase] Literature review: done (results=%d)", len(lit.results))
    except Exception:
        logger.info("[Phase] Literature review: done")

    # Predict results and filter by novelty
    logger.info("[Phase] Prediction: begin")
    preds = pipeline.predict(lit)
    try:
        logger.info(
            "[Phase] Prediction: done (predicted=%d)",
            len(getattr(preds, "predicted_results", []) or []),
        )
    except Exception:
        logger.info("[Phase] Prediction: done")
    logger.info("[Phase] Novelty check: begin")
    novel_statements = pipeline.novelty_filter(lit, preds)
    logger.info(
        "[Phase] Novelty check: kept %d/%d",
        len(novel_statements),
        len(getattr(preds, "predicted_results", []) or []),
    )

    # Attempt proofs in parallel; instantiate an isolated Solver per statement
    results: list[tuple[str, str]] = []
    futures = []
    refiner = ResultRefiner(model=_map_model(model, has_tools=False), reasoning_effort="medium")

    def _prove_stmt(statement: str) -> tuple[bool, str]:
        local_solver = Solver(model=model)
        return local_solver.solve(statement, 8, lit)

    logger.info("[Phase] Proving: begin (candidates=%d)", len(novel_statements))
    with ThreadPoolExecutor(max_workers=12) as ex:
        for stmt in novel_statements:
            futures.append((stmt, ex.submit(_prove_stmt, stmt)))
        for stmt, fut in futures:
            ok, proof_or_feedback = fut.result()
            if not ok:
                logger.info(
                    "[Proving] Failed: %s",
                    (stmt[:80] + "…") if len(stmt) > 80 else stmt,
                )
                continue
            logger.info(
                "[Proving] Success: %s", (stmt[:80] + "…") if len(stmt) > 80 else stmt
            )

            def _refine_and_select(base_stmt: str, base_proof: str) -> tuple[str, str]:
                try:
                    refined = refiner.refine(base_stmt, base_proof)
                except Exception:
                    refined = None
                if refined is not None:
                    rs, rp = refined
                else:
                    rs, rp = base_stmt, base_proof
                # Attempt tighten and judge
                try:
                    tightened = refiner.tighten(rs, rp)
                    if tightened is not None:
                        t_stmt, t_proof = tightened
                        j = Judge(model=_map_model(model, has_tools=True))
                        jres = j.assess(t_stmt, t_proof)
                        if jres.correctness:
                            logger.info("[Proving] Tighten accepted by Judge")
                            return t_stmt, t_proof
                        else:
                            logger.info(
                                "[Proving] Tighten rejected by Judge; keeping refined/original"
                            )
                except Exception:
                    logger.exception(
                        "[Proving] Tighten/Judge failed; keeping refined/original"
                    )
                return rs, rp

            rs, rp = _refine_and_select(stmt, proof_or_feedback)
            results.append((rs, rp))

    # Compile final report from literature context and successful results
    logger.info("[Phase] Proving: done (accepted=%d)", len(results))
    logger.info("[Phase] Report: begin")
    report = pipeline.compile_final_report(lit, results)
    logger.info("[Phase] Report: done (length=%d)", len(report.report_markdown or ""))
    logger.info("[Phase] Pipeline complete")
    return results, report.report_markdown


def run_continuous_math_research(
    seeds: str | list[str],
    *,
    model: str = "gpt-5",
    research_guideline: str | None = None,
    correct_out_path: str = "correct_predicted_results.json",
    seed_file_path: str | None = None,
) -> None:
    """Run the research loop until no predicted result can be proved.

    Each time a proof is found, append it immediately to correct_out_path.
    The list of proved statements is appended to the seed list for the next iteration.
    """
    # Normalize seeds to list[str]
    if isinstance(seeds, str):
        current_seeds: list[str] = [seeds]
    else:
        current_seeds = list(seeds)

    # Track seen statements to avoid duplicates growing unboundedly
    seen_statements = set(current_seeds)

    pipeline = ResearchPipeline(
        ResearchConfig(
            lit_model=model,
            predict_model=model,
            prove_model=model,
            research_guideline=research_guideline,
        )
    )

    iteration = 1
    logger = logging.getLogger(__name__)
    while True:
        logger.info("[Continuous] Iteration %d: seeds=%d", iteration, len(current_seeds))
        # Literature review with possibly multiple seeds
        lit = pipeline.literature_review(current_seeds)

        # Predict and filter by novelty
        preds = pipeline.predict(lit)
        novel_statements = pipeline.novelty_filter(lit, preds)
        if not novel_statements:
            logger.info("[Continuous] Iteration %d: no novel predictions; stopping.", iteration)
            break

        proved_this_round: list[tuple[str, str]] = []

        def _prove_stmt(statement: str) -> tuple[bool, str]:
            local_solver = Solver(model=model)
            return local_solver.solve(statement, 8, lit)

        refiner = ResultRefiner(model=model, reasoning_effort="medium")

        with ThreadPoolExecutor(max_workers=12) as ex:
            future_map = {ex.submit(_prove_stmt, stmt): stmt for stmt in novel_statements}
            for fut in as_completed(future_map):
                stmt = future_map[fut]
                try:
                    ok, proof_or_feedback = fut.result()
                except Exception as e:
                    logger.warning("[Continuous] Prover raised for a statement: %s", e)
                    continue
                if ok:
                    # Refine, then attempt tightening validated by Judge; fall back to refined/original
                    try:
                        refined = refiner.refine(stmt, proof_or_feedback)
                    except Exception as e:
                        logger.warning("[Continuous] Refiner failed; using original result: %s", e)
                        refined = None
                    if refined is not None:
                        base_stmt, base_proof = refined
                    else:
                        base_stmt, base_proof = stmt, proof_or_feedback

                    chosen_stmt, chosen_proof = base_stmt, base_proof
                    try:
                        tightened = refiner.tighten(base_stmt, base_proof)
                    except Exception as e:
                        logger.warning(
                            "[Continuous] Tighten step failed; keeping refined result: %s", e
                        )
                        tightened = None
                    if tightened is not None:
                        t_stmt, t_proof = tightened
                        try:
                            j = Judge(model=model)
                            jres = j.assess(t_stmt, t_proof)
                            if jres.correctness:
                                chosen_stmt, chosen_proof = t_stmt, t_proof
                                logger.info(
                                    "[Continuous] Tightened statement accepted by Judge"
                                )
                            else:
                                logger.info(
                                    "[Continuous] Tightened statement rejected by Judge; using refined/original"
                                )
                        except Exception as e:
                            logger.warning(
                                "[Continuous] Judge failed on tightened result; using refined/original: %s",
                                e,
                            )

                    proved_this_round.append((chosen_stmt, chosen_proof))
                    _append_correct_result_json(
                        correct_out_path, chosen_stmt, chosen_proof
                    )
                    logger.info(
                        "[Continuous] Proof accepted; appended to %s", correct_out_path
                    )

        if not proved_this_round:
            logger.info("[Continuous] Iteration %d: no proofs succeeded; stopping.", iteration)
            break

        # Append proved statements to seeds for the next iteration (deduplicated)
        for stmt, _proof in proved_this_round:
            if stmt not in seen_statements:
                current_seeds.append(stmt)
                seen_statements.add(stmt)

        # Persist updated seeds to file if a seed file path was provided
        if seed_file_path:
            try:
                seed_path_obj = Path(seed_file_path).expanduser().resolve()
                _write_seed_file(seed_path_obj, current_seeds)
                logger.info(
                    "[Continuous] Updated seed file: %s (count=%d)",
                    seed_path_obj,
                    len(current_seeds),
                )
            except Exception as e:
                logger.warning("[Continuous] Failed to update seed file: %s", e)

        iteration += 1
