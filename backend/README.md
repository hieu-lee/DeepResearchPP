### Math Proving System (IMO/USAMO)

A small, scriptable pipeline that asks an LLM to produce rigorous Markdown proofs for olympiad-style problems, judges the result, and iterates. Includes helpers for batch-running the 2025 IMO/USAMO problem sets.

### Highlights
- **CLI-first**: `cli.py` takes a statement or `-f file.txt` and prints a Markdown proof (or JSON with `--json`).
- **Feedback loop**: multiple provers run in parallel; a judge provides flaw-focused feedback; the system retries.
- **Geometry policy**: Euclidean geometry problems must be solved via an exclusively complex-number method.

### Reported Results (your mileage may vary)
- **IMO 2025**: GPT-5 scored 35/42 (gold medal level); GPT-5 mini scored 28/42 (silver medal level).
- **USAMO 2025**: GPT-5 scored 35/42; GPT-5 mini scored 40/42.

These numbers depend on prompts, randomness, model updates, and judging strictness. Treat them as indicative, not definitive.

### Quickstart
1) Create env and install deps
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
2) Set your OpenAI credentials (either works)
```bash
export OPENAI_API_KEY="sk-..."
# or
export OPENAI_API_KEY_PATH="$HOME/.openai/key.txt"
```
3) Run the CLI
```bash
# From a file
python cli.py -f imo2025_p1.txt

# From stdin
cat usamo2025_p2.txt | python cli.py

# Choose a model and write to a file
python cli.py -f usamo2025_p3.txt -m gpt-5 -o p3.md

# JSON output (stdout)
python cli.py -f imo2025_p4.txt --json
```

### Research mode with guideline steering
- Enable research mode to run the literature review → prediction → novelty filter → proof → report pipeline.
- Use `--research-guideline` to steer predictions toward a target research direction (optional).

```bash
# Minimal research run (seed result is read from the file)
python cli.py --research -S seed.txt -m gpt-5

# Steer predictions toward a goal (e.g., Riemann hypothesis or LLM efficiency)
python cli.py --research -S seed.txt --research-guideline "solve Riemann hypothesis"
python cli.py --research -S seed.txt --research-guideline "improve post-training efficiency for LLMs"
```

When a guideline is provided, the prediction stage prioritizes conjectures that concretely advance that goal, while still leveraging the trusted results from the literature review and enforcing novelty checks.

### Using Ollama (OpenAI-compatible Responses API)
- Start Ollama locally and pull a model that supports the OpenAI-compatible API.
- Run with the `--ollama` flag. This sets `OPENAI_BASE_URL` and defaults `-m` to `gpt-oss:20b` if you didn't provide one.
```bash
# Example: use local Ollama with default gpt-oss:20b
python cli.py --ollama -f imo2025_p1.txt

# Or specify a different local model
python cli.py --ollama -m llama3.1:70b -f usamo2025_p2.txt

# You can also set envs yourself instead of --ollama
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"  # placeholder, required by SDK
python cli.py -m gpt-oss:20b -f imo2025_p3.txt
```

### Using Google Generative AI (Gemini)
- Set `GOOGLE_API_KEY` (or configure `google-genai` auth as needed).
- Use the `--google` flag. If you don't specify `-m`, the system defaults to `gemini-2.5-pro`.
```bash
export GOOGLE_API_KEY="..."

# Default model (gemini-2.5-pro)
python cli.py --google -f usamo2025_p4.txt

# Specify a different Gemini model
python cli.py --google -m gemini-2.5-flash -f imo2025_p2.txt
```

Notes:
- The pipeline uses a provider-agnostic wrapper. For Google, it calls `google-genai` with `response_schema` bound to our Pydantic models for structured outputs.
- For OpenAI/Ollama, it uses the OpenAI Responses API with `responses.parse` to the same schemas.

### Batch runner and verification helpers
- `solve_imo.sh` runs five problems concurrently using the CLI and writes `p1.md` … `p5.md`. Note: it currently targets the `usamo2025_p{i}.txt` files by default.
- `verify_prompt.sh i` (macOS) copies a nicely formatted “problem + proof” block for problem `i` to the clipboard, expecting `usamo2025_p{i}.txt` and `p{i}.md` to exist. Requires `pbcopy`.

### Models and behavior (defaults)
- `Prover` (proof generation): defaults to `gpt-5-mini` with high reasoning effort.
- `Judge` (checks a single proof): defaults to `gpt-5-mini` with high reasoning effort.
- `FinalJudge` (selects among attempts): defaults to `gpt-5` with medium reasoning effort.
- `GeometryClassifier` (detects Euclidean plane geometry): defaults to `gpt-5-mini` with medium reasoning effort.
- CLI default model is `gpt-5` (`-m` overrides).

For detected Euclidean geometry, the solver enforces a complex-number solution (complex plane setup, optional Möbius normalization, algebraic justification via complex identities). Non-complex geometry approaches are rejected.

### File overview
- `cli.py`: command-line interface and I/O; supports `-f/--in-file`, `-m/--model`, `--json`, `-o/--out`.
- `solver.py`: orchestrates multiple `Prover`s in parallel with retries and judging; enforces complex-geometry policy.
- `prover.py`: calls the OpenAI Responses API with structured output (`ProofResponse`).
- `judge.py`: structured assessment (`JudgeResponse`) and final selection (`FinalJudgeResponse`).
- `classifier.py`: Euclidean geometry detector.
- `prompts.py`: prompt templates and builders.
- `output_schemas.py`: Pydantic schemas for structured responses.
- `imo2025_p*.txt`, `usamo2025_p*.txt`: problem statements.
- `solve_imo.sh`: example batch runner (currently wired to USAMO files).
- `verify_prompt.sh`: macOS clipboard helper for human verification.

### Requirements
Listed in `requirements.txt`:
- `openai>=1.40.0`
- `pydantic>=2.8.0`
- `pypandoc-binary>=1.12`

Python 3.9+ is recommended. macOS/Linux tested; Windows should work via WSL or PowerShell equivalents (clipboard helper is macOS-only).

### Notes on reproducibility
- LLM outputs are stochastic and model backends evolve; expect variance run-to-run.
- Network timeouts are retried a few times; see timeouts/retry parameters in `prover.py` and `judge.py`.
- If no proof is fully correct, the system returns the best attempt with the first detected flaw for debugging.


