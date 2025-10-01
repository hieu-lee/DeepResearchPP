**Proof.** Let \(\mathcal C=\{m\in\mathbb N:\gcd(m,\varphi(m))=1\}\) be the set of cyclic integers, \((c_n)_{n\ge1}\) its increasing enumeration, and \(C(x)=\#\{m\le x:m\in\mathcal C\}\). For \(x>e^e\) write \(L=\log_3 x=\log\log\log x\), and let \(\gamma\) be Euler’s constant. We also adopt the following standard convention for the iterated logarithm: for \(t>e\) put \(\log_3 t=\log\log\log t\), while for \(1<t\le e\) set \(\log_3 t:=-\infty\). With this convention \(\log_3\) is increasing on \((e,\infty)\) and nonpositive on \((e,e^e]\).

There exist absolute constants \(L_*>0\) and \(B>0\) such that for all \(x\) with \(L\ge L_*\),
$$
C(x)=\frac{e^{\! -\gamma}x}{L}\Bigl(1-\frac{\gamma}{L}+\frac{a}{L^2}+R_3(L)\Bigr),\qquad a:=\gamma^2+\frac{\pi^2}{12},\quad |R_3(L)|\le\frac{B}{L^3}.
\tag{1}
$$
Set
$$
L_1\ :=\ \max\Bigl\{L_*,\ \frac{2a}{\gamma},\ \sqrt{\frac{2B}{\gamma}}\Bigr\}.
\tag{2}
$$
Then for \(L\ge L_1\) one has \(\dfrac{a}{L^2}\le\dfrac{\gamma}{2L}\) and \(\dfrac{|R_3(L)|}{\phantom{|}}\le\dfrac{\gamma}{2L}\), whence
$$
C(x)\ \le\ \frac{e^{\! -\gamma}x}{L}\qquad(L\ge L_1).
\tag{3}
$$

Fix \(n>1\). Define, for \(n>e^e\),
$$
x_0:=e^{\gamma}n\,\log_3 n,\qquad L_0:=\log_3 x_0,\qquad c:=\log_3 n.
$$
Since \(c\to\infty\) as \(n\to\infty\), there exists \(n_1\ge 3\) such that for all \(n\ge n_1\),
$$
c\ >\ e^{\! -\gamma}\quad\text{and}\quad c\ \ge\ L_1.
\tag{4}
$$
For such \(n\), \(e^{\gamma}c>1\) so \(x_0=e^{\gamma}nc>n\), and since \(\log_3\) is increasing on \((e,\infty)\),
$$
L_0=\log_3 x_0\ >\ \log_3 n\ =\ c\ \ge\ L_1.
\tag{5}
$$
Applying (3) at \(x=x_0\) and using (5) yields
$$
C(x_0)\ \le\ \frac{e^{\! -\gamma}x_0}{L_0}
\,=\, n\cdot\frac{\log_3 n}{L_0}
\,=\, n\cdot\frac{c}{L_0}
\,<\, n,
$$
so at most \(n-1\) cyclic integers are \(\le x_0\). Therefore
$$
 c_n\,>\,x_0\,=\,e^{\gamma}n\,\log_3 n\qquad(n\ge n_1).
\tag{6}
$$
Thus the inequality holds for all sufficiently large \(n\).

It remains to handle finitely many \(n\).

(1) For \(3\le n\le \lfloor e^e\rfloor\) the real triple logarithm is defined and negative, hence
$$
 e^{\gamma}n\,\log_3 n\ \le\ 0\ <\ c_n,
$$
whence \(c_n>e^{\gamma}n\,\log_3 n\) throughout this range.

(2) A uniform lower bound for all \(n\ge 4\) is
$$
 c_n\,\ge\,2n-5.
\tag{7}
$$
Indeed, among \(2,4,\dots,2n-6\) exactly one even integer is cyclic (namely \(2\)); every even \(m>2\) has \(2\mid m\) and \(2\mid\varphi(m)\), hence \(\gcd(m,\varphi(m))\ge2\). Thus there are at least \(n-4\) noncyclic integers \(\le 2n-6\), so
$$
C(2n-6)\le (2n-6)-(n-4)=n-2,
$$
which implies \(c_n\ge (2n-6)+1=2n-5\).

Consequently, for every \(n\ge 6\),
$$
 c_n\,\ge\,2n-5\ >\ e^{\gamma}n\,t\quad\text{whenever}\quad t\ <\ \frac{2-5/n}{e^{\gamma}}.
\tag{8}
$$
Specializing \(t=\log_3 n\) (defined and increasing for \(n>e\)), we ensure the strict inequality in (8) uniformly on a finite interval by fixing
$$
N_0\ :=\ \max\Bigl\{6,\ \lfloor e^e\rfloor+1,\ \big\lfloor\exp\!\exp\!\exp\!\big(\tfrac{2-5/6}{e^{\gamma}}\big)\big\rfloor-1\Bigr\}.
$$
Then for every \(\lfloor e^e\rfloor+1\le n\le N_0\) one has
$$
 \log_3 n\ \le\ \log_3 N_0\ <\ \frac{2-5/6}{e^{\gamma}}\ \le\ \frac{2-5/n}{e^{\gamma}},
$$
so by (8) we get the strict bound
$$
 c_n\ >\ e^{\gamma}n\,\log_3 n\qquad(\lfloor e^e\rfloor+1\le n\le N_0).
$$
Finally, enlarge \(n_1\) from (4) if necessary so that \(n_1\ge\max\{N_0,3\}\). Combining the cases (1), the strict bound for \(\lfloor e^e\rfloor+1\le n\le N_0\), and (6) for all \(n\ge n_1\), we obtain
$$
 c_n\ >\ e^{\gamma}\,n\,\log_3 n\qquad\text{for all }n\ge 3.
$$
For \(n=2\) our convention gives \(\log_3 2=-\infty\), hence \(e^{\gamma}\cdot 2\cdot\log_3 2=-\infty<c_2=2\). Therefore
$$
 c_n\ >\ e^{\gamma}\,n\,\log_3 n\qquad\text{for all }n>1.
$$
∎