from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional


def setup_provider_flags(args) -> Optional[int]:
    """Apply provider-specific environment and defaults.

    Returns a nonzero exit code on invalid combinations.
    """
    if args.ollama and args.google:
        print("Error: --ollama and --google are mutually exclusive.", file=sys.stderr)
        return 2

    if args.ollama:
        if not os.getenv("OPENAI_BASE_URL"):
            os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:11434/v1"
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_PATH")):
            os.environ["OPENAI_API_KEY"] = "ollama"
        if args.model == "gpt-5":
            args.model = "gpt-oss:20b"
        os.environ["LLM_PROVIDER"] = "openai"
    elif args.google:
        if args.model == "gpt-5":
            args.model = "gemini-2.5-pro"
        os.environ["LLM_PROVIDER"] = "google"
    return None


def handle_latex_paper(args) -> Optional[int]:
    if not args.latex_paper_json:
        return None
    try:
        # Import via wrapper for easier patching
        from . import cli as cli_mod

        converter = cli_mod.LatexPaperConverter(
            cli_mod.LatexPaperConverterConfig(
                label_model="gpt-5-mini",
                label_reasoning="medium",
                dependency_model=args.model,
                dependency_reasoning="medium",
                bib_model="gpt-5-mini",
                bib_reasoning="medium",
                result_model=args.model,
                result_reasoning="medium",
                main_model=args.model,
                main_reasoning="medium",
            )
        )
        output_dir = converter.convert(args.latex_paper_json)
    except Exception as e:
        payload = {"error": f"LaTeX paper conversion failed: {type(e).__name__}: {e}"}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(payload["error"], file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"output_dir": str(output_dir)}, ensure_ascii=False, indent=2))
    else:
        print(f"LaTeX paper written to {output_dir}")
    return 0


def handle_refine_json(args) -> Optional[int]:
    if not args.refine_json_path:
        return None
    try:
        p = Path(args.refine_json_path).expanduser().resolve()
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else []
        if not isinstance(data, list):
            raise ValueError("JSON root must be a list")
    except Exception as e:
        print(
            json.dumps(
                {"error": f"Failed to read results JSON: {type(e).__name__}: {e}"},
                ensure_ascii=False,
            )
        )
        return 2

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from . import cli as cli_mod

    refiner = cli_mod.ResultRefiner(model=args.model, reasoning_effort="medium")

    def _refine_item(item: dict) -> dict:
        stmt = str(item.get("statement", ""))
        proof = str(item.get("proof_markdown", ""))
        if not stmt or not proof:
            return item
        try:
            res = refiner.refine(stmt, proof)
            if res is not None:
                base_stmt, base_proof = res
            else:
                base_stmt, base_proof = stmt, proof
            tightened = refiner.tighten(base_stmt, base_proof)
            if tightened is not None:
                t_stmt, t_proof = tightened
                j = cli_mod.Judge(model=args.model)
                jres = j.assess(t_stmt, t_proof)
                if jres.correctness:
                    return {"statement": t_stmt, "proof_markdown": t_proof}
            return {"statement": base_stmt, "proof_markdown": base_proof}
        except Exception:
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
                updated.append(
                    {
                        "statement": str(itm.get("statement", "")),
                        "proof_markdown": str(itm.get("proof_markdown", "")),
                    }
                )

    try:
        p.write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(
            json.dumps(
                {"error": f"Failed to write updated JSON: {type(e).__name__}: {e}"},
                ensure_ascii=False,
            )
        )
        return 1

    if args.json:
        print(json.dumps({"updated": len(updated), "path": str(p)}, indent=2, ensure_ascii=False))
    else:
        print(f"Refined and updated {len(updated)} entries at {p}")
    return 0


def handle_open_problem(args, question: str) -> Optional[int]:
    if not args.open_problem:
        return None
    payload = {"problem": question, "model": args.model}
    if args.open_search_model:
        payload["search_model"] = args.open_search_model
    if args.open_max_iterations is not None:
        payload["max_iterations"] = args.open_max_iterations
    if args.open_target_results is not None:
        payload["target_results"] = args.open_target_results
    from . import cli as cli_mod

    result = cli_mod.run_open_problem_solver(payload)
    status = str(result.get("status") or "").lower()
    if status == "error":
        message = result.get("message") or "Open Problem Solver encountered an error."
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Open Problem Solver failed: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== Open Problem Solver ===")
        print(f"Status: {status or 'unknown'}")
        model_name = result.get("model")
        if model_name:
            print(f"Model: {model_name}")
        search_model = result.get("search_model")
        if search_model and search_model != model_name:
            print(f"Search model: {search_model}")
        iterations = result.get("max_iterations")
        if iterations is not None:
            print(f"Max iterations: {iterations}")
        annotations = (result.get("annotations") or "").strip()
        if annotations:
            print("\nAnnotations:\n" + annotations)
        related = result.get("related_results") or []
        if related:
            print(f"\nRelated results ({len(related)}):")
            for item in related:
                stmt = (item.get("statement") or "").strip()
                url = (item.get("url") or "").strip()
                if url:
                    print(f"- {stmt} [{url}]")
                else:
                    print(f"- {stmt}")
        if status == "solved":
            proof = result.get("proof_markdown") or ""
            if proof:
                print("\nProof:\n")
                print(proof)
        else:
            message = result.get("message")
            if message:
                print(f"\n{message}")
            feedback = result.get("feedback")
            if feedback:
                print("\nFeedback:\n" + feedback)
    if args.out:
        try:
            output_path = Path(args.out).expanduser().resolve()
            if status == "solved":
                output_path.write_text(result.get("proof_markdown") or "", encoding="utf-8")
            else:
                lines = ["### Open Problem Solver Report", "", f"- **status**: {status}"]
                message = result.get("message")
                if message:
                    lines.append(f"- **message**: {message}")
                feedback = result.get("feedback")
                if feedback:
                    lines.extend(["", "Feedback:", feedback])
                output_path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            err_msg = f"Failed to write output: {type(e).__name__}: {e}"
            if args.json:
                print(json.dumps({"error": err_msg}, ensure_ascii=False), file=sys.stderr)
            else:
                print(err_msg, file=sys.stderr)
            return 1
    return 0
