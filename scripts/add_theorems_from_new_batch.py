#!/usr/bin/env python3
''' 
Convert each pair of conjecture files in new batch (conjX.txt + conjX.md)
into a LaTeX theorem file in JoIS paper/theorems following the style of
existing theorems. Ensures ASCII-only output (recommend to run the provided
sanitizer afterwards).

Heuristics:
- Extract the conjecture number and title from the first line matching
  "\\textbf{Conjecture N (Title).}" in conjX.txt and treat the remaining
  lines as the statement.
- Determine resolves vs disproves by scanning the proof markdown for keywords:
  any of {"false", "disprove", "counterexample"} implies "disproves", else
  default to "resolves".
- Generate a file name and label slug from the title. If a file already exists
  for that slug, append a numeric suffix.
- For proofs: if the markdown contains a LaTeX proof environment already
  ("\\begin{proof}"), include it verbatim; otherwise wrap the cleaned content
  in a LaTeX proof environment. Remove leading "Claim." and "Proof." markers.

Usage:
  python scripts/add_theorems_from_new_batch.py

This script writes files into JoIS paper/theorems.
'''

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
NEW_BATCH = ROOT / 'new batch'
THEOREMS_DIR = ROOT / 'JoIS paper' / 'theorems'


RE_CONJ_HEADER = re.compile(
    r'^\s*\*?\s*\\textbf\{\s*Conjecture\s+(?P<num>\d+)\s*\((?P<title>[^}]+)\)\.?\}\s*$',
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def find_conjecture_header_and_statement(txt: str) -> Tuple[Optional[int], Optional[str], str]:
    '''Return (conj_number, title, statement_text). Statement is everything
    after the header line with minimal trimming.'''
    lines = txt.splitlines()
    conj_no: Optional[int] = None
    title: Optional[str] = None
    stmt_lines: list[str] = []
    found = False
    for i, line in enumerate(lines):
        m = RE_CONJ_HEADER.match(line)
        if m:
            conj_no = int(m.group('num'))
            title = m.group('title').strip()
            stmt_lines = lines[i + 1:]
            found = True
            break
    if not found:
        for i, line in enumerate(lines):
            m2 = re.search(r'Conjecture\s+(\d+)\s*\(([^\)]+)\)', line, flags=re.IGNORECASE)
            if m2:
                conj_no = int(m2.group(1))
                title = m2.group(2).strip()
                stmt_lines = lines[i + 1:]
                found = True
                break
    while stmt_lines and not stmt_lines[0].strip():
        stmt_lines.pop(0)
    while stmt_lines and not stmt_lines[-1].strip():
        stmt_lines.pop()
    statement = '\n'.join(stmt_lines)
    return conj_no, title, statement


def infer_resolution_kind(md: str) -> str:
    s = md.lower()
    if any(kw in s for kw in [' is false', 'disprove', 'counterexample', 'contradicting', 'contradiction']):
        return 'disproves'
    return 'resolves'


def slugify_title(title: str) -> str:
    title = title.lower()
    title = title.replace('analog for ', '').replace('analog', '')
    title = re.sub(r'[^a-z0-9]+', '_', title)
    title = re.sub(r'_+', '_', title).strip('_')
    return title or 'conjecture'


def choose_unique_filename(base_slug: str) -> tuple[str, str]:
    slug = base_slug
    k = 1
    while True:
        fname = f'thm_{slug}.tex'
        fpath = THEOREMS_DIR / fname
        if not fpath.exists():
            return fname, slug
        k += 1
        slug = f'{base_slug}_{k}'


RE_STRIP_CLAIM = re.compile(r'^\s*\*\*?\s*claim[^\n]*\n\s*', re.IGNORECASE)
RE_STRIP_PROOF_HDR = re.compile(r'^\s*\*\*?\s*proof\.?\**\s*:?\s*', re.IGNORECASE)


def build_proof_block(md: str) -> tuple[str, bool]:
    '''Return (proof_tex, already_wrapped).'''
    if '\\begin{proof}' in md:
        return md.strip(), True
    s = RE_STRIP_CLAIM.sub('', md.lstrip())
    s = RE_STRIP_PROOF_HDR.sub('', s, count=1)
    s = s.strip().rstrip('\u001a\u0019\ufeff\u0000')
    proof = '\n'.join(['\\begin{proof}', s, '\\end{proof}', ''])
    return proof, False


def make_theorem_tex(title: str, kind: str, conj_no: Optional[int], label_slug: str, statement_tex: str, proof_tex: str) -> str:
    bracket_title = title
    if conj_no is not None:
        bracket_title += f' ({kind} Conj.~{conj_no} of \\cite{{Cohen2025}})'
    header = f'\\begin{{theorem}}[{bracket_title}]\\label{{thm:{label_slug}}}'
    parts = [header, statement_tex.strip(), '\\end{theorem}', '', proof_tex.strip(), '']
    return '\n'.join(parts)


def main() -> int:
    if not NEW_BATCH.exists():
        print(f'Missing folder: {NEW_BATCH}', file=sys.stderr)
        return 1
    THEOREMS_DIR.mkdir(parents=True, exist_ok=True)

    pairs = []
    for txt_path in sorted(NEW_BATCH.glob('conj*.txt')):
        md_path = txt_path.with_suffix('.md')
        if md_path.exists():
            pairs.append((txt_path, md_path))

    if not pairs:
        print('No conj*.txt/.md pairs found.')
        return 0

    created = []
    for txt_path, md_path in pairs:
        txt = read_text(txt_path)
        md = read_text(md_path)
        conj_no, title, statement = find_conjecture_header_and_statement(txt)
        if not title:
            title = f'Result from {txt_path.name}'
        kind = infer_resolution_kind(md)
        base_slug = slugify_title(title)
        fname, label_slug = choose_unique_filename(base_slug)
        proof_tex, _ = build_proof_block(md)

        theorem_tex = make_theorem_tex(title, kind, conj_no, label_slug, statement, proof_tex)
        out_path = THEOREMS_DIR / fname
        out_path.write_text(theorem_tex, encoding='utf-8', newline='\n')
        created.append(out_path)
        rel = out_path.relative_to(ROOT)
        print(f'Wrote: {rel}  ({kind}, Conj {conj_no}, label thm:{label_slug})')

    print(f'\nCreated {len(created)} theorem file(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

