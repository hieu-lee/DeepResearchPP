from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from .cli_args import parse_args
from .cli_helpers import _parse_seed_content2
from .cli_handlers import (
    setup_provider_flags,
    handle_latex_paper,
    handle_refine_json,
    handle_open_problem,
)


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
    rc = setup_provider_flags(args)
    if rc is not None:
        return rc

    if args.open_problem and (args.research or args.continuous):
        print(
            "Error: --open-problem cannot be combined with --research or --continuous.",
            file=sys.stderr,
        )
        return 2

    # LaTeX paper conversion mode
    rc = handle_latex_paper(args)
    if rc is not None:
        return rc

    # Batch refine JSON and exit early
    rc = handle_refine_json(args)
    if rc is not None:
        return rc

    # Determine the question/seed content
    question: Optional[str] = args.question
    if args.in_file:
        try:
            in_path = Path(args.in_file)
            question = in_path.read_text(encoding="utf-8").strip()
            # Configure per-pair logging manager when an input file is provided
            try:
                from .logging_hooks import logging_manager

                logging_manager.configure_from_input_file(in_path)
                # If not explicitly configured, run three pairs in parallel for single-proof mode
                # so that logs F1, F2, F3 are produced.
                if os.getenv("DEEPRESEARCH_SOLVER_PAIRS") is None:
                    os.environ["DEEPRESEARCH_SOLVER_PAIRS"] = "3"
            except Exception:
                pass
        except Exception as e:
            print(json.dumps({"error": f"Failed to read file: {type(e).__name__}: {e}"}), file=sys.stderr)
            return 2
    if not question:
        if sys.stdin.isatty():
            print(
                "Error: no seed/question provided. Use -S/--seed-file, --in-file, or a positional question.",
                file=sys.stderr,
            )
            return 2
        # Single-shot proving mode may read from stdin interactively
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
            logger.warning(
                "GOOGLE_API_KEY not set. The request may fail unless the client is otherwise configured."
            )
    else:
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_PATH")):
            logger.warning(
                "OPENAI_API_KEY not set. The request may fail unless the client is otherwise configured."
            )

    # Open problem flow
    rc = handle_open_problem(args, question)
    if rc is not None:
        return rc

    # Continuous research loop mode
    if args.continuous:
        try:
            seeds = _parse_seed_content2(question)
            # Import via wrapper for patchability
            from . import cli as cli_mod

            cli_mod.run_continuous_math_research(
                seeds,
                model=args.model,
                research_guideline=args.research_guideline,
                correct_out_path=(args.correct_out_path or "correct_predicted_results.json"),
                seed_file_path=args.seed_file,
            )
        except Exception as e:
            print(
                json.dumps(
                    {"error": f"Continuous research failed: {type(e).__name__}: {e}"},
                    ensure_ascii=False,
                )
            )
            return 1
        return 0

    # One-shot research mode
    if args.research:
        try:
            seed_parsed = _parse_seed_content2(question)
            from . import cli as cli_mod

            results, report_markdown = cli_mod.run_automate_math_research(
                seed_result=seed_parsed,
                model=args.model,
                research_guideline=args.research_guideline,
            )
        except Exception as e:
            print(
                json.dumps(
                    {"error": f"Research pipeline failed: {type(e).__name__}: {e}"},
                    ensure_ascii=False,
                )
            )
            return 1
        # Save final report to file
        out_path = args.out or "research_report.md"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report_markdown)
        except Exception as e:
            print(
                json.dumps(
                    {"error": f"Failed to write report: {type(e).__name__}: {e}"},
                    ensure_ascii=False,
                )
            )
            return 1
        # Also print brief summary to stdout
        if args.json:
            print(
                json.dumps(
                    {"results": results, "report_path": out_path}, indent=2, ensure_ascii=False
                )
            )
        else:
            print(f"Wrote final report to {out_path}")
            print(f"Compiled {len(results)} results with proofs.")
        return 0

    # Default: single proof mode
    try:
        # Import via wrapper for patchability
        from . import cli as cli_mod

        solved, payload = cli_mod.request_proof(question=question, model=args.model)
    except Exception as e:
        solved, payload = False, f"System error before solving: {type(e).__name__}: {e}"

    if not solved:
        heading = "Problem is too difficult"
        if args.json:
            print(
                json.dumps({"error": heading, "details": payload}, indent=2, ensure_ascii=False)
            )
        else:
            print(heading)

    markdown = payload

    if args.json:
        print(json.dumps({"markdown": markdown}, indent=2, ensure_ascii=False))
    else:
        print(markdown)

    if args.out:
        if not solved:
            report = f"""### Attempted proof report\n\n- **status**: failed\n- **reason**: Problem is too difficult\n\n**Details/feedback**:\n\n{payload if payload else '(no additional details)'}\n"""
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(report)
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(markdown)

    return 0
