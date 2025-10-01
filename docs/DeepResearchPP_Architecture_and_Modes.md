# DeepResearchPP — System Architecture, Modes, and Achievements

This document describes the DeepResearchPP system architecture, its three operating modes (normal, research, and open-problem), and the end-to-end orchestration of models, tools, and pipelines. It is derived from the current backend implementation and CLI, notably the modules under `backend/`.

- Primary entrypoint: `backend/cli_main.py`
- Re-export hub: `backend/cli.py`
- Core pipeline modules: `backend/solver.py`, `backend/prover.py`, `backend/judge.py`, `backend/research.py`, `backend/result_refiner.py`, `backend/open_problem_tool.py`, `backend/paper_converter.py`
- LLM wiring & tools: `backend/llm_provider.py`, `backend/tool_llm.py`, `backend/code_tool.py`, `backend/markdown_tool.py`, `backend/prompts.py`
- CLI composition: `backend/cli_args.py`, `backend/cli_handlers.py`, `backend/cli_helpers.py`
- Logging hooks: `backend/logging_hooks.py`


## Overview

DeepResearchPP is a math research and proving system that:

- Produces rigorous Markdown proofs for single statements (normal mode).
- Runs a multi-phase research pipeline that predicts, proves, and reports novel results (research mode), optionally as a continuous loop until no more results can be proven (continuous mode).
- Tackles difficult open problems by first gathering 20–30 supporting results via web search and then running an iterative Prover/Judge loop (open-problem mode).

Across modes the system relies on:

- Model selection and routing via `backend/llm_provider.py` and `backend/tool_llm.py`.
- A tool ecosystem that includes a `web_search` tool and a local, sandboxed Python runner `run_python` for quick computations/sanity checks.
- Sequential judging with feedback (two LLM judges) and optional refinement/tightening of successful results.
- Optional LaTeX paper conversion from a JSON list of results into a complete project.

Default model is `gpt-5` (CLI default); flags allow Google (Gemini) or OpenAI-compatible providers (including local Ollama and Groq OSS routing) with automatic mapping where needed.


## Architecture

### CLI Entrypoint and Modes

- `backend/cli_main.py` orchestrates the CLI:
  - Parses args: `backend/cli_args.py`.
  - Configures provider flags: `backend/cli_handlers.setup_provider_flags`.
  - Routes to one of the modes:
    - Normal mode (single proof) — default.
    - Research mode — `--research` (one-shot pipeline) or `--continuous` (loop).
    - Open-problem mode — `--open-problem` (mutually exclusive with `--research`/`--continuous`).
  - Additional utilities:
    - `--latex-paper` converts a results JSON file to a LaTeX paper project.
    - `--refine-json-result` refines an existing results JSON file in batch.

- Provider flags and defaults (`backend/cli_handlers.py`):
  - `--ollama`: sets `OPENAI_BASE_URL=http://127.0.0.1:11434/v1`, default model `gpt-oss:20b`, `LLM_PROVIDER=openai`.
  - `--google`: sets `LLM_PROVIDER=google`, default model `gemini-2.5-pro`.

- Logging: If `--in-file` is used, the system configures logging so that multiple solver pairs (default 3) write per-iteration logs; see `backend/logging_hooks.py` and `DEEPRESEARCH_SOLVER_PAIRS`.


### Core Components

- Solver (`backend/solver.py`)
  - Coordinates one Prover with two sequential Judges and feedback over multiple iterations (default 10 tries; research uses 8).
  - Judges must both accept a proof for success; otherwise the first flaw’s feedback is fed back to the Prover for revision.
  - When `gpt-oss-120b` is selected, Prover runs without tools on `openai/gpt-oss-120b` and Judges use `o4-mini` (tool-capable).
  - Integrates per-pair logging via `backend/logging_hooks.py`.

- Prover (`backend/prover.py`)
  - Produces a rigorous Markdown proof from a statement; can re-prove using prior proof and judge feedback.
  - Uses Responses API structured parsing with Pydantic schema `ProofResponse` and may call tools:
    - `web_search`: for literature/context.
    - `run_python`: a local isolated Python runner for quick checks (`backend/code_tool.py`).
  - Supports literature context for more grounded proofs (annotations + allowed lemmas/URLs).

- Judges (`backend/judge.py`)
  - Judge: returns `{correctness, feedback}` where feedback is ONLY the first flaw.
  - FinalJudge: picks the least incorrect proof among several.
  - Judges can also call `run_python` via tools for small verifications.

- Research Pipeline (`backend/research.py`)
  - Literature review: gathers results and unified notation/annotations via `web_search`.
  - Prediction: proposes likely-new results (conjectures), encouraged to sanity check via `run_python` and vet novelty via `web_search`.
  - Novelty filtering: validates conjectures for novelty; optionally augments literature with matched known results.
  - Proving: attempts proofs on novel statements in parallel, each via a fresh `Solver`.
  - Reporting: compiles a KaTeX-compatible Markdown research report and validates it (no backticks/env blocks; optional KaTeX check).

- Result Refiner (`backend/result_refiner.py`)
  - `refine`: adjust statements/proofs (remove unused assumptions, correct statements if disproved, strip conjecture markers).
  - `tighten`: propose strictly tighter statements (weaker assumptions or stronger conclusions) with an adapted proof. Tightened results are optionally re-judged.

- Open Problem Solver (`backend/open_problem_tool.py`)
  - Phase 1: gather 20–30 rigorously proven supporting results via `web_search`, plus unified annotations. The open problem itself is inserted as the first entry (`url=problem://input`).
  - Phase 2: run the standard Prover/Judge loop with max iterations (default 15) to attempt a full solution. In open-problem mode, three solver pairs run in parallel by default (configurable via `DEEPRESEARCH_SOLVER_PAIRS`).

- Paper Converter (`backend/paper_converter.py`)
  - Converts a results JSON (`[{statement, proof_markdown}, ...]`) into a LaTeX paper folder adjacent to the JSON file:
    - Label assignment per result.
    - Dependency extraction (internal refs and external URLs) via `web_search`.
    - Bibliography construction from external URLs; optional related-work augmentation via `web_search`.
    - Per-result `.tex` files with theorem/proof environments and consistent references/citations.
    - `main.tex` assembly with sections, related work, consolidated macros, and `\input{...}` includes.
    - Writes a `DEBUG_PROMPT.txt` to help interactive LaTeX error triage.

- LLM Provider and Tool Layer
  - `backend/llm_provider.py`: model-agnostic structured generation:
    - OpenAI-compatible Responses API (default; supports Pydantic `parse`).
    - Google GenAI (`LLM_PROVIDER=google`): `response_schema=Pydantic`.
    - Groq: special routing for `openai/gpt-oss-120b` with JSON schema enforcement and retry loop.
  - `backend/tool_llm.py`: tool-aware loop for Responses API. Executes local function tools (`run_python`, validators) and re-parses structured outputs after tool execution.

- Tools
  - `web_search` (provided to models): fetches relevant web context (no local implementation; routed by provider).
  - `run_python` (`backend/code_tool.py`) executes untrusted Python in a subprocess with isolation, time/memory limits, truncation of large outputs.
  - `validate_markdown` (`backend/markdown_tool.py`) enforces report constraints (no backticks, balanced delimiters, optional KaTeX rendering checks via Node.js `katex`).


## Modes

### 1) Normal Mode (single proof)

- Invocation: default when neither `--research`, `--continuous`, nor `--open-problem` is set.
- Flow: `backend/cli_research.request_proof` → `Solver.solve`.
  - Optional parallelism via `DEEPRESEARCH_SOLVER_PAIRS` (>1 runs multiple, returns first success else longest feedback). When `--in-file` is used, default pairs = 3 to generate logs for F1/F2/F3.
  - Prover produces an initial proof; Judge #1 evaluates; if accepted, Judge #2 evaluates. Both must accept; otherwise feedback loops back to the Prover (reprove).
- Output: Markdown proof to stdout (and optionally to `--out`). JSON mode prints `{markdown: ...}`.

Key modules:
- `backend/cli_main.py` — normal mode dispatch and output handling.
- `backend/cli_research.py` — `request_proof` parallel runner.
- `backend/solver.py` — `Solver` feedback loop and two-judge protocol.


### 2) Research Mode (one-shot) — `--research`

End-to-end pipeline to propose, prove, and report novel results:

- Literature Review
  - Gathers unified annotations and up to ~20 related results (LaTeX + URL), placing the seed input first.
  - `ResearchPipeline.literature_review` via `web_search`.

- Prediction
  - Proposes 5–10 bold but plausible conjectures using the annotations.
  - Encouraged to verify novelty via `web_search` and perform small sanity checks via `run_python`.
  - Retry logic handles empty/invalid JSON.

- Novelty Filter
  - Runs novelty checks per conjecture (parallel) with `web_search`; keeps only genuinely novel ones.
  - For non-novel results with a matched source, appends that known result to the literature (for report context).

- Proving
  - For each novel statement, spawns an isolated `Solver` (up to 8 tries). Uses literature context to ground proofs.
  - Successful proofs are refined (`ResultRefiner.refine`) and optionally tightened (`.tighten`), with tightened proofs checked by a `Judge` before acceptance.

- Final Report
  - Compiles a KaTeX Markdown report covering literature and accepted new results.
  - Validates Markdown (balanced delimiters, no backticks/env blocks, optional KaTeX rendering checks). Up to 5 repair rounds.

- Output
  - Writes `research_report.md` by default or to `--out`. In `--json` mode, prints `{results: [...], report_path: ...}`.

Key modules:
- `backend/cli_main.py` — research-mode dispatch and file writing.
- `backend/cli_research.py` — `run_automate_math_research` orchestration.
- `backend/research.py` — pipeline steps (literature, predict, novelty_filter, compile_final_report).


### 2b) Research Mode (continuous loop) — `--continuous`

Iterates the research pipeline, appending proved results to seeds and to a durable JSON file until no more proofs succeed.

- Seeds
  - Parsed from positional/`--in-file` input via `backend/cli_helpers._parse_seed_content2`.
  - Accepts: JSON array of strings, Python-like triple-quoted items inside `[ ... ]`, or multiple blocks separated by blank lines.

- Loop
  - For iteration t = 1, 2, ...
    1. Literature review on the current seed list.
    2. Predict and novelty-filter.
    3. Attempt proofs in parallel (each via a fresh `Solver`, up to 8 tries).
    4. For each success: refine → optionally tighten + judge → pick tightened if accepted.
    5. Append `(statement, proof)` to `correct_predicted_results.json` (or `--correct-out`).
    6. Add newly proved statements into the seeds for the next iteration (deduplicated).
    7. If `--seed-file` supplied, persist the updated seed array to that file (deterministic JSON of strings).
  - Stops when there are no novel predictions or no proofs succeed in a round.

- Output
  - Durable JSON append at each success, optional seed-file updates, progress logs via standard logging.

Key modules:
- `backend/cli_main.py` — continuous-mode dispatch.
- `backend/cli_research.py` — `run_continuous_math_research` loop.
- `backend/cli_helpers.py` — seed parsing and durable JSON append helpers.


### 3) Open Problem Mode — `--open-problem`

Tackles a hard open problem by first assembling a curated toolkit of proven results, then executing the Prover/Judge loop.

- Phase 1: Curate Related Results (20–30)
  - Uses `OPEN_PROBLEM_CONTEXT_SYSTEM_PROMPT` to collect rigorously proven supporting results via `web_search`.
  - Inserts the open problem itself as the first item with `url=problem://input`.
  - Caps to ≤30 results, target default 25 (configurable via `--open-target-results`).

- Phase 2: Solve
  - Runs `Solver.solve(problem, max_iterations, literature)` with default `max_iterations=15` (override `--open-max-iterations`). By default, three solver pairs are launched in parallel to improve odds of success.
  - Judges must both accept; otherwise the first flaw is fed back for improvement in the next iteration.

- Outputs
  - On success: returns `{status: "solved", proof_markdown, annotations, related_results, ...}`.
  - On failure: `{status: "failed", message: "Problem too difficult!", feedback?, ...}`.
  - CLI prints a human-readable summary; `--out` writes the proof or a short report.

Key modules:
- `backend/cli_handlers.py` — open-problem CLI handler.
- `backend/open_problem_tool.py` — literature curation + solver orchestration.


## Providers, Models, and Routing

- Provider selection via `LLM_PROVIDER` env var or CLI flags (`--google`, `--ollama`). Defaults to OpenAI-compatible Responses API.
- Model mapping:
  - If model is `gpt-oss-120b`:
    - Prover: `openai/gpt-oss-120b` (no tools) for generation.
    - Judges/Refiner/Reporter often mapped to `o4-mini` (tool-capable) where tools are required.
  - Open Problem’s literature phase maps `gpt-oss-120b` to `o4-mini` for tool support.
- Groq routing: when model is `openai/gpt-oss-120b` and `GROQ_API_KEY` is available, `backend/llm_provider.generate_structured` uses Groq Chat Completions with JSON-schema enforcement and a resilient retry loop.
- Google GenAI: `google.genai` with `response_schema=Pydantic` used in the simplified path (no local tools loop).


## Tools and Safety

- `web_search` (model-side) for literature discovery and novelty checks (context size often `medium`, occasionally `high`).
- `run_python` (`backend/code_tool.py`) executes untrusted snippets:
  - Isolated `python -I` subprocess.
  - Timeouts (default ~10s) and POSIX resource limits (virtual memory cap, CPU time), large output truncation.
- `validate_markdown` enforces report constraints (no backticks, balanced delimiters, optional KaTeX rendering checks via Node.js `katex`).


## Observability and Logging

- Logging level controlled by CLI (`--quiet` lowers to ERROR else INFO) with timestamps to stderr.
- Per-pair logs (if `--in-file` provided): `backend/logging_hooks.py` writes a main log and per-iteration logs `IterationN.log` inside `<input_stem>_<pair>_log/` folders.
- Environment variable `DEEPRESEARCH_SOLVER_PAIRS` controls the number of concurrent solver pairs for normal and open-problem modes; default is 3 for open-problem, and also 3 when `--in-file` is used in normal mode.


## LaTeX Paper Conversion (optional)

- Triggered via `--latex-paper <results.json>`:
  1) Parse results JSON as `[{statement, proof_markdown}, ...]`.
  2) Assign stable labels per result.
  3) Extract dependencies (internal labels and external URLs) via `web_search`.
  4) Build `bib.tex` from external URLs; optionally extend with related work.
  5) Write per-result `*.tex` files (theorem + proof, with references/citations).
  6) Assemble `main.tex` with sections, narrative, consolidated macros, related work, and `\input{...}` includes.
  7) Provide a debugging prompt via clipboard and `DEBUG_PROMPT.txt`.

Outputs a folder beside the JSON (same stem) containing `main.tex`, result files, and `bib.tex`.


## CLI Summary

Common flags (see `backend/cli_args.py`):
- `--model/-m`: model name (default `gpt-5`).
- `--research`: run one-shot research pipeline.
- `--continuous`: run continuous research loop (append successes to JSON and seeds).
- `--open-problem`: run open-problem solver (cannot combine with research/continuous).
- `--open-search-model`: override search model in open-problem mode.
- `--open-target-results`: 20–30 supporting results (default 25).
- `--open-max-iterations`: max prover iterations (default 15).
- `--in-file/-f`: read the statement/seed(s) from a file; configures per-pair logging and parallel pairs.
- `--out/-o`: write output markdown or report path.
- `--json`: JSON output mode.
- `--refine-json-result`: batch refine a results JSON file.
- `--latex-paper`: convert a results JSON to a LaTeX paper project.
- `--ollama` / `--google`: provider routing flags.


## Achievements (using GPT‑5)

The DeepResearchPP system, configured with `gpt-5` as the primary model, has accomplished the following:

- Solved 5 of 6 problems at IMO 2025.
- Scored 40/42 on USAMO 2025.
- Solved 8 open problems in number theory.
- Produced multiple new research results in convex optimization, number theory, and machine learning leading to the following papers:
  - https://arxiv.org/pdf/2509.04883
  - https://arxiv.org/pdf/2509.08954


## Notes on Robustness and Error Handling

- Structured outputs use Pydantic schemas; parsing is enforced by OpenAI Responses API (`parse`) or Google GenAI `response_schema`, with fallbacks and repair prompts.
- Groq path includes a retry loop and schema re-instruction if parsing fails.
- Research prediction step tolerates transient empty outputs by retrying and, if necessary, proceeding with no predictions.
- Paper generation deduplicates labels, sanitizes filenames, de-duplicates macros, and validates URLs.
- JSON append and seed-file updates are durable and defensive against partial/corrupt files.


## File Map (key modules)

- CLI and handlers
  - `backend/cli_main.py` — main CLI dispatcher and mode routing
  - `backend/cli_args.py` — argument parsing
  - `backend/cli_handlers.py` — provider flags, open-problem/refine/paper handlers
  - `backend/cli_helpers.py` — seed parsing and durable JSON append

- Proving core
  - `backend/solver.py` — Prover + Judges feedback loop
  - `backend/prover.py` — proof generation and reproving
  - `backend/judge.py` — judging and final-judge selection

- Research pipeline
  - `backend/research.py` — literature → prediction → novelty → report
  - `backend/result_refiner.py` — refine and tighten proved results
  - `backend/open_problem_tool.py` — curated context + solver for open problems

- Paper conversion
  - `backend/paper_converter.py` — labels, dependencies, bib, per-result TeX, main.tex

- LLM and tools
  - `backend/llm_provider.py` — provider-agnostic structured generation
  - `backend/tool_llm.py` — tool-aware loop and local tool execution
  - `backend/code_tool.py` — isolated Python execution tool
  - `backend/markdown_tool.py` — Markdown/KaTeX validator
  - `backend/prompts.py` — all system/user prompt templates

- Logging
  - `backend/logging_hooks.py` — per-pair solver/prover detailed logs
