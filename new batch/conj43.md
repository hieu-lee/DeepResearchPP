**Proof.** Fix $\varepsilon\in(0,\tfrac12)$ and let $x$ be large. Put
$$
 h:=\varepsilon\sqrt x,\qquad z:=\exp\big((\log x)^{1/2}\big),\qquad V(z):=\prod_{p\le z}\Bigl(1-\tfrac1p\Bigr)\sim\frac{e^{-\gamma}}{\log z}.
$$
Let $I:=(x,x+h]$, $P^-(n)$ denote the least prime factor of $n$ (with $P^-(1)=\infty$), and
$$
C(x):=\#\{n\le x: \gcd(n,\varphi(n))=1\}.
$$
We prove that, uniformly for large $x$,
$$
C(x+h)-C(x)\ge (e^{-\gamma}+o(1))\,\frac{h}{(\log x)^{1/2}},\tag{A}
$$
which implies the desired bound for $\sqrt{c_{n+1}}-\sqrt{c_n}$.

1) $z$-rough integers in $I$. Let
$$
S_0:=\#\{n\in I: P^-(n)>z\}.
$$
For squarefree $d$, write $A_d:=\#\{n\in I: d\mid n\}=h/d+r_d$ with $|r_d|\le 1$. Apply the effective fundamental lemma of the linear sieve (dimension $1$) against the set of sifting primes $\{p\le z\}$ with level
$$
D:=\frac{h}{(\log z)^B}\qquad(B>2\ \text{fixed}).
$$
Let $u:=\frac{\log D}{\log z}$. Since $\log z=(\log x)^{1/2}$ and $\log D=\tfrac12\log x+O(\log\log x)$, we have $u\to\infty$. The fundamental lemma furnishes lower-sieve weights giving
$$
S_0\ge h\,V(z)\bigl(1+O(e^{-u})\bigr)-\sum_{d\le D}|r_d|\ge h\,V(z)\Bigl(1+O(e^{-u})-O\Bigl(\frac{D}{h\,V(z)}\Bigr)\Bigr).
$$
Because $\sum_{d\le D}|r_d|\le D$, $e^{-u}=o(1)$ and
$$
\frac{D}{h\,V(z)}\asymp\frac{(\log z)^{-B}}{(\log z)^{-1}}=(\log z)^{1-B}=o(1),
$$
we obtain, uniformly for large $x$,
$$
S_0\ge h\,V(z)\,(1+o(1)).\tag{1}
$$

2) Removing non-squarefree integers. If $p^2\mid n$ then $p\mid\varphi(n)$; hence such $n$ are not cyclic. The contribution of squareful $n\in I$ with $P^-(n)>z$ satisfies
$$
S_1\le \sum_{z<p\le \sqrt{x+h}}\Bigl(\Big\lfloor\frac{h}{p^2}\Big\rfloor+1\Bigr)
 \ll h\sum_{p>z}\frac1{p^2}+\pi(\sqrt{x+h})
 \ll \frac{h}{z}+\frac{\sqrt x}{\log x}=o\!\Big(\frac{h}{\log z}\Big).\tag{2}
$$
Here we used $\sum_{p>z}1/p^2\ll 1/z$ and $\log z=(\log x)^{1/2}$.

3) Excluding collision pairs $q\equiv1\pmod p$. For squarefree $n$ with $P^-(n)>z$, the condition $\gcd(n,\varphi(n))>1$ is equivalent to the existence of primes $p,q\mid n$ with $q\equiv1\pmod p$. Let $S_{\mathrm{col}}$ count $n\in I$ with $P^-(n)>z$ for which such a pair exists. Write $S_{\mathrm{col}}=S_{\mathrm{col}}^{\le h}+S_{\mathrm{col}}^{>h}$ according to $pq\le h$ or $pq>h$.

3a) Density range $pq\le h$. Using partial summation together with Brun–Titchmarsh for $\pi(\cdot; p,1)$, we have uniformly for $p\le\sqrt h$ that
$$
\sum_{\substack{q\le T\\ q\equiv1\ (\mathrm{mod}\ p)}}\frac1q\ll \frac{\log\log T}{\varphi(p)}\ll \frac{\log\log T}{p}.
$$
Therefore
$$
S_{\mathrm{col}}^{\le h}\le h\sum_{\substack{z<p\le\sqrt h}}\frac1p\sum_{\substack{z<q\le h/p\\ q\equiv1\ (\mathrm{mod}\ p)}}\frac1q
\ll h\sum_{z<p\le\sqrt h}\frac{\log\log(h/p)}{p^2}
\ll h\,\frac{\log\log x}{z}=o\!\Big(\frac{h}{\log z}\Big).\tag{3}
$$

3b) Unit range $pq>h$. Each $n\in I$ counted here admits a representation $n=mpq$ with $m\ge1$, $p,q$ prime $>z$, $q\equiv1\pmod p$. Put
$$
 p_0:=\sqrt h\,\log x=\sqrt{\varepsilon}\,x^{1/4}\,\log x.
$$
Split the contribution according to $p\le p_0$ and $p>p_0$.

– Range $p>p_0$. Parameterize $q\equiv1\pmod p$ by $q=kp+1$ with $k\ge1$. The condition $mpq\in I$ is equivalent to
$$
 x< m\,p\,(k p+1)\le x+h.
$$
For fixed $(m,k)$ this constrains $p$ to lie in an interval $J_{m,k}$ of length
$$
|J_{m,k}|=\frac{\sqrt{1+4k(x+h)/m}-\sqrt{1+4k x/m}}{2k}
\le \frac{h}{\sqrt{m k x}}<\frac{h}{\sqrt x}=\varepsilon<1.
$$
Hence each $J_{m,k}$ contains at most one integer. Moreover, $J_{m,k}\cap(p_0,\infty)\ne\varnothing$ only if $k\ll (x+h)/(m p_0^2)$. Summing over $m\le (x+h)/p_0^2$ and $k$ gives
$$
T_2\ll \sum_{m\le (x+h)/p_0^2}\frac{x}{m p_0^2}\ll \frac{x}{p_0^2}\,\log\!\Big(\frac{x}{p_0^2}\Big)
=\frac{\sqrt x}{\varepsilon\,\log x}\,(1+o(1)).\tag{4}
$$
Because $\log z=(\log x)^{1/2}$, we have $T_2=o\!\big(h/\log z\big)$.

– Range $z<p\le p_0$. For fixed such $p$ and a prime $q\equiv1\pmod p$, the condition $mpq\in I$ determines $m$ uniquely (if it exists), since the interval $\big(x/(pq),(x+h)/(pq]\big)$ has length $h/(pq)<1$. Hence summing over $m$ first and then over $q$ yields
$$
T_1\le \sum_{z<p\le p_0}\#\Big\{q\le \frac{x+h}{p}:\ q\in\mathcal P,\ q\equiv1\ (\mathrm{mod}\ p)\Big\}
=\sum_{z<p\le p_0}\pi\!\Big(\frac{x+h}{p};p,1\Big).
$$
By Brun–Titchmarsh (valid since $p^2\ll x$ for $p\le p_0$),
$$
\pi\!\Big(\frac{x+h}{p};p,1\Big)\ll \frac{(x+h)/p}{\varphi(p)\,\log((x+h)/p^2)}\ll \frac{x}{p^2\,\log x}.
$$
Therefore
$$
T_1\ll \frac{x}{\log x}\sum_{p>z}\frac1{p^2}\ll \frac{x}{z\,\log x}=o\!\Big(\frac{h}{\log z}\Big).\tag{5}
$$
Combining (4) and (5),
$$
S_{\mathrm{col}}^{>h}=T_1+T_2=o\!\Big(\frac{h}{\log z}\Big).\tag{6}
$$

Collecting (3) and (6), we obtain
$$
S_{\mathrm{col}}=S_{\mathrm{col}}^{\le h}+S_{\mathrm{col}}^{>h}=o\!\Big(\frac{h}{\log z}\Big).\tag{7}
$$

4) Cyclic integers in $I$. By (1), (2), (7),
$$
C(x+h)-C(x)\ge S_0-S_1-S_{\mathrm{col}}=h\,V(z)\,(1+o(1)).
$$
Since $V(z)\sim e^{-\gamma}/\log z$ and $\log z=(\log x)^{1/2}$, we obtain uniformly
$$
C(x+h)-C(x)\ge (e^{-\gamma}+o(1))\,\frac{h}{(\log x)^{1/2}}\qquad (x\to\infty).
$$
Because $(\log x)^{1/2}=o(\sqrt x)$, the right-hand side tends to $+\infty$. Hence for each fixed $\varepsilon\in(0,\tfrac12)$ there exists $x_0(\varepsilon)$ such that for all $x\ge x_0(\varepsilon)$,
$$
C\bigl(x+\varepsilon\sqrt x\bigr)-C(x)\ge 1.
$$

5) Consecutive cyclic integers. Apply the previous assertion with $x=c_n$. For all $n$ with $c_n\ge x_0(\varepsilon)$, the interval $(c_n,\,c_n+\varepsilon\sqrt{c_n}]$ contains some cyclic integer, hence by minimality of $c_{n+1}$,
$$
 c_{n+1}\le c_n+\varepsilon\sqrt{c_n}.
$$
Therefore
$$
\sqrt{c_{n+1}}-\sqrt{c_n}=\frac{c_{n+1}-c_n}{\sqrt{c_{n+1}}+\sqrt{c_n}}\le \frac{\varepsilon\sqrt{c_n}}{\sqrt{c_{n+1}}+\sqrt{c_n}}\le \varepsilon.
$$
Thus there exists $N(\varepsilon)$ such that for all $n\ge N(\varepsilon)$, $\sqrt{c_{n+1}}-\sqrt{c_n}<\varepsilon$. ∎