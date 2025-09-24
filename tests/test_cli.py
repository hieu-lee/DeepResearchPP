import io
import json
import os
from pathlib import Path

import types


def test_parse_seed_content2_triple_quoted():
    import backend.cli as cli

    text = '[\n r"""A first statement""",\n r"""Second one with \\LaTeX"""\n]'
    res = cli._parse_seed_content2(text)
    assert isinstance(res, list)
    assert res == ["A first statement", "Second one with \\LaTeX"]


def test_main_plain_success(tmp_path, monkeypatch):
    import backend.cli as cli

    captured = {"called": False, "args": None}

    def fake_request_proof(question: str, model: str = "gpt-5"):
        captured["called"] = True
        captured["args"] = {"question": question, "model": model}
        return True, "OK-PROOF"

    monkeypatch.setattr(cli, "request_proof", fake_request_proof)

    # Capture stdout
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)

    rc = cli.main(["Some statement to prove", "-m", "test-model"])
    assert rc == 0
    assert captured["called"]
    assert captured["args"]["question"] == "Some statement to prove"
    assert captured["args"]["model"] == "test-model"
    assert "OK-PROOF" in out.getvalue()


def test_main_plain_failure_with_out(tmp_path, monkeypatch):
    import backend.cli as cli

    def fake_request_proof(question: str, model: str = "gpt-5"):
        return False, "detailed failure feedback"

    monkeypatch.setattr(cli, "request_proof", fake_request_proof)

    out_file = tmp_path / "report.md"
    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)

    rc = cli.main(["Q", "--out", str(out_file)])
    assert rc == 0

    text = out.getvalue()
    # Prints a heading then the payload
    assert "Problem is too difficult" in text
    assert "detailed failure feedback" in text

    # File contains a structured report
    content = out_file.read_text(encoding="utf-8")
    assert content.startswith("### Attempted proof report")
    assert "detailed failure feedback" in content


def test_open_problem_solved_text_output(monkeypatch):
    import backend.cli as cli

    def fake_open_solver(payload: dict):
        return {
            "status": "solved",
            "proof_markdown": "# proof body",
            "model": payload.get("model", "m"),
        }

    monkeypatch.setattr(cli, "run_open_problem_solver", fake_open_solver)

    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)

    rc = cli.main(["Some open problem", "--open-problem"])
    assert rc == 0
    s = out.getvalue()
    assert "=== Open Problem Solver ===" in s
    assert "Status: solved" in s
    assert "# proof body" in s


def test_ollama_flag_sets_env_and_model(monkeypatch):
    import backend.cli as cli

    # Isolate environment mutations
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    seen = {}

    def fake_request_proof(question: str, model: str = "gpt-5"):
        seen["model"] = model
        return True, "ok"

    monkeypatch.setattr(cli, "request_proof", fake_request_proof)

    rc = cli.main(["Q", "--ollama"])
    assert rc == 0
    assert os.environ.get("OPENAI_BASE_URL", "").endswith(":11434/v1")
    assert os.environ.get("OPENAI_API_KEY") == "ollama"
    assert os.environ.get("LLM_PROVIDER") == "openai"
    # Default model gets swapped to gpt-oss:20b when --ollama is used
    assert seen.get("model") == "gpt-oss:20b"


def test_refine_json_path(monkeypatch, tmp_path):
    import backend.cli as cli

    # Prepare input file with one item
    p = tmp_path / "results.json"
    p.write_text(json.dumps([
        {"statement": "S", "proof_markdown": "P"}
    ]), encoding="utf-8")

    class FakeRefiner:
        def __init__(self, model: str, reasoning_effort: str = "medium"):
            self.model = model

        def refine(self, stmt: str, proof: str):
            return (stmt + "*", proof + "*")

        def tighten(self, stmt: str, proof: str):
            # Skip tightening to avoid Judge path
            return None

    monkeypatch.setattr(cli, "ResultRefiner", FakeRefiner)
    monkeypatch.setattr(cli, "Judge", lambda model=None: types.SimpleNamespace(assess=lambda *a, **k: types.SimpleNamespace(correctness=True)))

    out = io.StringIO()
    monkeypatch.setattr("sys.stdout", out)

    rc = cli.main(["ignored", "--refine-json-result", str(p)])
    assert rc == 0

    updated = json.loads(p.read_text(encoding="utf-8"))
    assert updated and updated[0]["statement"] == "S*"
    assert updated[0]["proof_markdown"] == "P*"

