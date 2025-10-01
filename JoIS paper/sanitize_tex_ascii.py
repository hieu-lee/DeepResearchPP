#!/usr/bin/env python3
"""
sanitize_tex_ascii.py

Scan .tex files for non-ASCII characters and optionally fix them by
replacing with ASCII equivalents. Designed for the JoIS paper folder.

Usage examples:
  - Report only (non-zero exit code if issues found):
      python sanitize_tex_ascii.py --path .
  - Fix in place with backups (*.bak):
      python sanitize_tex_ascii.py --path . --fix

Notes:
  - Replacements include typographic quotes, dashes, ellipsis, and common
    whitespace characters. Accented letters are transliterated via
    Unicode normalization (NFKD) with combining marks removed.
  - Files are processed recursively under the given path.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import unicodedata as ud
from typing import Dict, Iterable, List, Tuple


COMMON_MAP: Dict[str, str] = {
    # Quotes
    "\u2018": "'",  # ‘
    "\u2019": "'",  # ’
    "\u201A": ",",  # ‚
    "\u201C": '"',  # “
    "\u201D": '"',  # ”
    "\u201E": '"',  # „
    # Dashes / hyphens / minus
    "\u2010": "-",  # Hyphen
    "\u2011": "-",  # Non-breaking hyphen
    "\u2012": "-",  # Figure dash
    "\u2013": "-",  # En dash
    "\u2014": "--", # Em dash -> two hyphens
    "\u2212": "-",  # Minus sign
    # Ellipsis
    "\u2026": "...",
    # Spaces / non-breaking spaces
    "\u00A0": " ",  # NBSP
    "\u2007": " ",  # Figure space
    "\u2009": " ",  # Thin space
    "\u202F": " ",  # Narrow no-break space
    # Bullets and similar
    "\u2022": "*",   # Bullet
    "\u30FB": "*",   # Katakana middle dot (fallback)
    # Misc punctuation
    "\u00AB": '"',   # «
    "\u00BB": '"',   # »
    "\u2032": "'",  # ′ prime
    "\u2033": '"',   # ″ double prime
}


def ascii_compatible(s: str) -> bool:
    return all(ord(ch) < 128 for ch in s)


def find_non_ascii_lines(text: str) -> List[Tuple[int, List[Tuple[int, str]]]]:
    """Return a list of (line_no, [(col_no, char), ...]) for non-ASCII.
    line_no and col_no are 1-based.
    """
    out: List[Tuple[int, List[Tuple[int, str]]]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        hits: List[Tuple[int, str]] = []
        for j, ch in enumerate(line, start=1):
            if ord(ch) >= 128:
                hits.append((j, ch))
        if hits:
            out.append((i, hits))
    return out


def apply_common_map(text: str) -> str:
    if not text:
        return text
    # Build translation via regex for performance
    pattern = re.compile("|".join(map(re.escape, COMMON_MAP.keys())))
    return pattern.sub(lambda m: COMMON_MAP[m.group(0)], text)


def strip_combining_marks(text: str) -> str:
    return "".join(ch for ch in text if ud.category(ch) != "Mn")


def sanitize_text(text: str) -> str:
    # 1) Normalize common punctuation and spaces first
    t = apply_common_map(text)
    # 2) NFKD decompose accented chars
    t = ud.normalize("NFKD", t)
    # 3) Drop combining marks to get ASCII-friendly forms
    t = strip_combining_marks(t)
    # 4) As a last resort, drop any remaining non-ASCII bytes
    t = t.encode("ascii", errors="ignore").decode("ascii")
    # 5) Normalize line endings to preserve original style (leave as-is)
    return t


def process_file(path: str, fix: bool, backup: bool) -> Tuple[bool, int]:
    """Process a single file.
    Returns (had_non_ascii_before, num_replacements_made)
    """
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    non_ascii = find_non_ascii_lines(text)
    had_non_ascii = bool(non_ascii)
    replacements = 0

    if had_non_ascii:
        rel = os.path.relpath(path)
        print(f"\n[Non-ASCII] {rel}")
        for ln, cols in non_ascii:
            marks = ", ".join(f"col {c} U+{ord(ch):04X} '{ch}'" for c, ch in cols)
            print(f"  line {ln}: {marks}")

        if fix:
            new_text = sanitize_text(text)
            if new_text != text:
                if backup:
                    shutil.copy2(path, path + ".bak")
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new_text)
                # crude estimate: count of removed/replaced chars
                replacements = sum(1 for ch in text if ord(ch) >= 128)
                print(f"  -> fixed ({replacements} chars affected)")
            else:
                print("  -> nothing to change after normalization")

    return had_non_ascii, replacements


def iter_tex_files(root: str, exts: Iterable[str]) -> Iterable[str]:
    exts = tuple(exts)
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(exts):
                yield os.path.join(dirpath, fn)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Detect and fix non-ASCII in .tex files")
    ap.add_argument("--path", default=".", help="Root folder to scan (default: .)")
    ap.add_argument("--fix", action="store_true", help="Write sanitized files in place")
    ap.add_argument("--no-backup", action="store_true", help="Do not create .bak backups when fixing")
    ap.add_argument(
        "--extensions",
        nargs="*",
        default=[".tex"],
        help="File extensions to include (default: .tex)",
    )

    args = ap.parse_args(argv)
    root = os.path.abspath(args.path)
    backup = not args.no_backup

    print(f"Scanning: {root}")
    had_any = False
    total_replaced = 0
    files = sorted(iter_tex_files(root, args.extensions))
    if not files:
        print("No files found matching extensions.")
        return 0

    for path in files:
        had, rep = process_file(path, fix=args.fix, backup=backup)
        had_any |= had
        total_replaced += rep

    if had_any and not args.fix:
        print("\nNon-ASCII characters found. Rerun with --fix to sanitize.")
        return 1

    if args.fix:
        print(f"\nSanitization complete. Total non-ASCII chars affected: {total_replaced}.")
    else:
        print("\nNo non-ASCII characters detected." if not had_any else "")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

