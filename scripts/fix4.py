import io
p='scripts/rebuild_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
del lines[155]
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('deleted old 19 line')
