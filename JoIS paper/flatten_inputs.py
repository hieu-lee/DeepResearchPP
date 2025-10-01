#!/usr/bin/env python3
"""
flatten_inputs.py

Create a single-file LaTeX source by expanding all \input{...} directives
recursively. Intended for JoIS paper's main.tex but works generally.

Usage:
  # Produce main_flattened.tex next to main.tex
  python flatten_inputs.py --main main.tex

  # Overwrite main.tex in place (backup created)
  python flatten_inputs.py --main main.tex --in-place

  # Specify custom output path
  python flatten_inputs.py --main main.tex --output combined.tex

Notes:
  - Only \input{...} with braces is expanded. Other forms are left unchanged.
  - Nested inputs are expanded recursively.
  - If an input file is not found, the original \input line is kept and a
    warning comment is inserted.
  - Inserted blocks are surrounded by BEGIN/END comments for traceability.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Set


INPUT_RE = re.compile(r"\\input\s*\{([^}]+)\}")


def first_unescaped_percent(s: str) -> int:
    """Return the index of the first unescaped % in s, or -1 if none."""
    i = 0
    n = len(s)
    while i < n:
        j = s.find('%', i)
        if j == -1:
            return -1
        # count backslashes immediately before j
        bs = 0
        k = j - 1
        while k >= 0 and s[k] == '\\':
            bs += 1
            k -= 1
        if bs % 2 == 0:
            return j
        i = j + 1
    return -1


def resolve_path(base_dir: str, target: str) -> str:
    # Add .tex if missing extension
    if not os.path.splitext(target)[1]:
        target = target + ".tex"
    return os.path.abspath(os.path.join(base_dir, target))


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def flatten_file(path: str, stack: List[str], visited: Set[str], verbose: bool) -> str:
    abspath = os.path.abspath(path)
    if verbose:
        print(f"[flatten] {abspath}")
    if abspath in stack:
        return f"% WARNING: cycle detected when including {abspath}; leaving \input unchanged\n\\input{{{path}}}\n"

    base_dir = os.path.dirname(abspath)
    text = read_text(abspath)

    out_lines: List[str] = []
    for raw_line in text.splitlines(keepends=True):
        # Split at the first unescaped % to avoid processing comments
        idx = first_unescaped_percent(raw_line)
        if idx == -1:
            code_part = raw_line
            comment_part = ""
        else:
            code_part = raw_line[:idx]
            comment_part = raw_line[idx:]

        # Expand inputs in code_part
        last_end = 0
        buf: List[str] = []
        for m in INPUT_RE.finditer(code_part):
            buf.append(code_part[last_end:m.start()])
            target = m.group(1).strip()
            resolved = resolve_path(base_dir, target)
            if os.path.isfile(resolved):
                block = flatten_file(resolved, stack + [abspath], visited, verbose)
                rel = os.path.relpath(resolved, start=base_dir)
                buf.append(f"% BEGIN INPUT {rel}\n")
                buf.append(block)
                if not block.endswith("\n"):
                    buf.append("\n")
                buf.append(f"% END INPUT {rel}\n")
            else:
                # File not found; keep original directive and warn
                rel = target
                buf.append(f"% WARNING: could not find input file '{rel}'\n")
                buf.append(m.group(0))
            last_end = m.end()
        buf.append(code_part[last_end:])
        # Reattach comment part
        buf.append(comment_part)
        out_lines.append("".join(buf))

    return "".join(out_lines)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Flatten LaTeX by expanding \\input{...}")
    ap.add_argument("--main", default="main.tex", help="Path to main .tex file")
    ap.add_argument("--output", default=None, help="Output path (default: main_flattened.tex)")
    ap.add_argument("--in-place", action="store_true", help="Overwrite the main file (creates .bak)")
    ap.add_argument("--verbose", action="store_true", help="Print files as they are expanded")
    args = ap.parse_args(argv)

    main_path = os.path.abspath(args.main)
    if not os.path.isfile(main_path):
        print(f"Main file not found: {main_path}", file=sys.stderr)
        return 2

    combined = flatten_file(main_path, stack=[], visited=set(), verbose=args.verbose)

    if args.in_place:
        backup = main_path + ".bak"
        if not os.path.exists(backup):
            try:
                import shutil
                shutil.copy2(main_path, backup)
            except Exception:
                pass
        with open(main_path, "w", encoding="utf-8", newline="") as f:
            f.write(combined)
        print(f"Wrote flattened file in place: {main_path}\nBackup saved: {backup}")
        return 0

    out_path = args.output
    if out_path is None:
        base_dir, base_name = os.path.split(main_path)
        name, ext = os.path.splitext(base_name)
        out_path = os.path.join(base_dir, f"{name}_flattened{ext}")

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(combined)
    print(f"Wrote flattened file: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

