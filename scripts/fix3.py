import io
p='scripts/rebuild_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
# Merge line 156 and 157 into one
merged = '  19:("Oppermann analog for cyclics","For every \\(n>1\\) there exist \\(c,c\'\\in\\mathcal{C}\\) with \\(n^2-n<c<n^2<c\'<n^2+n\\). Moreover, \\(N_{\\mathcal C}^{-}(n)\\sim \\frac{n}{e^{\\gamma}\\,\\log\\log\\log n}(1-\\gamma/\\log\\log\\log n)\\) and similarly for \\(N_{\\mathcal C}^{+}(n)\\)."),'
lines[156] = merged
# Delete the old continuation line 157
del lines[157]
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('patched 19')
