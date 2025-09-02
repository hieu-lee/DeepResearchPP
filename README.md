# DeepResearch++

```
⚠️ This project, DeepResearch++, is source-available only.
Viewing is allowed, but usage, modification, or distribution is prohibited.
```

An open, reproducible research-and-proving agent for mathematics. DeepResearch++ uses strong open models (e.g., GPT‑OSS‑120B) and provider‑agnostic calls to generate conjectures, attempt rigorous Markdown proofs, critique flaws, and iterate—aiming to accelerate mathematical discovery and, ultimately, scientific research.

## Key capabilities
- **Review → Conjecture generation**: builds candidate conjectures from seeds and recent results.
- **Novelty filter**: down‑selects to likely‑new ideas to avoid re‑discoveries.
- **Proof engine**: parallel provers generate proofs; a judge critiques; the system refines and selects the best attempt.
- **Geometry policy**: Euclidean geometry must use the complex‑plane method for robustness and verifiability.
- **Reproducible outputs**: Markdown report with statement, status, proof, and failure analysis.
- **Interfaces**: CLI‑first with a minimal web UI; runs with OpenAI‑compatible endpoints (local or hosted).

## Architecture (high level)
- **Backend (Python)**
  - `backend/cli.py`: CLI interface (file/stdin, JSON, output file).
  - `backend/solver.py`: orchestrates multiple provers, judging, retries, and final selection.
  - `backend/prover.py` and `backend/judge.py`: model calls with structured outputs via Pydantic schemas.
  - `backend/research.py`: literature review → prediction → novelty filter → proof → report.
  - `backend/classifier.py`: geometry classifier that enforces complex‑number solutions for Euclidean problems.
  - `backend/llm_provider.py`: provider‑agnostic wrapper for OpenAI‑compatible APIs and Google Generative AI.
- **Web (Vite/React)**: lightweight UI in `web/` for chatting and running experiments against the backend API.

## Quickstart (CLI)

Prereqs: Python 3.9+, macOS/Linux recommended.

```bash
# Create a virtual env and install deps
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Set credentials (choose one provider). For OpenAI-compatible:
export OPENAI_API_KEY="sk-..."

# Run on a problem file
python cli.py -f usamo2025_p2.txt

# JSON output
python cli.py -f imo2025_p4.txt --json

# Choose a model and write to a file
python cli.py -f usamo2025_p3.txt -m gpt-5 -o p3.md
```

### Research mode
```bash
# Minimal research loop from a seed result
python cli.py --research -S seeds/seed_reasoning.txt -m gpt-5

# Steer predictions toward a target direction
python cli.py --research -S seeds/seed_number_theory.txt \
  --research-guideline "prime gaps in short intervals"
```

### Using local open models via Ollama
```bash
# Start Ollama separately, then:
export OPENAI_BASE_URL="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="ollama"   # placeholder required by SDK
python cli.py --ollama -f usamo2025_p2.txt             # defaults to gpt-oss:20b
python cli.py --ollama -m llama3.1:70b -f imo2025_p3.txt
```

### Using Google Generative AI (Gemini)
```bash
export GOOGLE_API_KEY="..."
python cli.py --google -f usamo2025_p4.txt             # defaults to gemini-2.5-pro
python cli.py --google -m gemini-2.5-flash -f imo2025_p2.txt
```

## Web UI (optional)
```bash
cd web
npm install
npm run dev
```

## Repository structure
```
backend/               # CLI, solver, provers/judges, research loop, schemas
web/                   # Vite/React UI
research_report.md     # Example output/report
```

## Legal status
- See `LICENSE`. This repository is **source‑available** for viewing only. No usage, modification, or distribution is permitted without prior written permission.
- Contact: `hieuld1009@gmail.com`.

## Notes on reproducibility
- LLM outputs are stochastic and providers evolve; expect run‑to‑run variance.
- If no complete proof is found, the system returns the best attempt with the first detected flaw to aid debugging.
