import re
from pathlib import Path


def _decode_content(raw: str) -> str:
    # Normalize common escaped newlines first (Windows CRLF and LF)
    raw = raw.replace("\\r\\n", "\n").replace("\\n", "\n")
    # Reduce quadruple/single backslashes into a single backslash for LaTeX readability
    raw = raw.replace("\\\\", "\\")
    # Unescape quotes if present
    raw = raw.replace('\\"', '"')
    return raw


def main():
    base = Path(__file__).resolve().parent
    src = base / "list.txt"
    text = src.read_text(encoding="utf-8")

    # Extract all raw triple-quoted blocks r"""..."""
    blocks = re.findall(r"r?\"\"\"(.*?)\"\"\"", text, flags=re.S | re.I)

    if not blocks:
        raise SystemExit("No conjecture entries found in list.txt")

    # Decode escape sequences for readability and write to files
    for i, block in enumerate(blocks, start=1):
        content = _decode_content(block)
        (base / f"conj{i}.txt").write_text(content, encoding="utf-8")

    print(f"Extracted {len(blocks)} conjectures to {base}")


if __name__ == "__main__":
    main()
