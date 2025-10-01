from pdfminer.high_level import extract_text
p='paper/cohen41.pdf'
print('Extracting from',p)
text=extract_text(p)
open('paper/cohen41.txt','w',encoding='utf-8').write(text)
print('Wrote text length',len(text))
