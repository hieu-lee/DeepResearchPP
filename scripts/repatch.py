import io
p='scripts/rebuild_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
lines[146] = "  8:(\"Deligne's conjecture: primes between squares\",\"Let \\(N_{\\mathcal P}(n):=\\#\\{\\,p\\in\\mathcal P: n^2<p<(n+1)^2\\,\\}\\). As (n\\to\\infty), N_{\\mathcal P}(n)\\sim n/\\log n.\"),"
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('patched line 146')
