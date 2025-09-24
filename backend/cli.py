from .cli_args import parse_args  # re-export for compatibility
from .cli_helpers import (
    _parse_seed_content,
    _parse_seed_content2,
    _append_correct_result_json,
    _write_seed_file,
)
from .cli_research import (
    request_proof,
    run_automate_math_research,
    run_continuous_math_research,
)
from .open_problem_tool import run_open_problem_solver  # for patchability
from .result_refiner import ResultRefiner  # for patchability
from .judge import Judge  # for patchability
from .paper_converter import LatexPaperConverter, LatexPaperConverterConfig  # for patchability
from .cli_main import main

if __name__ == "__main__":
    raise SystemExit(main())
