import re
from pathlib import Path

ROOT = Path(r"D:\DeepResearchPP\JoIS paper\theorems")

# Characters that, if a line starts with them, we may want to join with the previous line
LINE_START_JOIN_CHARS = (
    '(',
)


def fix_double_backslashes_preserving_eol(line: str) -> tuple[str, int]:
    """
    Replace doubled backslashes (\\) with single backslashes (\) everywhere
    EXCEPT for the final linebreak command at end of line. If the end of the line
    has multiple backslashes due to duplication (e.g., \\\\), normalize to a single
    LaTeX linebreak (\\) at the very end.

    Returns (new_line, replacements_count).
    """
    # Separate newline characters to preserve original newline style
    nl = ''
    if line.endswith("\r\n"):
        core = line[:-2]
        nl = "\r\n"
    elif line.endswith("\n"):
        core = line[:-1]
        nl = "\n"
    else:
        core = line

    # Identify trailing whitespace and backslashes before newline
    rstrip_ws = core.rstrip(' \t')
    trailing_ws = core[len(rstrip_ws):]

    # Count trailing backslashes in the trimmed core
    trailing_bs = 0
    i = len(rstrip_ws) - 1
    while i >= 0 and rstrip_ws[i] == '\\':
        trailing_bs += 1
        i -= 1

    # If there are trailing backslashes, we preserve exactly two (LaTeX linebreak)
    has_eol_break = trailing_bs >= 2
    preserved_tail = ''
    if has_eol_break:
        # Remove the trailing backslashes from the core
        head = rstrip_ws[:-trailing_bs]
        # First collapse quadruple backslashes to double, then double to single in the head
        tmp = head.replace('\\\\', '\\')
        converted_head = tmp.replace('\\'*2, '\\')
        # Preserve exactly two backslashes as the linebreak command
        preserved_tail = '\\\\' + trailing_ws
        new_core = converted_head + preserved_tail
        # Count replacements: approximate by counting pairs in head
        repl_count = head.count('\\\\') + head.count('\\')
    else:
        # No special EOL break; convert globally (quadruple->double, then double->single)
        before = core
        tmp = before.replace('\\\\', '\\')
        after = tmp.replace('\\'*2, '\\')
        new_core = after
        repl_count = before.count('\\\\') + before.count('\\')

    return new_core + nl, repl_count


def join_bad_line_starts(lines: list[str]) -> tuple[list[str], int]:
    """
    Join lines that start with undesirable characters like '(' with the previous line,
    but avoid touching display-math blocks started by \[ ... \] or $$ ... $$. Returns
    (new_lines, joins_made).
    """
    out: list[str] = []
    joins = 0
    inside_bracket_display = False  # \[ ... \]
    inside_dollar_display = False   # $$ ... $$ possibly multiline

    def trimmed(s: str) -> str:
        return s.rstrip('\r\n')

    for idx, line in enumerate(lines):
        t = trimmed(line).lstrip()
        tno = trimmed(line)
        # Track display math boundaries (consider both forms before/after fixes)
        t_stripped = tno.strip()
        if (t_stripped.startswith('\\[') or t_stripped.startswith('[')) and False:
            # dead branch kept for clarity; handled below using startswith on full tokens
            pass
        # Toggle bracket display
        if t_stripped.startswith('\\[') or t_stripped == '\\[' or t_stripped == '\[':
            inside_bracket_display = True
        if t_stripped.startswith('\\]') or t_stripped == '\\]' or t_stripped == '\]':
            inside_bracket_display = False
        # Toggle dollar display
        if t_stripped == '$$':
            inside_dollar_display = not inside_dollar_display
        elif t_stripped.startswith('$$') and t_stripped.endswith('$$') and len(t_stripped) > 2:
            # single-line $$ ... $$; do nothing to inside_dollar_display
            pass

        if out and not inside_bracket_display and not inside_dollar_display:
            # Only consider joining for text mode lines
            if t and t[0] in LINE_START_JOIN_CHARS:
                # Join with previous line
                prev = out.pop()
                # Remove its newline, add a space if needed, then append current line sans leading spaces
                if prev.endswith('\r\n'):
                    base = prev[:-2]
                    nl = '\r\n'
                elif prev.endswith('\n'):
                    base = prev[:-1]
                    nl = '\n'
                else:
                    base = prev
                    nl = ''
                # Ensure a single space between
                base = base.rstrip()
                joined = base + ' ' + tno.lstrip()
                out.append(joined + nl)
                joins += 1
                continue
        out.append(line)

    return out, joins


def ensure_step_headers_on_new_lines(text: str) -> tuple[str, int]:
    """
    Ensure occurrences of true step headers like "Step 1)", "Step 2:", "Step 3." start at a new line.
    Avoid touching references like "in Step 3" or "Steps 1-4".
    Returns (new_text, changes).
    """
    changes = 0

    # Pattern for step headers: Step <number> followed by ) or : or .
    step_pat = re.compile(r"(^|[^\n])(Step\s*[0-9]+\s*[)\.:])")

    def repl(m: re.Match) -> str:
        nonlocal changes
        prefix = m.group(1)
        step = m.group(2)
        # If prefix is empty, already at line start
        if prefix == '':
            return step
        # Avoid inserting a newline for references like "in Step 3" by demanding prefix ends with whitespace
        if not prefix.isspace():
            return prefix + step
        changes += 1
        return '\n' + step

    new_text = step_pat.sub(repl, text)
    return new_text, changes


def process_file(path: Path) -> dict:
    raw = path.read_text(encoding='utf-8')
    lines = raw.splitlines(keepends=True)

    # Pass 1: Fix doubled backslashes preserving EOL linebreaks
    fixed_lines: list[str] = []
    backslash_fixes = 0
    for line in lines:
        new_line, cnt = fix_double_backslashes_preserving_eol(line)
        fixed_lines.append(new_line)
        backslash_fixes += cnt

    # Pass 2: Join lines starting with '(' outside display math blocks
    joined_lines, joins = join_bad_line_starts(fixed_lines)

    # Pass 3: Ensure step headers start on new lines (conservative)
    joined_text = ''.join(joined_lines)
    final_text, step_changes = ensure_step_headers_on_new_lines(joined_text)

    changed = final_text != raw
    if changed:
        path.write_text(final_text, encoding='utf-8', newline='')

    return {
        'file': str(path),
        'changed': changed,
        'backslash_fixes': backslash_fixes,
        'joins': joins,
        'step_changes': step_changes,
    }


def main():
    if not ROOT.exists():
        print(f"Theorems directory not found: {ROOT}")
        return
    tex_files = sorted(ROOT.glob('*.tex'))
    if not tex_files:
        print("No .tex files found.")
        return
    summary = []
    for f in tex_files:
        res = process_file(f)
        summary.append(res)
        if res['changed']:
            print(f"Updated: {f.name} (\\ fixes={res['backslash_fixes']}, joins={res['joins']}, steps={res['step_changes']})")
        else:
            print(f"No change: {f.name}")

    # Simple totals
    total_changed = sum(1 for r in summary if r['changed'])
    total_bf = sum(r['backslash_fixes'] for r in summary)
    total_joins = sum(r['joins'] for r in summary)
    total_steps = sum(r['step_changes'] for r in summary)
    print(f"Done. Files changed: {total_changed}, backslash fixes: {total_bf}, joins: {total_joins}, step newlines: {total_steps}")

if __name__ == '__main__':
    main()
