import json
import re
from pathlib import Path


def _parse_seed_content(text: str) -> str | list[str]:
    '''Parse seed content as JSON list[str] if possible; otherwise return the raw string.

    Accepts either a single statement string or a JSON array of statement strings.
    '''
    try:
        import json as _json

        val = _json.loads(text)
        if isinstance(val, list) and all(isinstance(x, str) for x in val):
            return val
        if isinstance(val, str):
            return val
        # Fallback to raw text if not list[str] or string
        return text
    except Exception:
        # Heuristic 1: bracketed list of quoted items with unescaped LaTeX backslashes
        stripped = text.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            # Extract all top-level double-quoted segments without interpreting escapes
            # This tolerates LaTeX like \mathrm without requiring JSON escapes
            items = re.findall(r'"([^\"]*)"', stripped, flags=re.S)
            items = [s.strip() for s in items if s and s.strip()]
            if items:
                return items
        # Heuristic 2: blank-line delimited multiple seeds
        blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
        if len(blocks) > 1:
            return blocks
        return text


def _parse_seed_content2(text: str) -> str | list[str]:
    '''Enhanced parser for seed content supporting triple-quoted lists.

    Tries JSON; then r\"\"\"...\"\"\" items inside [...]; then \"...\" items; then blank-line blocks; else raw text.
    '''
    try:
        import json as _json
        val = _json.loads(text)
        if isinstance(val, list) and all(isinstance(x, str) for x in val):
            return val
        if isinstance(val, str):
            return val
        return text
    except Exception:
        stripped = text.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            items3 = re.findall(r'r?"""(.*?)"""', stripped, flags=re.S | re.I)
            items3 = [s.strip() for s in items3 if s and s.strip()]
            if items3:
                return items3
            items = re.findall(r'"([^\\"]*)"', stripped, flags=re.S)
            items = [s.strip() for s in items if s and s.strip()]
            if items:
                return items
        blocks = [b.strip() for b in re.split(r"\n\s*\n+", text) if b.strip()]
        if len(blocks) > 1:
            return blocks
        return text


def _append_correct_result_json(path: str, statement: str, proof_markdown: str) -> None:
    '''Append a correct result to a JSON array file in a durable way.

    If the file does not exist or is invalid, create it with a single-element array.
    '''
    obj = {"statement": statement, "proof_markdown": proof_markdown}
    try:
        p = Path(path).expanduser().resolve()
        if p.exists():
            try:
                raw = p.read_text(encoding="utf-8")
                data = json.loads(raw) if raw.strip() else []
                if not isinstance(data, list):
                    data = []
            except Exception:
                data = []
        else:
            data = []
        data.append(obj)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        # Best-effort fallback: write a minimal JSON array
        try:
            Path(path).write_text(json.dumps([obj], indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


def _write_seed_file(path: Path, seeds: list[str]) -> None:
    '''Write seeds to file deterministically as a JSON array of strings.

    If the directory does not exist, attempt to create it. Best-effort; errors are swallowed.
    '''
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Maintain stable ordering for reproducibility
        unique = list(dict.fromkeys(seeds))
        path.write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
