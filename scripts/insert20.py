import io
p='scripts/rebuild_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
insert_idx = 156  # before current 22
lines.insert(insert_idx, '  20:("k-fold Oppermann for cyclics","For every \\(k\\in \\mathbb{N}\\) there exists \\(N(k)\\) such that for all \\(n>N(k)\\), both \\[n^2-n,n^2] and [n^2,n^2+n] contain at least k cyclic integers."),')
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Inserted 20')
