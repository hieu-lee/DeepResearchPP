import argparse
from typing import Optional


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
        help=(
            "Run continuous research loop: iterate predictions->proofs until none can be proved; "
            "append successes to correct_predicted_results.json (configurable via --correct-out)"
        ),
    )
    parser.add_argument(
        "--open-problem",
        action="store_true",
        help=(
            "Use the Open Problem Solver: gather related results first, then run the prover/judge loop."
        ),
    )
    parser.add_argument(
        "--open-search-model",
        dest="open_search_model",
        default=None,
        help=(
            "Optional model override for the literature search phase in --open-problem mode."
        ),
    )
    parser.add_argument(
        "--open-target-results",
        dest="open_target_results",
        type=int,
        default=None,
        help="Desired number of supporting results to gather in --open-problem mode (range 20-30).",
    )
    parser.add_argument(
        "--open-max-iterations",
        dest="open_max_iterations",
        type=int,
        default=None,
        help="Maximum prover iterations before giving up in --open-problem mode (default 12).",
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
        help=(
            "Use an Ollama server (OpenAI-compatible). Sets base URL and defaults model to gpt-oss:20b if -m not provided."
        ),
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
        "--latex-paper",
        dest="latex_paper_json",
        default=None,
        help=(
            "Convert a results JSON file (array of {statement, proof_markdown}) into a LaTeX paper folder next to the JSON file."
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
        help=(
            "Path to append correct results JSON in --continuous mode (default: correct_predicted_results.json)"
        ),
    )
    return parser.parse_args(argv)

