import re
text=open('paper/cohen41.txt',encoding='utf-8').read()
lines=text.splitlines()
conjs=[]
i=0
while i<len(lines):
    line=lines[i]
    m=re.match(r"\s*Conjecture\s+(\d+)\s*\((.*?)\)\.(.*)", line)
    if m:
        num=int(m.group(1))
        title=m.group(2)
        rest=m.group(3).strip()
        stmt=[rest] if rest else []
        j=i+1
        while j<len(lines):
            l=lines[j]
            if not l.strip():
                break
            if re.match(r"\s*Conjecture\s+\d+|^\f|^Figure|^\s*\d+\s*$", l):
                break
            if re.search(r"On seeing Conjecture|I verified|I confirmed|The right side|If true, Conjecture|Conjecture \d+ is false|I found no counterexamples|After seeing", l):
                break
            stmt.append(l)
            j+=1
        conjs.append((num,title,stmt))
        i=j
    else:
        i+=1
print(len(conjs))
for num,title,stmt in conjs:
    print(num, title)
