**Claim (k-fold Oppermann for cyclic integers).** For every fixed $k\in\mathbb N$ there exists $N(k)$ such that for all $n\ge N(k)$, each of the intervals $[n^2-n,n^2]$ and $[n^2,n^2+n]$ contains at least $k$ integers $m$ with $\gcd(m,\varphi(m))=1$.

**Proof.** Put $X:=n^2$ and $H:=n=\sqrt X$. It suffices to prove that there exists $X_0$ such that for all $X\ge X_0$ and for each of the two intervals $I\in\{[X-H,X],\,[X,X+H]\}$ one has
$$
\#(I\cap\mathcal C)\ \gg\ \frac{H\,\log\log\log X}{\log X},
$$
with an absolute implied constant; this clearly implies the claim for any fixed $k$ since $H/\log X\to\infty$.

Fix $A\ge2$ and let $L:=(\log X)^A$. Write $\mathcal P_0:=\{p\in\mathcal P:3\le p\le L\}$. For $p\in\mathcal P_0$ define
$$
 y_p:=\frac{X}{p},\qquad \Delta_p:=\frac{H}{p},\qquad J^+(p):=[y_p,\,y_p+\Delta_p],\qquad J^-(p):=[y_p-\Delta_p,\,y_p].
$$
For $I=[X,X+H]$ use the right windows $J(p):=J^+(p)$; for $I=[X-H,X]$ use the left windows $J(p):=J^-(p)$. In both cases, if $r\in J(p)$ then $m:=pr\in I$. For $X$ large, the windows are disjoint in the sense that for every real $r$,
$$
W(r):=\#\{p\in\mathcal P_0: r\in J(p)\}\in\{0,1\}.
$$
Indeed, if $r\in J(p)$ then $pr\in[X-H,X+H]$, so necessarily
$$
p\in\left(\frac{X-H}{r},\,\frac{X+H}{r}\right),
$$
an interval of length $\ll H/r\le H/(X/L-\Delta_L)\ll L/\sqrt X<1$ for large $X$, whence uniqueness of $p$.

Set $U:=\bigcup_{p\in\mathcal P_0} J(p)$. Then
$$
|U|=\sum_{p\in\mathcal P_0}|J(p)|=\sum_{p\le L}\frac{H}{p}
 = H\sum_{p\le L}\frac1p\sim H\log\log L\asymp H\log\log\log X.\tag{1}
$$
We first show that $U$ contains many primes, and then exclude a single forbidden residue class inside each window to ensure cyclicity.

Lemma 1 (Many primes in $U$). For all sufficiently large $X$,
$$
\#\bigl(U\cap\mathcal P\bigr)\ \gg\ \frac{|U|}{\log X}\ \asymp\ \frac{H\,\log\log\log X}{\log X}.\tag{2}
$$

Proof. Let $\Lambda$ be the von Mangoldt function and $\psi(x):=\sum_{n\le x}\Lambda(n)$. By the prime number theorem in the form $\psi(t)=t+O\bigl(t\,e^{-c\sqrt{\log t}}\bigr)$ for some absolute $c>0$, we have, for each window $J(p)=[\alpha,\beta]$ with $\beta-\alpha=\Delta_p$ and $\alpha\asymp X/p$,
$$
\sum_{\alpha<n\le\beta}\Lambda(n)
= \psi(\beta)-\psi(\alpha)
= \Delta_p + O\!\left(\alpha\,e^{-c\sqrt{\log \alpha}}\right) + O(1).
$$
Summing over the disjoint windows and using $\alpha\ge X/L$ and $\#\mathcal P_0=\pi(L)$,
$$
\sum_{n\in U\cap\mathbb Z}\Lambda(n)
= \sum_{p\le L}\Delta_p + O\!\left(\sum_{p\le L}\frac{X}{p}\,e^{-c\sqrt{\log(X/p)}}\right)+O\bigl(\pi(L)\bigr)
= |U| + o(|U|).
$$
Indeed, uniformly for $p\le L=(\log X)^A$ we have $e^{-c\sqrt{\log(X/p)}}\le e^{-c'\sqrt{\log X}}$ for some $c'>0$, so the middle error is $\ll X e^{-c'\sqrt{\log X}}\sum_{p\le L}\tfrac1p\ll X e^{-c'\sqrt{\log X}}\log\log L=o(|U|)$, and $\pi(L)=o(|U|)$ since $|U|\asymp \sqrt X\log\log\log X$ while $\pi(L)\asymp L/\log L=(\log X)^A/\log\log X$.

Prime powers contribute negligibly: the number of prime squares in a single window $J(p)$ is $\ll \Delta_p/\sqrt{y_p}= (H/p)/\sqrt{X/p}=(H/\sqrt X)p^{-1/2}$, so over all $p\le L$ there are $\ll \sum p^{-1/2}\ll \sqrt L/\log L$ prime squares in $U$; higher prime powers contribute even less. Hence
$$
\sum_{\substack{n\in U\cap\mathbb Z\\ n=\text{prime power},\,\nu\ge2}}\Lambda(n)\ \ll\ (\log X)\Bigl(\frac{\sqrt L}{\log L}+\pi(L)\Bigr)
= o(|U|).
$$
Therefore
$$
\sum_{\substack{r\in U\cap\mathcal P}}\log r
= \sum_{n\in U\cap\mathbb Z}\Lambda(n) - o(|U|)
= |U|+o(|U|).
$$
For both choices of $I$ and all $r\in U$ we have $r\le X$ (indeed $r\le y_p+\Delta_p\le (X+H)/3\le X$ for $p\ge3$), hence $\log r\le\log X$. Consequently,
$$
\#(U\cap\mathcal P)\ \ge\ \frac{\sum_{r\in U\cap\mathcal P}\log r}{\log X}
\ =\ \frac{|U|}{\log X}+o\!\left(\frac{|U|}{\log X}\right),
$$
which is (2). $\square$

Lemma 2 (Excluding $1\pmod p$ in its own window). For all large $X$,
$$
\sum_{p\in\mathcal P_0}\#\{r\in J(p)\cap\mathcal P: r\equiv1\ (\bmod\ p)\}
\ \ll\ \frac{H}{\log X}.\tag{3}
$$

Proof. For fixed $p\in\mathcal P_0$, the Brun–Titchmarsh inequality on the short interval $J(p)$ gives
$$
\#\{r\in J(p)\cap\mathcal P: r\equiv1\ (\bmod\ p)\}
\ \le\ \frac{2|J(p)|}{\varphi(p)\,\log(|J(p)|/p)}
\ =\ \frac{2(H/p)}{(p-1)\,\log(H/p^2)}.
$$
Since $p\le L=(\log X)^A$ and $H=\sqrt X$, one has $H/p^2\to\infty$ and $\log(H/p^2)\ge \tfrac12\log X-2\log L\sim \tfrac12\log X$. Summing over $p\in\mathcal P_0$ and using $\sum_{p\ge3}1/(p(p-1))<\infty$ yields (3). $\square$

We now produce cyclic integers. By Lemma 1 and (1),
$$
\#(U\cap\mathcal P)\ \gg\ \frac{|U|}{\log X}\ \asymp\ \frac{H\,\log\log\log X}{\log X}.
$$
By Lemma 2, at most $\ll H/\log X$ of these primes lie in the forbidden residue class $1\pmod p$ inside their unique window. Consequently,
$$
\#\Bigl\{r\in U\cap\mathcal P:\ \text{if }r\in J(p)\text{ then }r\not\equiv1\ (\bmod\ p)\Bigr\}
\ \gg\ \frac{H\,\log\log\log X}{\log X}.
$$
For each such prime $r$ there is a unique $p\in\mathcal P_0$ with $r\in J(p)$; then $m:=pr\in I$, and $m$ is odd and squarefree with prime factors $p<r$. For squarefree $m=\prod p_i$, one has $\gcd(m,\varphi(m))=1$ if and only if for all distinct $i\ne j$ one has $p_j\not\equiv1\pmod{p_i}$. Here the only pair is $(p,r)$. We ensured $r\not\equiv1\pmod p$, while $p\not\equiv1\pmod r$ holds because $p<r$. Thus each such $r$ yields a distinct $m=pr\in I\cap\mathcal C$ (injectivity follows from the disjointness $W(r)\in\{0,1\}$).

Therefore, for each of the intervals $I\in\{[X-H,X],[X,X+H]\}$ we have
$$
\#(I\cap\mathcal C)\ \gg\ \frac{H\,\log\log\log X}{\log X}.
$$
Since $H/\log X\to\infty$, this lower bound exceeds any prescribed $k$ for all $X\ge X_0(k)$. Recalling $X=n^2$ and $H=n$ completes the proof. $\square$ ∎