import re, json
from textwrap import dedent

excl={9,52,54,59,60,61}
with open('paper/conjectures.json',encoding='utf-8') as f:
    conjs=json.load(f)

# Titles sometimes have funky chars; normalize some
norm=lambda s: s.replace('�','').replace('  ',' ').strip()

common_defs=dedent(r'''
\begin{definition}
Let \mathbb{N} denote the set of positive integers. Let \varphi(n) be Euler's totient function and let \gcd(\cdot,\cdot) be the greatest common divisor.
A positive integer m is called \emph{cyclic} if and only if \gcd\!\bigl(m,\varphi(m)\bigr)=1. Define the set of cyclic integers
\[\mathcal{C}:=\{m\in\mathbb{N}: \gcd(m,\varphi(m))=1\},\]
and let \(c_1<c_2<\cdots\) be the increasing enumeration of \(\mathcal{C}\).
Let \(\mathcal{P}\) be the set of prime numbers and let \(p_1<p_2<\cdots\) be its increasing enumeration. Let \(\gamma\) denote the Euler--Mascheroni constant.
For a set S, write \(\#S\) for its cardinality.
\end{definition}''')

defs_blocks={
 'squares': dedent(r'''\begin{definition}
For \(n\in\mathbb{N}\), let \(N_{\mathcal P}(n):=\#\{\,p\in\mathcal P: n^2<p<(n+1)^2\,\}\) be the number of primes strictly between successive squares, and
let \(N_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2<c<(n+1)^2\,\}\) be the analogous quantity for cyclic integers.
\end{definition}'''),
 'L': dedent(r'''\begin{definition}
Define the \emph{k-fold Legendre index sequences} as follows. Let \(L_{\mathcal P}\subseteq \mathbb{N}\) be the set of integers k such that for all integers \(j>k\), we have \(N_{\mathcal P}(j)\ge N_{\mathcal P}(k)\).
Similarly, let \(L_{\mathcal C}\subseteq \mathbb{N}\) be the set of integers k such that for all \(j>k\), we have \(N_{\mathcal C}(j)\ge N_{\mathcal C}(k)\).
For \(n\in\mathbb{N}\), write \(L_{\mathcal P}(n)\) and \(L_{\mathcal C}(n)\) for the n-th elements of these increasing sequences.
\end{definition}'''),
 'Op': dedent(r'''\begin{definition}
For \(n\in\mathbb{N}\), define the half-square interval counts for cyclic integers
\[
N^{-}_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2-n\le c\le n^2\,\},\qquad
N^{+}_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2\le c\le n^2+n\,\}.
\]
\end{definition}'''),
 'SG': dedent(r'''\begin{definition}
A \emph{Sophie Germain cyclic} is a cyclic integer \(c\in\mathcal{C}\) such that \(2c+1\in\mathcal{C}\). Let the increasing sequence of SG cyclics be \(\sigma_1<\sigma_2<\cdots\).
Define the counting function of SG cyclics by \(C_{\mathrm{SG}}(x):=\#\{\,\sigma\le x : \sigma\text{ is an SG cyclic}\,\}\).
\end{definition}'''),
 'SADS': dedent(r'''\begin{definition}
Given an initial sequence \(a_1,a_2,a_3,\dots\) of positive integers, define its \emph{successive absolute difference sequences} (SADS) recursively by
\(a^{(0)}_n:=a_n\) and, for \(k\ge 1\), \(a^{(k)}_n:=\lvert a^{(k-1)}_{n+1}-a^{(k-1)}_{n}\rvert\) for all indices where this is defined.
The \emph{first element of each successor sequence} refers to \(a^{(k)}_1\), \(k\ge 1\).
\end{definition}'''),
 'Ccount': dedent(r'''\begin{definition}
The counting function of cyclic integers is \(C(x):=\#\{\,c\in\mathcal{C}: c\le x\,\}\).
\end{definition}''')
}

extra_by_num={
 8:['squares'],
 10:['squares','L'],
 11:['squares','L'],
 12:['squares','L'],
 13:['squares','L'],
 16:[],
 17:[],
 19:['Op'],
 20:[],
 22:[],
 23:[],
 24:[],
 25:[],
 26:[],
 27:[],
 28:[],
 29:[],
 30:[],
 31:[],
 32:[],
 33:[],
 34:[],
 35:[],
 36:['SG'],
 37:['SG'],
 38:['SG'],
 39:[],
 40:[],
 41:[],
 42:[],
 43:['SG'],
 44:[],
 45:[],
 46:[],
 47:[],
 48:[],
 49:[],
 50:[],
 51:['SG'],
 53:[],
 55:['SG'],
 56:[],
 57:[],
 58:['SG'],
 62:['SADS'],
 63:['SADS','SG'],
 64:['SG'],
 65:['Ccount'],
 66:['SG'],
}

# Bodies: build from extracted statements with some cleanup; for complex ones we rewrite succinctly
bodies={}
for item in conjs:
    n=item['num']
    if n in excl: continue
    title=norm(item['title'])
    stmt=norm(item['stmt'])
    # quick normalizations
    stmt=stmt.replace('�^','').replace('�%','').replace('�','').replace('  ',' ')
    # Replacements for math intervals
    stmt=stmt.replace(' (', ' (').replace(' )',' )')
    bodies[n]=(title,stmt)

# Overwrite some bodies with precise LaTeX we crafted for clarity
custom={
 2:("Goldbach analog for cyclics","For every even integer \\(n>2\\), there exist cyclic integers \\(c_1,c_2\\in\\mathcal{C}\\) such that \\(c_1+c_2=n\\)."),
 3:("Twin cyclics analog","There exist infinitely many cyclic integers \\(c\\in\\mathcal{C}\\) such that \\(c+2\\in\\mathcal{C}\\)."),
 4:("Cyclic triplets","There exist infinitely many composite cyclic integers \\(c\\in\\mathcal{C}\\) such that \\(c, c+2, c+4\\) are all composite and lie in \\mathcal{C}."),
 5:("Cyclic quintuplets","There exist infinitely many cyclic integers \\(c\\in\\mathcal{C}\\) such that \\(c, c+2, c+4, c+6, c+8\\) are all in \\mathcal{C}."),
 6:("Legendre analog for cyclics","For every \\(n\\in\\mathbb{N}\\), there exists \\(c\\in\\mathcal{C}\\) with \\(n^2<c<(n+1)^2\\)."),
 7:("Desboves analog for cyclics","For every \\(n\\in\\mathbb{N}\\), there exist \\(c<c'\\) in \\mathcal{C} with \\(n^2<c<c'<(n+1)^2\\)."),
  8:("Deligne's conjecture: primes between squares","Let \(N_{\mathcal P}(n):=\#\{\,p\in\mathcal P: n^2<p<(n+1)^2\,\}\). As \(n\to\infty\), N_{\mathcal P}(n)\sim n/\log n."),
 10:("k-fold Legendre for primes","Define \\(L_{\\mathcal P}\\) as in the definitions. Then \\(L_{\\mathcal P}\\) begins \\(\\{1,7,11,17,18,26,27,32,46,50,56,58,85,88,92,137,143,145,\\dots\\}\\)."),
 11:("Asymptotic k-fold Legendre for primes","There exists a regularly varying function with index \\(b\\in(3/2,2]\\) such that \\(L_{\\mathcal P}(n)\\sim n^b\\,\\ell(n)\\)."),
 12:("k-fold Legendre for cyclics","Define \\(L_{\\mathcal C}\\) as in the definitions. Then \\(L_{\\mathcal C}\\) begins \\(1,3,5,8,11,14,15,16,19,21,27,29,33,38,39,46,47,51,58,61,62,66,82,86,90,104,105,108,110,118,126,127,129,131,138,141,149,152,159,161,167,170,172,174,180,182,185,187,\\dots\\)."),
 13:("Asymptotic k-fold Legendre for cyclics","There exists a regularly varying function with index \\(b\\in[1,2]\\) such that \\(L_{\\mathcal C}(n)\\sim n^b\\,\\ell(n)\\)."),
 14:("Near-square analog for cyclics","Infinitely many \\(n\\in\\mathbb{N}\\) satisfy \\(n^2+1\\in\\mathcal{C}\\)."),
 15:("Near-square analog of Golubew for cyclics","For every \\(m\\in\\mathbb{N}\\), \\((m^3,(m+1)^3)\\) contains a cyclic \\(n^2+1\\); and \\((m^4,(m+1)^4)\\) contains two such values \\(n^2+1<n'^2+1\\)."),
 16:("Counting Oppermann primes","Let \\(N_{\\mathcal P}^{-}(n):=\\#\\{\\,p\\in\\mathcal P: n^2-n\\le p\\le n^2\\,\\}\\) and \\(N_{\\mathcal P}^{+}(n):=\\#\\{\\,p\\in\\mathcal P: n^2\\le p\\le n^2+n\\,\\}\\). Then \\(N_{\\mathcal P}^{-}(n)\\sim N_{\\mathcal P}^{+}(n)\\sim n/(2\\log n)\\)."),
 17:("k-fold Oppermann for primes","For every \\(k\\in\\mathbb{N}\\) there exists \\(N(k)\\) such that for all \\(n>N(k)\\), both \\[n^2-n,n^2] and [n^2,n^2+n] contain at least k primes."),
 19:("Oppermann analog for cyclics","For every \\(n>1\\) there exist \\(c,c'\\in\\mathcal{C}\\) with \\(n^2-n<c<n^2<c'<n^2+n\\). Moreover, \\(N_{\\mathcal C}^{\\pm}(n)\\sim n/(e^{\\gamma}\\,\\log\\log\\log n)\\bigl(1-\\gamma/\\log\\log\\log n\bigr)\\)."),
 20:("k-fold Oppermann for cyclics","For every \\(k\\in \\mathbb{N}\\) there exists \\(N(k)\\) such that for all \\(n>N(k)\\), both \\[n^2-n,n^2] and [n^2,n^2+n] contain at least k cyclic integers."),
 22:("k-fold Brocard for primes","There exists \\(B:\\mathbb{N}\\to\\mathbb{N}\\) such that for all \\(n\\ge B(k)\\), \\([n^2,(n+1)^2]\\) contains at least k primes (with empirical small values listed in the paper)."),
 23:("Brocard analog for cyclics","For every \\(n>2\\), the open interval \\((c_n^2, c_{n+1}^2)\\) contains at least six cyclic integers."),
 24:("k-fold Brocard analog for cyclics","There exists \\(C:\\mathbb{N}\\to\\mathbb{N}\\) such that for all \\(n\\ge C(k)\\), \\((c_n^2, c_{n+1}^2)\\) contains at least k cyclic integers."),
 25:("Schinzel P1 analog for cyclics","For every \\(n\\), \\(c_{n+1}\\le c_n+\\sqrt{c_n}\\) with exceptions \\(c_3=3,c_5=7,c_{11}=23\\)."),
 26:("Schinzel log^2 analog for cyclics","For every \\(n\\), \\(c_{n+1}\\le c_n+(\\log c_n)^2\\) with exceptions \\(c_1=1, c_2=2, c_3=3, c_5=7\\)."),
 27:("Schinzel 2·log analog for cyclics","For every \\(n\\), \\(c_{n+1}\\le c_n+2\\log c_n\\) with exceptions \\(c_1=1, c_5=7\\)."),
 28:("Twin primes between consecutive cubes","For every \\(n\\), at least two twin prime pairs lie between \\(n^3\\) and \\((n+1)^3\\); more generally, at least k beyond a threshold."),
 29:("Cousin primes between consecutive cubes","For \\(n>1\\), at least two cousin prime pairs lie between consecutive cubes; more generally, at least k beyond a threshold."),
 30:("Sexy primes between consecutive cubes","For \\(n>2\\), at least two sexy prime pairs lie between consecutive cubes; more generally, at least k beyond a threshold."),
 31:("Asymptotic k-fold primes between cubes","Counts of twin/cousin/sexy prime pairs between \\(n^3\\) and \\((n+1)^3\\) are asymptotic to regularly varying functions with indices in \\((3/2,2]\\)."),
 32:("Twin cyclics between consecutive cubes","At least two twin cyclic pairs between \\(n^3\\) and \\((n+1)^3\\); more generally, at least k beyond a threshold."),
 33:("Cousin cyclics between consecutive cubes","For \\(n>1\\), at least one cousin cyclic pair between consecutive cubes; more generally, at least k beyond a threshold."),
 34:("Sexy cyclics between consecutive cubes","For \\(n\\ge 5\\), at least two sexy cyclic pairs between consecutive cubes; more generally, at least k beyond a threshold."),
 35:("Asymptotic k-fold cyclics between cubes","Counts of twin/cousin/sexy cyclic pairs between cubes are asymptotic to regularly varying functions with indices in \\[1,5/2]\\."),
 36:("Infinitely many SG cyclics","There are infinitely many \\(c\\in\\mathcal{C}\\) with \\(2c+1\\in\\mathcal{C}\\)."),
 37:("SG cyclics modulo 3","As the number of SG cyclics grows, the limiting fractions congruent to 1 and 3 mod 3 are equal."),
 38:("Desboves analog for SG cyclics","For every \\(n\\), there are at least two SG cyclics in \\((n^2,(n+1)^2)\\)."),
 39:("Firoozbakht analog for cyclics 1","For all \\(n\\notin\\{1,2,3,5\\}\\), \\(c_{n+1}^{1/(n+1)}<c_n^{1/n}\\)."),
 40:("Firoozbakht analog for cyclics 2","For all \\(n>1\\), \\(c_n^{1/(n-1)}>c_{n+1}^{1/n}\\), interpreting \\(c_1^{1/0}:=1\\)."),
 41:("Firoozbakht analog for cyclics 3","For each \\(k\\) there exists \\(N(k)\\) such that for all \\(n>N(k)\\), \\(c_n^{1/(n+k)}>c_{n+1}^{1/(n+k+1)}\\)."),
 42:("Firoozbakht analog for cyclics 4","For \\(k\\in\\{0\\}\\cup\\mathbb{N}\\), define \\(A_{\\mathcal{C}}(k):=\\max_{n\\ge1} c_n^{1/(n+k)}\\). Then \\(A_{\\mathcal{C}}(k)\\) strictly decreases with k (empirical values in paper)."),
 43:("Firoozbakht analog for SG cyclics","For all \\(n\\notin\\{1,2,3,5\\}\\), \\(\\sigma_{n+1}^{1/(n+1)}<\\sigma_n^{1/n}\\)."),
 44:("Andrica analog for cyclics","For all \\(n\\), \\sqrt{c_{n+1}}-\\sqrt{c_n}<1\\."),
 45:("Generalized analog for primes","For all \\(t\\in(0,1/2]\\), \\lim_{n\\to\\infty}(p_{n+1}^t-p_n^t)=0\\."),
 46:("Generalized analog for cyclics","For all \\(t\\in(0,1/2]\\), \\lim_{n\\to\\infty}(c_{n+1}^t-c_n^t)=0\\."),
 47:("Visser analog for cyclics","For every \\varepsilon\\in(0,1/2) there exists N(\\varepsilon) s.t. for all \\(n>N(\\varepsilon)\\), \\sqrt{c_{n+1}}-\\sqrt{c_n}<\\varepsilon\\."),
 48:("Generalized KMSZ for primes","For each integer k there exists N(k) s.t. for all n>N(k), p_{n+1}-p_n<\\sqrt{p_n}+k."),
 49:("Generalized KMSZ for cyclics","For each integer k there exists N(k) s.t. for all n>N(k), c_{n+1}-c_n<\\sqrt{c_n}+k."),
 50:("Carneiro analog for cyclics","For all n with c_n>3, c_{n+1}-c_n<\\sqrt{c_n\\log c_n}."),
 51:("Carneiro analog for SG cyclics","For all n with \\sigma_n>3, \\sigma_{n+1}-\\sigma_n<\\sqrt{\\sigma_n\\log \\sigma_n}."),
 53:("Dusart analog for cyclics","For all n>1, \\(c_n>e^{\\gamma}n(\\log\\log\\log n+\\log\\log\\log\\log n)\\)."),
 55:("Ishikawa analog for SG cyclics","For all n>2, \\sigma_n+\\sigma_{n+1}>\\sigma_{n+2}."),
 56:("sum-3-versus-sum-2 analog for cyclics","For all n>9, c_n+c_{n+1}+c_{n+2}>c_{n+3}+c_{n+4}."),
 57:("Dusart–Mandl analog for cyclics","For all n>5, (c_1+\\cdots+c_n)/n<c_n/2."),
 58:("Dusart–Mandl analog for SG cyclics","For all n>5, (\\sigma_1+\\cdots+\\sigma_n)/n<\\sigma_n/2."),
 62:("Proth–Gilbreath analog for cyclics","Form the SADS from (c_n) with c_1 omitted; then the first term of every successor sequence equals 1."),
 63:("Proth–Gilbreath analog for SG cyclics","Form the SADS from (\\sigma_n) with \\sigma_1 omitted; then the first term of every successor sequence equals 1."),
 64:("Hardy–Littlewood analog for SG primes","Let \\pi_{SG}(x) count SG primes; for all 2\\le m\\le n, \\pi_{SG}(m+n)\\le \\pi_{SG}(m)+\\pi_{SG}(n)."),
 65:("Hardy–Littlewood analog for cyclics","With C(x) the cyclic counting function, for all 1\\le m\\le n, C(m+n)\\le C(m)+C(n)."),
 66:("Hardy–Littlewood analog for SG cyclics","With C_{SG}(x) the SG cyclic counting function, for all 1\\le m\\le n, C_{SG}(m+n)\\le C_{SG}(m)+C_{SG}(n)."),
}

for k,v in custom.items():
    bodies[k]=v

order=[2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,19,20,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,53,55,56,57,58,62,63,64,65,66]

out=[]
for n in order:
    title,stmt = bodies[n]
    blocks=[common_defs]
    for key in extra_by_num.get(n,[]):
        blocks.append(defs_blocks[key])
    entry = '\n\n'.join(blocks)
    entry += f"\n\n\\bigskip\n\n\\textbf{{Conjecture {n} ({title}).}}\n{stmt}"
    out.append('"""\n'+entry+'\n"""')

with open('open_problems/list.txt','w',encoding='utf-8') as f:
    f.write('[\n'+',\n\n'.join(out)+'\n]\n')
print('Wrote',len(out),'entries to open_problems/list.txt')