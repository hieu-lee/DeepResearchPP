from __future__ import annotations

import re
import shutil
import subprocess
from typing import Any, Dict, List, Tuple


def _balanced_delimiters(text: str) -> List[str]:
    errors: List[str] = []
    stack: List[str] = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for idx, ch in enumerate(text):
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                errors.append(f"Unbalanced delimiter at index {idx}: '{ch}'")
            else:
                stack.pop()
    if stack:
        errors.append("Unbalanced delimiters: " + ''.join(stack))
    return errors


_MATH_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("inline_paren", re.compile(r"\\\((.+?)\\\)", re.DOTALL)),
    ("display_bracket", re.compile(r"\\\[(.+?)\\\]", re.DOTALL)),
    ("display_dollar", re.compile(r"\$\$(.+?)\$\$", re.DOTALL)),
    ("inline_dollar", re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)),
]


def _find_math_segments(md: str) -> List[str]:
    segments: List[str] = []
    for _name, pat in _MATH_PATTERNS:
        for m in pat.finditer(md):
            segments.append(m.group(1))
    return segments


def _katex_available() -> bool:
    if not shutil.which("node"):
        return False
    # Quick probe to see if katex is installed
    probe = subprocess.run(
        ["node", "-e", "try{require('katex');process.exit(0)}catch(e){process.exit(2)}"],
        capture_output=True,
        text=True,
    )
    return probe.returncode == 0


def _katex_validate(expr: str) -> Tuple[bool, str | None]:
    script = (
        "const fs=require('fs');"
        "let inp=fs.readFileSync(0,'utf8');"
        "try{const katex=require('katex');katex.renderToString(inp,{throwOnError:true});process.stdout.write('OK');}"
        "catch(e){process.stderr.write(e.message||String(e));process.exit(2);}"
    )
    p = subprocess.run(
        ["node", "-e", script],
        input=expr,
        text=True,
        capture_output=True,
    )
    if p.returncode == 0:
        return True, None
    return False, (p.stderr.strip() or p.stdout.strip() or "Unknown KaTeX error")


def validate_markdown(markdown: str) -> Dict[str, Any]:
    """Validate Markdown and math fragments; returns {ok: bool, errors: [..]}.

    - Fails on backticks, unbalanced delimiters, \begin/\end, and KaTeX render errors if available.
    """
    errors: List[str] = []

    if '```' in markdown:
        errors.append("Backticks (code fences) are not allowed in the report output.")

    errors.extend(_balanced_delimiters(markdown))

    if re.search(r"\\begin\{.+?\}|\\end\{.+?\}", markdown):
        errors.append("Environment blocks (\\begin{...} / \\end{...}) are not allowed.")

    katex_ok = _katex_available()
    if katex_ok:
        for seg in _find_math_segments(markdown):
            ok, err = _katex_validate(seg)
            if not ok:
                errors.append(f"KaTeX error: {err}")

    return {"ok": len(errors) == 0, "errors": errors}


def build_validate_markdown_tool_definition() -> Dict[str, Any]:
    return {
        "name": "validate_markdown",
        "type": "function",
        "description": (
            "Validate Markdown+KaTeX for the report. Returns {ok, errors[]} with human-readable issues."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "markdown": {
                    "type": "string",
                    "description": "Full markdown document to validate",
                }
            },
            "required": ["markdown"],
            "additionalProperties": False,
        },
    }


