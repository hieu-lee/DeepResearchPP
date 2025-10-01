import io
p='scripts/rebuild_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
del lines[147]
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('removed line 147')
