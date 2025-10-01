import io
p='scripts/auto_build_list.py'
with io.open(p,encoding='utf-8') as f:
    lines=f.read().splitlines()
# Remove old line 125
lines.pop(125)
with io.open(p,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('removed line 125')
