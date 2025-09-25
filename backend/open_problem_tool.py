from __future__ import annotations

import logging
from typing import Any, Dict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .tool_llm import generate_structured_with_tools
from .output_schemas import LiteratureReviewResult, LiteratureResultItem
from .solver import Solver
from .prompts import (
    OPEN_PROBLEM_CONTEXT_SYSTEM_PROMPT,
    build_open_problem_context_user_prompt,
)


logger = logging.getLogger("backend.open_problem_solver")

DEFAULT_TARGET_RESULTS = 25
MAX_RESULTS_CAP = 30
DEFAULT_MAX_ITERATIONS = 15


def _map_model(name: str, *, requires_tools: bool = False) -> str:
    if name == "gpt-oss-120b":
        return "o4-mini" if requires_tools else "openai/gpt-oss-120b"
    return name


def _web_search_tool() -> Dict[str, str]:
    return {"type": "web_search", "search_context_size": "high"}


def _collect_related_results(problem: str, *, model: str, target_results: int) -> LiteratureReviewResult:
    messages = [
        {"role": "system", "content": OPEN_PROBLEM_CONTEXT_SYSTEM_PROMPT},
        {"role": "user", "content": build_open_problem_context_user_prompt(problem, target_results)},
    ]
    logger.info(
        "[OpenProblemSolver] Collecting literature (model=%s, target=%d)",
        model,
        target_results,
    )
    resp = generate_structured_with_tools(
        messages=messages,
        response_model=LiteratureReviewResult,
        model=model,
        tools=[_web_search_tool()],
        tool_registry={},
        reasoning_effort="high",
        timeout=3600.0,
    )
    lit: LiteratureReviewResult = resp.output_parsed  # type: ignore[assignment]
    results = list(getattr(lit, "results", []) or [])
    problem_stmt = problem.strip()
    if problem_stmt:
        seed_item = LiteratureResultItem(statement=problem_stmt, url="problem://input")
        # Remove any existing duplicates of the problem entry
        filtered = [item for item in results if getattr(item, "url", "") != "problem://input"]
        results = [seed_item] + filtered
    if target_results > 0:
        cap = min(MAX_RESULTS_CAP, max(1, target_results))
    else:
        cap = MAX_RESULTS_CAP
    lit.results = results[:cap]
    return lit


def run_open_problem_solver(args: Dict[str, Any]) -> Dict[str, Any]:
    problem_raw = str(args.get("problem", ""))
    problem = problem_raw.strip()
    if not problem:
        return {
            "status": "error",
            "message": "Problem statement is required.",
        }

    solver_model = str(args.get("model") or "gpt-5").strip() or "gpt-5"
    search_model_input = str(args.get("search_model") or solver_model).strip() or solver_model
    search_model = _map_model(search_model_input, requires_tools=True)

    try:
        max_iterations_val = int(args.get("max_iterations", DEFAULT_MAX_ITERATIONS))
    except Exception:
        max_iterations_val = DEFAULT_MAX_ITERATIONS
    max_iterations = max(1, min(max_iterations_val, 20))

    try:
        target_results_val = int(args.get("target_results", DEFAULT_TARGET_RESULTS))
    except Exception:
        target_results_val = DEFAULT_TARGET_RESULTS
    target_results = max(20, min(target_results_val, MAX_RESULTS_CAP))

    try:
        literature = _collect_related_results(problem, model=search_model, target_results=target_results)
    except Exception as exc:  # pragma: no cover
        logger.exception("[OpenProblemSolver] Literature collection failed: %s", exc)
        return {
            "status": "error",
            "message": f"Failed to collect related results: {type(exc).__name__}: {exc}",
        }

    # Determine parallel pairs for solver runs in open-problem mode.
    # Respect DEEPRESEARCH_SOLVER_PAIRS if set; otherwise default to 3 for open-problem.
    try:
        pairs = int(os.getenv("DEEPRESEARCH_SOLVER_PAIRS", "") or "3")
    except Exception:
        pairs = 3
    pairs = max(1, pairs)

    def _run_one() -> tuple[bool, str]:
        s = Solver(model=solver_model)
        return s.solve(problem, max_iterations, literature)

    if pairs == 1:
        try:
            solved, proof_or_feedback = _run_one()
        except Exception as exc:  # pragma: no cover
            logger.exception("[OpenProblemSolver] Solver execution failed: %s", exc)
            return {
                "status": "error",
                "message": f"Solver execution failed: {type(exc).__name__}: {exc}",
            }
    else:
        results: list[tuple[bool, str]] = []
        first_success: tuple[bool, str] | None = None
        try:
            with ThreadPoolExecutor(max_workers=pairs) as ex:
                futs = [ex.submit(_run_one) for _ in range(pairs)]
                for fut in as_completed(futs):
                    try:
                        ok, payload = fut.result()
                    except Exception as exc:  # pragma: no cover
                        logger.exception("[OpenProblemSolver] Parallel solver failed: %s", exc)
                        ok, payload = False, ""
                    results.append((ok, payload))
                    if ok and first_success is None:
                        first_success = (ok, payload)
        except Exception as exc:  # pragma: no cover
            logger.exception("[OpenProblemSolver] Parallel execution failed: %s", exc)
            return {
                "status": "error",
                "message": f"Parallel execution failed: {type(exc).__name__}: {exc}",
            }
        if first_success is not None:
            solved, proof_or_feedback = first_success
        elif results:
            solved, proof_or_feedback = max(results, key=lambda x: len(x[1] or ""))
        else:
            solved, proof_or_feedback = False, "No result produced."

    related_payload = [
        {
            "statement": getattr(item, "statement", ""),
            "url": getattr(item, "url", ""),
        }
        for item in literature.results
    ]

    if solved:
        return {
            "status": "solved",
            "proof_markdown": proof_or_feedback,
            "annotations": getattr(literature, "annotations", ""),
            "related_results": related_payload,
            "model": solver_model,
            "search_model": search_model_input,
            "max_iterations": max_iterations,
        }

    result: Dict[str, Any] = {
        "status": "failed",
        "message": "Problem too difficult!",
        "annotations": getattr(literature, "annotations", ""),
        "related_results": related_payload,
        "model": solver_model,
        "search_model": search_model_input,
        "max_iterations": max_iterations,
    }
    if proof_or_feedback:
        result["feedback"] = proof_or_feedback
    return result


def build_open_problem_solver_tool_definition() -> Dict[str, Any]:
    return {
        "name": "open_problem_solver",
        "type": "function",
        "description": (
            "Tackle a challenging open math problem in two phases: first collect 20-30 supporting results via web search, "
            "then run a Prover/Judge loop with a Python sandbox (numpy and scipy available) to attempt a rigorous proof. "
            "Returns a Markdown proof when successful or 'Problem too difficult!' when no proof passes two judges."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "Problem statement in Markdown/LaTeX to attempt to prove.",
                },
                "model": {
                    "type": "string",
                    "description": "Model to use for the prover/judges (default gpt-5).",
                },
                "search_model": {
                    "type": "string",
                    "description": "Optional model override for the literature search step (defaults to the prover model).",
                },
                "max_iterations": {
                    "type": "integer",
                    "minimum": 1,
                "maximum": 20,
                "description": "Maximum prover iterations before giving up (default 15).",
                },
                "target_results": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 30,
                    "description": "Target number of related results to gather before solving (default 25).",
                },
            },
            "required": ["problem"],
            "additionalProperties": False,
        },
    }


__all__ = ["run_open_problem_solver", "build_open_problem_solver_tool_definition"]
