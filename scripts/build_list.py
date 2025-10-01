# -*- coding: utf-8 -*-
from textwrap import dedent

def common_defs():
    return dedent(r'''
    \begin{definition}
    Let \mathbb{N} denote the set of positive integers. Let \varphi(n) be Euler's totient function and let \gcd(\cdot,\cdot) be the greatest common divisor.
    A positive integer m is called \emph{cyclic} if and only if \gcd\!\bigl(m,\varphi(m)\bigr)=1. Define the set of cyclic integers
    \[\mathcal{C}:=\{m\in\mathbb{N}: \gcd(m,\varphi(m))=1\},\]
    and let \(c_1<c_2<\cdots\) be the increasing enumeration of \(\mathcal{C}\).
    Let \(\mathcal{P}\) be the set of prime numbers and let \(p_1<p_2<\cdots\) be its increasing enumeration. Let \(\gamma\) denote the Euler--Mascheroni constant.
    For a set S, write \(\#S\) for its cardinality.
    \end{definition}
    ''').strip()

def defs_squares_primes():
    return dedent(r'''
    \begin{definition}
    For \(n\in\mathbb{N}\), let \(N_{\mathcal P}(n):=\#\{\,p\in\mathcal P: n^2<p<(n+1)^2\,\}\) be the number of primes strictly between successive squares, and
    let \(N_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2<c<(n+1)^2\,\}\) be the analogous quantity for cyclic integers.
    \end{definition}
    ''').strip()

def defs_L_sequences():
    return dedent(r'''
    \begin{definition}
    Define the \emph{k-fold Legendre index sequences} as follows. Let \(L_{\mathcal P}\subseteq \mathbb{N}\) be the set of integers k such that for all integers \(j>k\), we have \(N_{\mathcal P}(j)\ge N_{\mathcal P}(k)\).
    Similarly, let \(L_{\mathcal C}\subseteq \mathbb{N}\) be the set of integers k such that for all \(j>k\), we have \(N_{\mathcal C}(j)\ge N_{\mathcal C}(k)\).
    For \(n\in\mathbb{N}\), write \(L_{\mathcal P}(n)\) and \(L_{\mathcal C}(n)\) for the n-th elements of these increasing sequences.
    \end{definition}
    ''').strip()

def defs_oppermann_counts():
    return dedent(r'''
    \begin{definition}
    For \(n\in\mathbb{N}\), define the half-square interval counts for cyclic integers
    \[
    N^{-}_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2-n\le c\le n^2\,\},\qquad
    N^{+}_{\mathcal C}(n):=\#\{\,c\in\mathcal C: n^2\le c\le n^2+n\,\}.
    \]
    \end{definition}
    ''').strip()

def defs_brocard():
    return dedent(r'''
    \begin{definition}
    For \(k\in\mathbb{N}\), let \(B(k)\) denote a threshold such that for all \(n\ge B(k)\), the interval \([n^2,(n+1)^2]\) contains at least \(k\) primes. Likewise, \(C(k)\) will denote a threshold such that for all \(n\ge C(k)\), the interval \([n^2,(n+1)^2]\) contains at least \(k\) cyclic integers.
    \end{definition}
    ''').strip()

def defs_cubes_pairs(label, gap):
    names = {2:'twin',4:'cousin',6:'sexy'}
    gapname = names[gap]
    return dedent('''\
    \\begin{definition}
    A pair of consecutive {label} \\((x_m,x_{{m+1}})\\) is called \\emph{{{gapname}}} if \\(x_{{m+1}}-x_m={gap}\\).
    For \\(n\\in\\mathbb{{N}}\\), the number of {gapname} {label} between the cubes \\(n^3\\) and \\((n+1)^3\\) is the number of indices m such that \\(n^3<x_m<x_{{m+1}}\\le (n+1)^3\\) and \\(x_{{m+1}}-x_m={gap}\\).
    \\end{definition}
    '''.format(label=label, gapname=gapname, gap=gap)).strip()

def defs_SG():
    return dedent(r'''
    \begin{definition}
    A \emph{Sophie Germain cyclic} is a cyclic integer \(c\in\mathcal{C}\) such that \(2c+1\in\mathcal{C}\). Let the increasing sequence of SG cyclics be \(\sigma_1<\sigma_2<\cdots\).
    Define the counting function of SG cyclics by \(C_{\mathrm{SG}}(x):=\#\{\,\sigma\le x : \sigma\text{ is an SG cyclic}\,\}\).
    \end{definition}
    ''').strip()

def defs_SADS():
    return dedent(r'''
    \begin{definition}
    Given an initial sequence \(a_1,a_2,a_3,\dots\) of positive integers, define its \emph{successive absolute difference sequences} (SADS) recursively by
    \(a^{(0)}_n:=a_n\) and, for \(k\ge 1\), \(a^{(k)}_n:=\lvert a^{(k-1)}_{n+1}-a^{(k-1)}_{n}\rvert\) for all indices where this is defined.
    The \emph{first element of each successor sequence} refers to \(a^{(k)}_1\), \(k\ge 1\).
    \end{definition}
    ''').strip()

def defs_counting_C():
    return dedent(r'''
    \begin{definition}
    The counting function of cyclic integers is \(C(x):=\#\{\,c\in\mathcal{C}: c\le x\,\}\).
    \end{definition}
    ''').strip()

def entry(num, title, body, extra_defs=None):
    parts = [common_defs()]
    if extra_defs:
        parts.extend(extra_defs)
    defs_block = "\n\n".join(parts)
    tmpl = '"""\n' + defs_block + '\n\n\\bigskip\n\n\\textbf{Conjecture NUM (TITLE).}\n' + body + '\n"""'
    return tmpl.replace('NUM', str(num)).replace('TITLE', title)

entries = []

# 2 Goldbach analog for cyclics
entries.append(entry(2, 'Goldbach analog for cyclics', dedent(r'''
For every even integer \(n>2\), there exist cyclic integers \(c_1,c_2\in\mathcal{C}\) such that \(c_1+c_2=n\).
'''))

# 3 twin cyclics analog
entries.append(entry(3, 'Twin cyclics analog', dedent(r'''
There exist infinitely many cyclic integers \(c\in\mathcal{C}\) such that \(c+2\in\mathcal{C}\).
'''))

# 4 cyclic triplets
entries.append(entry(4, 'Cyclic triplets', dedent(r'''
There exist infinitely many composite cyclic integers \(c\in\mathcal{C}\) such that \(c,\,c+2,\,c+4\) are all composite and all belong to \(\mathcal{C}\).
'''))

# 5 cyclic quintuplets
entries.append(entry(5, 'Cyclic quintuplets', dedent(r'''
There exist infinitely many cyclic integers \(c\in\mathcal{C}\) such that \(c,\,c+2,\,c+4,\,c+6,\,c+8\) are all in \(\mathcal{C}\).
'''))

# 6 Legendre analog for cyclics
entries.append(entry(6, 'Legendre analog for cyclics', dedent(r'''
For every \(n\in\mathbb{N}\), there exists a cyclic integer \(c\in\mathcal{C}\) with \(n^2<c<(n+1)^2\).
'''))

# 7 Desboves analog for cyclics
entries.append(entry(7, 'Desboves analog for cyclics', dedent(r'''
For every \(n\in\mathbb{N}\), there exist cyclic integers \(c<c'\) in \(\mathcal{C}\) such that \(n^2<c<c'<(n+1)^2\).
'''))

# 8 Deligne’s conjecture for primes in square intervals
entries.append(entry(8, "Deligne's conjecture: primes between squares", dedent(r'''
Let \(N_{\mathcal P}(n):=\#\{\,p\in\mathcal P: n^2<p<(n+1)^2\,\}\). As \(n\to\infty\),
\[\,N_{\mathcal P}(n)\sim \frac{n}{\log n}.\]
'''), extra_defs=[defs_squares_primes()]))

# 10 k-fold Legendre for primes
entries.append(entry(10, 'k-fold Legendre for primes', dedent(r'''
Define \(L_{\mathcal P}\) as in the definitions. Then the increasing sequence \(L_{\mathcal P}\) begins
\[\,L_{\mathcal P} = \{1,\,7,\,11,\,17,\,18,\,26,\,27,\,32,\,46,\,50,\,56,\,58,\,85,\,88,\,92,\,137,\,143,\,145,\,\dots\}.\]
'''), extra_defs=[defs_squares_primes(), defs_L_sequences()]))

# 11 asymptotic k-fold Legendre for primes
entries.append(entry(11, 'Asymptotic k-fold Legendre for primes', dedent(r'''
Let \(L_{\mathcal P}(n)\) be the n-th element of \(L_{\mathcal P}\). There exists a regularly varying function with index \(b\in(3/2,2]\) such that, as \(n\to\infty\),
\[\,L_{\mathcal P}(n)\sim n^{b}\,\ell(n)\]
for some slowly varying function \(\ell\).
'''), extra_defs=[defs_squares_primes(), defs_L_sequences()]))

# 12 k-fold Legendre for cyclics
entries.append(entry(12, 'k-fold Legendre for cyclics', dedent(r'''
Define \(L_{\mathcal C}\) as in the definitions. Then the increasing sequence \(L_{\mathcal C}\) begins
\[\,L_{\mathcal C} = (1,\,3,\,5,\,8,\,11,\,14,\,15,\,16,\,19,\,21,\,27,\,29,\,33,\,38,\,39,\,46,\,47,\,51,\,58,\,61,\,62,\,66,\,82,\,86,\,90,\,104,\,105,\,108,\,110,\,118,\,126,\,127,\,129,\,131,\,138,\,141,\,149,\,152,\,159,\,161,\,167,\,170,\,172,\,174,\,180,\,182,\,185,\,187,\,\dots).\]
'''), extra_defs=[defs_squares_primes(), defs_L_sequences()]))

# 13 asymptotic k-fold Legendre for cyclics
entries.append(entry(13, 'Asymptotic k-fold Legendre for cyclics', dedent(r'''
Let \(L_{\mathcal C}(n)\) be the n-th element of \(L_{\mathcal C}\). There exists a regularly varying function with index \(b\in[1,2]\) such that, as \(n\to\infty\),
\[\,L_{\mathcal C}(n)\sim n^{b}\,\ell(n)\]
for some slowly varying function \(\ell\).
'''), extra_defs=[defs_squares_primes(), defs_L_sequences()]))

# 14 near-square analog for cyclics
entries.append(entry(14, 'Near-square analog for cyclics', dedent(r'''
There exist infinitely many \(n\in\mathbb{N}\) such that \(n^2+1\in\mathcal{C}\).
'''))

# 15 near-square analog of Golubew for cyclics
entries.append(entry(15, 'Near-square analog of Golubew for cyclics', dedent(r'''
For every \(m\in\mathbb{N}\), the interval \((m^3,(m+1)^3)\) contains at least one cyclic integer of the form \(n^2+1\). Moreover, for every \(m\in\mathbb{N}\), the interval \((m^4,(m+1)^4)\) contains at least two cyclic integers of the form \(n^2+1\), say \(n^2+1\) and \(n'^2+1\) with \(n<n'\).
'''))

# 16 counting Oppermann primes
entries.append(entry(16, 'Counting Oppermann primes', dedent(r'''
Let \(N_{\mathcal P}^{-}(n):=\#\{\,p\in\mathcal P: n^2-n\le p\le n^2\,\}\) and \(N_{\mathcal P}^{+}(n):=\#\{\,p\in\mathcal P: n^2\le p\le n^2+n\,\}\).
As \(n\to\infty\), \(N_{\mathcal P}^{-}(n)\sim N_{\mathcal P}^{+}(n)\sim \dfrac{n}{2\log n}.\)
'''))

# 17 k-fold Oppermann for primes
entries.append(entry(17, 'k-fold Oppermann for primes', dedent(r'''
For every \(k\in\mathbb{N}\) there exists \(N(k)\) such that, for all \(n>N(k)\), both intervals \([n^2-n,n^2]\) and \([n^2,n^2+n]\) contain at least \(k\) primes.
'''))

# 19 Oppermann analog for cyclics
entries.append(entry(19, 'Oppermann analog for cyclics', dedent(r'''
For every integer \(n>1\), there exist \(c,c'\in\mathcal{C}\) such that
\[n^2-n<c<n^2<c'<n^2+n.\]
Moreover, as \(n\to\infty\),
\[
N_{\mathcal C}^{-}(n)\sim \frac{n}{e^{\gamma}\,\log\log\log n}\!\left(1-\frac{\gamma}{\log\log\log n}\right),\qquad
N_{\mathcal C}^{+}(n)\sim \frac{n}{e^{\gamma}\,\log\log\log n}\!\left(1-\frac{\gamma}{\log\log\log n}\right).
\]
'''), extra_defs=[defs_oppermann_counts()]))

# 20 k-fold Oppermann for cyclics
entries.append(entry(20, 'k-fold Oppermann for cyclics', dedent(r'''
For every \(k\in\mathbb{N}\) there exists \(N(k)\) such that, for all \(n>N(k)\), both intervals \([n^2-n,n^2]\) and \([n^2,n^2+n]\) contain at least \(k\) cyclic integers.
'''))

# 22 k-fold Brocard for primes
entries.append(entry(22, 'k-fold Brocard for primes', dedent(r'''
There exists a function \(B:\mathbb{N}\to\mathbb{N}\) such that, for every \(k\in\mathbb{N}\) and all \(n\ge B(k)\), the interval \([n^2,(n+1)^2]\) contains at least \(k\) primes. Empirically, \(B(4)=2,\,B(5)=2,\,B(6)=3,\,B(7)=B(8)=B(9)=5,\,B(10)=B(11)=7,\,B(12)=\cdots=B(16)=10,\,B(17)=\cdots=B(20)=13\).
'''), extra_defs=[defs_brocard()]))

# 23 Brocard analog for cyclics
entries.append(entry(23, 'Brocard analog for cyclics', dedent(r'''
For every integer \(n>2\), the open interval \((c_n^2, c_{n+1}^2)\) contains at least six cyclic integers.
'''))

# 24 k-fold Brocard analog for cyclics
entries.append(entry(24, 'k-fold Brocard analog for cyclics', dedent(r'''
There exists a function \(C:\mathbb{N}\to\mathbb{N}\) such that, for every \(k\in\mathbb{N}\) and all \(n\ge C(k)\), the open interval \((c_n^2, c_{n+1}^2)\) contains at least \(k\) cyclic integers.
'''), extra_defs=[defs_brocard()]))

# 25 Schinzel P1 analog for cyclics
entries.append(entry(25, 'Schinzel P1 analog for cyclics', dedent(r'''
For every \(n\in\mathbb{N}\),
\[ c_{n+1} \le c_n + \sqrt{c_n},\]
with the exceptional cases \(c_3=3\), \(c_5=7\), \(c_{11}=23\).
'''))

# 26 Schinzel log^2 analog for cyclics
entries.append(entry(26, 'Schinzel log^2 analog for cyclics', dedent(r'''
For every \(n\in\mathbb{N}\),
\[ c_{n+1} \le c_n + (\log c_n)^2,\]
with the exceptional cases \(c_1=1\), \(c_2=2\), \(c_3=3\), \(c_5=7\).
'''))

# 27 Schinzel 2*log analog for cyclics
entries.append(entry(27, 'Schinzel 2·log analog for cyclics', dedent(r'''
For every \(n\in\mathbb{N}\),
\[ c_{n+1} \le c_n + 2\log c_n,\]
with the exceptional cases \(c_1=1\), \(c_5=7\).
'''))

# 28 number of twin primes between consecutive cubes
entries.append(entry(28, 'Twin primes between consecutive cubes', dedent(r'''
Let a pair of consecutive primes \((p_m,p_{m+1})\) be called twin if \(p_{m+1}-p_m=2\). For every \(n\in\mathbb{N}\), the number of twin prime pairs with \(n^3<p_m<p_{m+1}\le (n+1)^3\) is at least two. More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) such pairs.
'''))

# 29 cousin primes between cubes
entries.append(entry(29, 'Cousin primes between consecutive cubes', dedent(r'''
Let a pair of consecutive primes \((p_m,p_{m+1})\) be called cousin if \(p_{m+1}-p_m=4\). For all \(n>1\), the number of cousin prime pairs with \(n^3<p_m<p_{m+1}\le (n+1)^3\) is at least two. More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) such pairs.
'''))

# 30 sexy primes between cubes
entries.append(entry(30, 'Sexy primes between consecutive cubes', dedent(r'''
Let a pair of consecutive primes \((p_m,p_{m+1})\) be called sexy if \(p_{m+1}-p_m=6\). For all \(n>2\), the number of sexy prime pairs with \(n^3<p_m<p_{m+1}\le (n+1)^3\) is at least two. More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) such pairs.
'''))

# 31 asymptotic counts primes between cubes
entries.append(entry(31, 'Asymptotic k-fold primes between cubes', dedent(r'''
As \(n\to\infty\), the numbers of twin/cousin/sexy prime pairs between \(n^3\) and \((n+1)^3\) are asymptotic to regularly varying functions of \(n\) with indices in \((3/2,2]\). In particular, the indices for twin and cousin primes are equal.
''')))

# 32-34 twin/cousin/sexy cyclics between cubes
entries.append(entry(32, 'Twin cyclics between consecutive cubes', defs_cubes_pairs('cyclics',2)+"\n"+dedent(r'''
For every \(n\in\mathbb{N}\), there are at least two twin cyclic pairs between \(n^3\) and \((n+1)^3\). More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) twin cyclic pairs between \(n^3\) and \((n+1)^3\).
''')))
entries.append(entry(33, 'Cousin cyclics between consecutive cubes', defs_cubes_pairs('cyclics',4)+"\n"+dedent(r'''
For all \(n>1\), there is at least one cousin cyclic pair between \(n^3\) and \((n+1)^3\). More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) cousin cyclic pairs between \(n^3\) and \((n+1)^3\).
''')))
entries.append(entry(34, 'Sexy cyclics between consecutive cubes', defs_cubes_pairs('cyclics',6)+"\n"+dedent(r'''
For all \(n\ge 5\), there are at least two sexy cyclic pairs between \(n^3\) and \((n+1)^3\). More generally, for each \(k\in\mathbb{N}\), there exists \(N(k)\) such that for all \(n\ge N(k)\), there are at least \(k\) sexy cyclic pairs between \(n^3\) and \((n+1)^3\).
''')))

# 35 asymptotic counts cyclics between cubes
entries.append(entry(35, 'Asymptotic k-fold cyclics between cubes', dedent(r'''
As \(n\to\infty\), the numbers of twin/cousin/sexy cyclic pairs between \(n^3\) and \((n+1)^3\) are asymptotic to regularly varying functions of \(n\) with indices in \([1,5/2]\).
'''))

# 36 infinitely many SG cyclics
entries.append(entry(36, 'Infinitely many SG cyclics', dedent(r'''
There exist infinitely many Sophie Germain cyclics, i.e., infinitely many \(c\in\mathcal{C}\) with \(2c+1\in\mathcal{C}\).
'''), extra_defs=[defs_SG()]))

# 37 SG cyclics mod 3
entries.append(entry(37, 'SG cyclics modulo 3', dedent(r'''
Let \(a_j(x):=\#\{\,\sigma\le x: \sigma\equiv j\pmod 3\,\}\) for \(j\in\{1,2,3\}\). As \(x\to\infty\), each \(a_j(x)\to\infty\) and
\[\lim_{x\to\infty}\frac{a_1(x)}{C_{\mathrm{SG}}(x)}=\lim_{x\to\infty}\frac{a_3(x)}{C_{\mathrm{SG}}(x)}.\]
'''), extra_defs=[defs_SG()]))

# 38 Desboves analog for SG cyclics
entries.append(entry(38, 'Desboves analog for SG cyclics', dedent(r'''
For every \(n\in\mathbb{N}\), there exist at least two SG cyclics in the open interval \((n^2,(n+1)^2)\).
'''), extra_defs=[defs_SG()]))

# 39-43 Firoozbakht analogs
entries.append(entry(39, 'Firoozbakht analog for cyclics 1', dedent(r'''
For every \(n\in\mathbb{N}\) with \(n\notin\{1,2,3,5\}\),
\[c_{n+1}^{\,1/(n+1)}<c_{n}^{\,1/n}.\]
The four exceptional cases correspond to \(1<2^{1/2}<3^{1/3}<5^{1/4}<7^{1/5}<11^{1/6}\).
''')))

entries.append(entry(40, 'Firoozbakht analog for cyclics 2', dedent(r'''
For every integer \(n>1\),
\[c_{n}^{\,1/(n-1)}>c_{n+1}^{\,1/n},\]
interpreting \(c_1^{1/0}:=1\), so the only exception is \(c_1=1<c_2=2\).
''')))

entries.append(entry(41, 'Firoozbakht analog for cyclics 3', dedent(r'''
For every \(k\in\mathbb{N}\) there exists \(N(k)\) such that, for all \(n>N(k)\),
\[c_{n}^{\,1/(n+k)}>c_{n+1}^{\,1/(n+k+1)}.\]
In particular, \(N(1)=N(2)=5\) and \(N(3)=N(4)=11\).
''')))

entries.append(entry(42, 'Firoozbakht analog for cyclics 4', dedent(r'''
For \(k\in\{0\}\cup\mathbb{N}\), define \(A_{\mathcal{C}}(k):=\max_{n\ge 1} c_{n}^{\,1/(n+k)}\). Then
\(A_{\mathcal{C}}(0)\approx1.4953>A_{\mathcal{C}}(1)\approx1.4085>A_{\mathcal{C}}(2)\approx1.3495>A_{\mathcal{C}}(3)\approx1.3053>A_{\mathcal{C}}(4)\approx1.2710>\cdots\).
''')))

entries.append(entry(43, 'Firoozbakht analog for SG cyclics', dedent(r'''
Let \((\sigma_n)\) be the increasing sequence of SG cyclics. For every \(n\notin\{1,2,3,5\}\),
\[\sigma_{n+1}^{\,1/(n+1)}<\sigma_{n}^{\,1/n}.\]
The four exceptional cases are as in Conjecture 39.
'''), extra_defs=[defs_SG()]))

# 44 Andrica analog for cyclics
entries.append(entry(44, 'Andrica analog for cyclics', dedent(r'''
For all \(n\in\mathbb{N}\),
\[\sqrt{c_{n+1}}-\sqrt{c_n}<1.\]
''')))

# 45 generalized analog for primes
entries.append(entry(45, 'Generalized analog for primes', dedent(r'''
For every real \(t\in(0,1/2]\),
\[\lim_{n\to\infty}\bigl(p_{n+1}^{t}-p_n^{t}\bigr)=0.\]
''')))

# 46 generalized analog for cyclics
entries.append(entry(46, 'Generalized analog for cyclics', dedent(r'''
For every real \(t\in(0,1/2]\),
\[\lim_{n\to\infty}\bigl(c_{n+1}^{t}-c_n^{t}\bigr)=0.\]
''')))

# 47 Visser analog for cyclics
entries.append(entry(47, 'Visser analog for cyclics', dedent(r'''
For every \(\varepsilon\in(0,1/2)\) there exists \(N(\varepsilon)\) such that, for all \(n>N(\varepsilon)\),
\[\sqrt{c_{n+1}}-\sqrt{c_n}<\varepsilon.\]
''')))

# 48 generalized KMSZ for primes
entries.append(entry(48, 'Generalized KMSZ for primes', dedent(r'''
For every integer \(k\in\mathbb{Z}\), there exists \(N(k)\) such that, for all \(n>N(k)\),
\[p_{n+1}-p_n<\sqrt{p_n}+k.\]
''')))

# 49 generalized KMSZ for cyclics
entries.append(entry(49, 'Generalized KMSZ for cyclics', dedent(r'''
For every integer \(k\in\mathbb{Z}\), there exists \(N(k)\) such that, for all \(n>N(k)\),
\[c_{n+1}-c_n<\sqrt{c_n}+k.\]
''')))

# 50 Carneiro analog for cyclics
entries.append(entry(50, 'Carneiro analog for cyclics', dedent(r'''
For every \(n\) with \(c_n>3\),
\[c_{n+1}-c_n<\sqrt{c_n\,\log c_n}.\]
''')))

# 51 Carneiro analog for SG cyclics
entries.append(entry(51, 'Carneiro analog for SG cyclics', dedent(r'''
For every \(n\) with \(\sigma_n>3\),
\[\sigma_{n+1}-\sigma_n<\sqrt{\sigma_n\,\log \sigma_n}.\]
'''), extra_defs=[defs_SG()]))

# 53 Dusart analog for cyclics
entries.append(entry(53, 'Dusart analog for cyclics', dedent(r'''
For all \(n>1\),
\[c_n>e^{\gamma}\,n\,\bigl(\log\log\log n+\log\log\log\log n\bigr).\]
''')))

# 55 Ishikawa analog for SG cyclics
entries.append(entry(55, 'Ishikawa analog for SG cyclics', dedent(r'''
For all \(n>2\),
\[\sigma_n+\sigma_{n+1}>\sigma_{n+2}.\]
'''), extra_defs=[defs_SG()]))

# 56 sum-3-versus-sum-2 analog for cyclics
entries.append(entry(56, 'sum-3-versus-sum-2 analog for cyclics', dedent(r'''
For all \(n>9\),
\[c_n+c_{n+1}+c_{n+2}>c_{n+3}+c_{n+4}.\]
''')))

# 57 Dusart–Mandl analog for cyclics
entries.append(entry(57, 'Dusart–Mandl analog for cyclics', dedent(r'''
For all \(n>5\),
\[\frac{c_1+c_2+\cdots+c_n}{n}<\frac{c_n}{2}.\]
''')))

# 58 Dusart–Mandl analog for SG cyclics
entries.append(entry(58, 'Dusart–Mandl analog for SG cyclics', dedent(r'''
For all \(n>5\),
\[\frac{\sigma_1+\sigma_2+\cdots+\sigma_n}{n}<\frac{\sigma_n}{2}.\]
'''), extra_defs=[defs_SG()]))

# 62 Proth-Gilbreath analog for cyclics
entries.append(entry(62, 'Proth–Gilbreath analog for cyclics', dedent(r'''
Form the SADS from the sequence of cyclic integers with \(c_1=1\) omitted. Then the first term of every successor sequence equals 1; that is, if \(a^{(0)}_n=c_{n+1}\) for \(n\ge 1\) and \(a^{(k)}_n=\lvert a^{(k-1)}_{n+1}-a^{(k-1)}_{n}\rvert\), then \(a^{(k)}_1=1\) for all \(k\ge 1\).
'''), extra_defs=[defs_SADS()]))

# 63 Proth-Gilbreath analog for SG cyclics
entries.append(entry(63, 'Proth–Gilbreath analog for SG cyclics', dedent(r'''
Form the SADS from the sequence \((\sigma_n)\) of SG cyclics with \(\sigma_1=1\) omitted. Then the first term of every successor sequence equals 1.
'''), extra_defs=[defs_SADS(), defs_SG()]))

# 64 Hardy–Littlewood analog for SG primes
entries.append(entry(64, 'Hardy–Littlewood analog for SG primes', dedent(r'''
Let \(\pi_{\mathrm{SG}}(x)\) denote the counting function of SG primes. Then, for all integers \(2\le m\le n\),
\[\pi_{\mathrm{SG}}(m+n)\le \pi_{\mathrm{SG}}(m)+\pi_{\mathrm{SG}}(n).\]
'''), extra_defs=[defs_SG()]))

# 65 Hardy–Littlewood analog for cyclics
entries.append(entry(65, 'Hardy–Littlewood analog for cyclics', dedent(r'''
Let \(C(x)=\#\{\,c\in\mathcal{C}: c\le x\,\}\) be the counting function of cyclic integers. For all integers \(1\le m\le n\),
\[C(m+n)\le C(m)+C(n).\]
'''), extra_defs=[defs_counting_C()]))

# 66 Hardy–Littlewood analog for SG cyclics
entries.append(entry(66, 'Hardy–Littlewood analog for SG cyclics', dedent(r'''
Let \(C_{\mathrm{SG}}(x)\) be the counting function of SG cyclics. For all integers \(1\le m\le n\),
\[C_{\mathrm{SG}}(m+n)\le C_{\mathrm{SG}}(m)+C_{\mathrm{SG}}(n).\]
'''), extra_defs=[defs_SG()]))

# Exclusions: 9, 52, 54, 59, 60, 61
include_nums = {2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,19,20,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,53,55,56,57,58,62,63,64,65,66}
filtered = [e for e in entries if int(e.split('Conjecture ')[1].split(' ')[0]) in include_nums]

content = '[\n' + ',\n\n'.join(filtered) + '\n]\n'
open('open_problems/list.txt','w',encoding='utf-8').write(content)
print('Wrote', len(filtered), 'entries to open_problems/list.txt')
