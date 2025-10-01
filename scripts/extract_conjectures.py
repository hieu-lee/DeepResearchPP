import os
import re

SRC = os.path.join('open_problems', 'list.txt')
OUT_DIR = os.path.join('open_problems')

def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        data = f.read()

    # Extract raw triple-quoted string contents r""" ... """
    blocks = re.findall(r'r"""\s*(.*?)\s*"""', data, flags=re.DOTALL)

    conjectures = []
    for blk in blocks:
        def_m = re.search(r'\\begin\{definition\}.*?\\end\{definition\}', blk, flags=re.DOTALL)
        conj_m = re.search(r'\\textbf\{Conjecture[^\n]*\}\s*\n.*', blk, flags=re.DOTALL)
        if conj_m:
            if def_m:
                combined = def_m.group(0).strip() + "\n\n" + blk[conj_m.start():].strip()
            else:
                combined = blk[conj_m.start():].strip()
            conjectures.append(combined)

    if not conjectures:
        raise SystemExit('No conjecture statements found in list.txt')

    # Write each conjecture (with definition) to conj{i}.txt
    for i, stmt in enumerate(conjectures, start=1):
        out_path = os.path.join(OUT_DIR, f'conj{i}.txt')
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(stmt + "\n")

    print(f"Wrote {len(conjectures)} conjecture files to {OUT_DIR}")

if __name__ == '__main__':
    main()
