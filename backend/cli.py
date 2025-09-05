import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional
import logging
import re

from .solver import Solver
from .judge import Judge
from .research import ResearchPipeline, ResearchConfig
from .result_refiner import ResultRefiner


def request_proof(question: str, model: str = "gpt-5") -> tuple[bool, str]:
    solver = Solver(model=model)
    return solver.solve(problem=question)


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
    logger.info("[Phase] Start research pipeline (model=%s, guideline=%s, seeds_len=%s)", model, bool(research_guideline), seed_len)
    # Literature review
    logger.info("[Phase] Literature review: begin")
    def _map_model(name: str, *, has_tools: bool = False, is_prover: bool = False) -> str:
        if name == "gpt-oss-120b":
            if is_prover:
                return "openai/gpt-oss-120b"
            return "o4-mini" if has_tools else "openai/gpt-oss-120b"
        return name

    pipeline = ResearchPipeline(
        ResearchConfig(
            lit_model=_map_model(model, has_tools=True),
            predict_model=_map_model(model, has_tools=True),
            prove_model=_map_model(model, has_tools=True),
            reporter_model=("o4-mini" if model == "gpt-oss-120b" else _map_model(model, has_tools=False)),
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
        logger.info("[Phase] Prediction: done (predicted=%d)", len(getattr(preds, "predicted_results", []) or []))
    except Exception:
        logger.info("[Phase] Prediction: done")
    logger.info("[Phase] Novelty check: begin")
    novel_statements = pipeline.novelty_filter(lit, preds)
    logger.info("[Phase] Novelty check: kept %d/%d", len(novel_statements), len(getattr(preds, "predicted_results", []) or []))

    # Attempt proofs in parallel; instantiate an isolated Solver per statement
    from concurrent.futures import ThreadPoolExecutor, as_completed

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
                logger.info("[Proving] Failed: %s", (stmt[:80] + "…") if len(stmt) > 80 else stmt)
                continue
            logger.info("[Proving] Success: %s", (stmt[:80] + "…") if len(stmt) > 80 else stmt)
            # Launch refinement + tighten + judge in parallel per successful proof
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
                            logger.info("[Proving] Tighten rejected by Judge; keeping refined/original")
                except Exception:
                    logger.exception("[Proving] Tighten/Judge failed; keeping refined/original")
                return rs, rp

            # Execute immediately (already in parallel prove loop); could be offloaded but keep bounded
            chosen_stmt, chosen_proof = _refine_and_select(stmt, proof_or_feedback)
            results.append((chosen_stmt, chosen_proof))

    # Compile final report from literature context and successful results
    logger.info("[Phase] Proving: done (accepted=%d)", len(results))
    logger.info("[Phase] Report: begin")
    report = pipeline.compile_final_report(lit, results)
    logger.info("[Phase] Report: done (length=%d)", len(report.report_markdown or ""))
    logger.info("[Phase] Pipeline complete")
    return results, report.report_markdown


def _parse_seed_content(text: str) -> str | list[str]:
    """Parse seed content as JSON list[str] if possible; otherwise return the raw string.

    Accepts either a single statement string or a JSON array of statement strings.
    """
    try:
        import json as _json

        val = _json.loads(text)
        if isinstance(val, list) and all(isinstance(x, str) for x in val):
            return val
        if isinstance(val, str):
            return val
        # Fallback to raw text if not list[str] or string
        return text
    except Exception:
        # Heuristic 1: bracketed list of quoted items with unescaped LaTeX backslashes
        stripped = text.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            # Extract all top-level double-quoted segments without interpreting escapes
            # This tolerates LaTeX like \mathrm without requiring JSON escapes
            items = re.findall(r'"([^\"]*)"', stripped, flags=re.S)
            items = [s.strip() for s in items if s and s.strip()]
            if items:
                return items
        # Heuristic 2: blank-line delimited multiple seeds
        blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
        if len(blocks) > 1:
            return blocks
        return text


def _append_correct_result_json(path: str, statement: str, proof_markdown: str) -> None:
    """Append a correct result to a JSON array file in a durable way.

    If the file does not exist or is invalid, create it with a single-element array.
    """
    obj = {"statement": statement, "proof_markdown": proof_markdown}
    try:
        p = Path(path).expanduser().resolve()
        if p.exists():
            try:
                raw = p.read_text(encoding="utf-8")
                data = json.loads(raw) if raw.strip() else []
                if not isinstance(data, list):
                    data = []
            except Exception:
                data = []
        else:
            data = []
        data.append(obj)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        # Best-effort fallback: write a minimal JSON array
        try:
            Path(path).write_text(json.dumps([obj], indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


def _write_seed_file(path: Path, seeds: list[str]) -> None:
    """Write seeds to file deterministically as a JSON array of strings.

    If the directory does not exist, attempt to create it. Best-effort; errors are swallowed.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Maintain stable ordering for reproducibility
        unique = list(dict.fromkeys(seeds))
        path.write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


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

        # Prove predictions in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed

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
                        logger.warning("[Continuous] Tighten step failed; keeping refined result: %s", e)
                        tightened = None
                    if tightened is not None:
                        t_stmt, t_proof = tightened
                        try:
                            j = Judge(model=model)
                            jres = j.assess(t_stmt, t_proof)
                            if jres.correctness:
                                chosen_stmt, chosen_proof = t_stmt, t_proof
                                logger.info("[Continuous] Tightened statement accepted by Judge")
                            else:
                                logger.info("[Continuous] Tightened statement rejected by Judge; using refined/original")
                        except Exception as e:
                            logger.warning("[Continuous] Judge failed on tightened result; using refined/original: %s", e)

                    proved_this_round.append((chosen_stmt, chosen_proof))
                    # Persist immediately with chosen content
                    _append_correct_result_json(correct_out_path, chosen_stmt, chosen_proof)
                    logger.info("[Continuous] Proof accepted; appended to %s", correct_out_path)

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
                logger.info("[Continuous] Updated seed file: %s (count=%d)", seed_path_obj, len(current_seeds))
            except Exception as e:
                logger.warning("[Continuous] Failed to update seed file: %s", e)

        iteration += 1


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask an LLM to produce a rigorous Markdown proof for a given statement.",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Mathematical statement to prove. If omitted, will read from stdin.",
    )
    parser.add_argument(
        "-f",
        "--in-file",
        dest="in_file",
        default=None,
        help="Path to a file containing the problem statement to prove.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="gpt-5",
        help="Model name (default: gpt-5)",
    )
    parser.add_argument(
        "--research",
        action="store_true",
        help="Run the automate math research pipeline instead of a single proof.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuous research loop: iterate predictions->proofs until none can be proved; append successes to correct_predicted_results.json (configurable via --correct-out)",
    )
    parser.add_argument(
        "-S",
        "--seed-file",
        dest="seed_file",
        default=None,
        help="Path to a file containing the seed result (LaTeX) for research mode.",
    )
    parser.add_argument(
        "--research-guideline",
        dest="research_guideline",
        default=None,
        help=(
            "High-level directive to steer predictions, e.g. 'solve Riemann hypothesis' or "
            "'improve post-training efficiency for LLMs'."
        ),
    )
    parser.add_argument(
        "--ollama",
        action="store_true",
        help="Use an Ollama server (OpenAI-compatible). Sets base URL and defaults model to gpt-oss:20b if -m not provided.",
    )
    parser.add_argument(
        "--google",
        action="store_true",
        help="Use Google Generative AI. Defaults model to gemini-2.5-pro if -m not provided.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the response as JSON {\"markdown\": ...} instead of plain Markdown.",
    )
    parser.add_argument(
        "--refine-json-result",
        dest="refine_json_path",
        default=None,
        help=(
            "Path to a JSON results file (array of {statement, proof_markdown}); refines all entries in parallel and updates the file."
        ),
    )
    parser.add_argument(
        "-o",
        "--out",
        default=None,
        help="Optional path to write the Markdown proof to.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress logs (stderr).",
    )
    parser.add_argument(
        "--correct-out",
        dest="correct_out_path",
        default=None,
        help="Path to append correct results JSON in --continuous mode (default: correct_predicted_results.json)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    # Configure logging (stderr) for progress visibility
    log_level = logging.ERROR if args.quiet else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
        force=True,
    )
    logger = logging.getLogger(__name__)

    # Provider selection and environment wiring
    if args.ollama and args.google:
        print("Error: --ollama and --google are mutually exclusive.", file=sys.stderr)
        return 2

    if args.ollama:
        # Respect an explicit override if already set
        if not os.getenv("OPENAI_BASE_URL"):
            os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:11434/v1"
        # Some OpenAI SDK versions require an API key to be set even if the backend ignores it
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_PATH")):
            os.environ["OPENAI_API_KEY"] = "ollama"
        # If the user did not specify a model explicitly (parser default is gpt-5), switch to gpt-oss:20b
        if args.model == "gpt-5":
            args.model = "gpt-oss:20b"
        # Signal provider selection to our wrapper
        os.environ["LLM_PROVIDER"] = "openai"
    elif args.google:
        if args.model == "gpt-5":
            args.model = "gemini-2.5-pro"
        os.environ["LLM_PROVIDER"] = "google"

    # Batch refine an existing JSON results file and exit (handled early to avoid stdin prompt)
    if args.refine_json_path:
        try:
            p = Path(args.refine_json_path).expanduser().resolve()
            raw = p.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else []
            if not isinstance(data, list):
                raise ValueError("JSON root must be a list")
        except Exception as e:
            print(json.dumps({"error": f"Failed to read results JSON: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 2

        from concurrent.futures import ThreadPoolExecutor, as_completed
        refiner = ResultRefiner(model=(_map_model(args.model, has_tools=False) if ' _map_model' in globals() else args.model), reasoning_effort="medium")

        def _refine_item(item: dict) -> dict:
            stmt = str(item.get("statement", ""))
            proof = str(item.get("proof_markdown", ""))
            if not stmt or not proof:
                return item
            try:
                # First pass: refinement
                res = refiner.refine(stmt, proof)
                if res is not None:
                    base_stmt, base_proof = res
                else:
                    base_stmt, base_proof = stmt, proof
                # Second pass: tightening with judge validation
                tightened = refiner.tighten(base_stmt, base_proof)
                if tightened is not None:
                    t_stmt, t_proof = tightened
                    j = Judge(model=(_map_model(args.model, has_tools=True) if ' _map_model' in globals() else args.model))
                    jres = j.assess(t_stmt, t_proof)
                    if jres.correctness:
                        return {"statement": t_stmt, "proof_markdown": t_proof}
                return {"statement": base_stmt, "proof_markdown": base_proof}
            except Exception:
                pass
            return {"statement": stmt, "proof_markdown": proof}

        updated: list[dict] = []
        with ThreadPoolExecutor(max_workers=12) as ex:
            fut_map = {ex.submit(_refine_item, item): idx for idx, item in enumerate(data)}
            for fut in as_completed(fut_map):
                try:
                    updated.append(fut.result())
                except Exception:
                    idx = fut_map[fut]
                    itm = data[idx]
                    updated.append({
                        "statement": str(itm.get("statement", "")),
                        "proof_markdown": str(itm.get("proof_markdown", "")),
                    })

        try:
            p.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(json.dumps({"error": f"Failed to write updated JSON: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 1

        if args.json:
            print(json.dumps({"updated": len(updated), "path": str(p)}, indent=2, ensure_ascii=False))
        else:
            print(f"Refined and updated {len(updated)} entries at {p}")
        return 0

    # Prefer input from file if provided
    question = None
    if args.in_file:
        try:
            path = Path(args.in_file).expanduser().resolve()
            question = path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            return 2
    else:
        question = args.question

    # If in research mode and a seed file is provided, prefer it over --in-file/positional input
    if (args.research or args.continuous) and args.seed_file:
        try:
            seed_path = Path(args.seed_file).expanduser().resolve()
            question = seed_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"Error reading seed file: {e}", file=sys.stderr)
            return 2
    if not question:
        if sys.stdin.isatty():
            print("Enter the statement to prove, then press Ctrl-D:", file=sys.stderr)
        question = sys.stdin.read().strip()
    if not question:
        print("Error: no statement provided.", file=sys.stderr)
        return 2

    # Ensure API key presence early for clearer error message
    provider = (os.getenv("LLM_PROVIDER") or "openai").lower()
    if provider == "google":
        if not os.getenv("GOOGLE_API_KEY"):
            logger.warning("GOOGLE_API_KEY not set. The request may fail unless the client is otherwise configured.")
    else:
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_PATH")):
            logger.warning("OPENAI_API_KEY not set. The request may fail unless the client is otherwise configured.")

    # Remove special geometry classification mode; '@' prefix no longer has special meaning

    # Batch refine an existing JSON results file and exit
    if args.refine_json_path:
        try:
            p = Path(args.refine_json_path).expanduser().resolve()
            raw = p.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else []
            if not isinstance(data, list):
                raise ValueError("JSON root must be a list")
        except Exception as e:
            print(json.dumps({"error": f"Failed to read results JSON: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 2

        from concurrent.futures import ThreadPoolExecutor, as_completed
        refiner = ResultRefiner(model=args.model, reasoning_effort="medium")

        def _refine_item(item: dict) -> dict:
            stmt = str(item.get("statement", ""))
            proof = str(item.get("proof_markdown", ""))
            if not stmt or not proof:
                return item
            try:
                # First pass: refinement
                res = refiner.refine(stmt, proof)
                if res is not None:
                    base_stmt, base_proof = res
                else:
                    base_stmt, base_proof = stmt, proof
                # Second pass: tightening with judge validation
                tightened = refiner.tighten(base_stmt, base_proof)
                if tightened is not None:
                    t_stmt, t_proof = tightened
                    j = Judge(model=args.model)
                    jres = j.assess(t_stmt, t_proof)
                    if jres.correctness:
                        return {"statement": t_stmt, "proof_markdown": t_proof}
                return {"statement": base_stmt, "proof_markdown": base_proof}
            except Exception:
                pass
            return {"statement": stmt, "proof_markdown": proof}

        updated: list[dict] = []
        with ThreadPoolExecutor(max_workers=12) as ex:
            fut_map = {ex.submit(_refine_item, item): idx for idx, item in enumerate(data)}
            for fut in as_completed(fut_map):
                try:
                    updated.append(fut.result())
                except Exception:
                    idx = fut_map[fut]
                    itm = data[idx]
                    updated.append({
                        "statement": str(itm.get("statement", "")),
                        "proof_markdown": str(itm.get("proof_markdown", "")),
                    })

        try:
            p.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(json.dumps({"error": f"Failed to write updated JSON: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 1

        if args.json:
            print(json.dumps({"updated": len(updated), "path": str(p)}, indent=2, ensure_ascii=False))
        else:
            print(f"Refined and updated {len(updated)} entries at {p}")
        return 0

    # Continuous research loop mode
    if args.continuous:
        try:
            seeds = _parse_seed_content(question)
            run_continuous_math_research(
                seeds,
                model=args.model,
                research_guideline=args.research_guideline,
                correct_out_path=(args.correct_out_path or "correct_predicted_results.json"),
                seed_file_path=args.seed_file,
            )
        except Exception as e:
            print(json.dumps({"error": f"Continuous research failed: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 1
        return 0

    # One-shot research mode
    if args.research:
        try:
            seed_parsed = _parse_seed_content(question)
            results, report_markdown = run_automate_math_research(
                seed_result=seed_parsed,
                model=args.model,
                research_guideline=args.research_guideline,
            )
        except Exception as e:
            print(json.dumps({"error": f"Research pipeline failed: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 1
        # Save final report to file
        out_path = args.out or "research_report.md"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report_markdown)
        except Exception as e:
            print(json.dumps({"error": f"Failed to write report: {type(e).__name__}: {e}"}, ensure_ascii=False))
            return 1
        # Also print brief summary to stdout
        if args.json:
            print(json.dumps({"results": results, "report_path": out_path}, indent=2, ensure_ascii=False))
        else:
            print(f"Wrote final report to {out_path}")
            print(f"Compiled {len(results)} results with proofs.")
        return 0

    try:
        solved, payload = request_proof(question=question, model=args.model)
    except Exception as e:
        solved, payload = False, f"System error before solving: {type(e).__name__}: {e}"

    if not solved:
        # Always emit a clear header plus any available feedback/payload
        heading = "Problem is too difficult"
        if args.json:
            print(json.dumps({"error": heading, "details": payload}, indent=2, ensure_ascii=False))
        else:
            print(heading)

    markdown = payload

    if args.json:
        print(json.dumps({"markdown": markdown}, indent=2, ensure_ascii=False))
    else:
        print(markdown)

    if args.out:
        # If unsolved, still write a structured Markdown report with any feedback/details
        if not solved:
            report = f"""### Attempted proof report\n\n- **status**: failed\n- **reason**: Problem is too difficult\n\n**Details/feedback**:\n\n{payload if payload else '(no additional details)'}\n"""
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())