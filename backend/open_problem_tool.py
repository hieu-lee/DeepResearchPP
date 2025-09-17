from __future__ import annotations

import logging
from typing import Any, Dict

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
DEFAULT_MAX_ITERATIONS = 12


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

    solver = Solver(model=solver_model)
    try:
        solved, proof_or_feedback = solver.solve(problem, max_iterations, literature)
    except Exception as exc:  # pragma: no cover
        logger.exception("[OpenProblemSolver] Solver execution failed: %s", exc)
        return {
            "status": "error",
            "message": f"Solver execution failed: {type(exc).__name__}: {exc}",
        }

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
                    "description": "Maximum prover iterations before giving up (default 12).",
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
