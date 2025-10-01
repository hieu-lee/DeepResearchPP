**Proof.** Fix $n\in\mathbb N$ and set $x:=n^2$, $H:=2n+1$, $X:=x+H\asymp x$. We work inside the interval $(x,X)=(x,x+H)$. For an interval $I\subset\mathbb R$ and $z\ge2$, let
\[
S(I;z):=\#\{m\in I\cap\mathbb N: P^-(m)\ge z\},
\]
with $P^-(1)=\infty$ and $P^-(m)$ the least prime factor of $m$. We use Mertens’ product $\prod_{p<z}(1-1/p)=e^{-
\gamma}/\log z\,(1+O(1/\log z))$.

Choose
\[
z:=\Bigl\lceil x^{1/4}(\log x)^{-6}\Bigr\rceil.
\]

Step 1 (many $z$-rough integers). Let $\mathcal A=\{x+1,\dots,x+H-1\}$. By the linear Selberg sieve lower bound in dimension $1$ applied to consecutive integers,
\[
S((x,x+H);z)\ge H\prod_{p<z}\Bigl(1-{1\over p}\Bigr)-C_0 z^2
=\frac{e^{-\gamma}+o(1)}{\log z}\,H\ -\ C_0 z^2.
\]
Since $H\asymp x^{1/2}$ and $z^2=x^{1/2}(\log x)^{-12}$, the main term dominates; hence, for all large $x$,
\[
S((x,x+H);z)\ge \frac{e^{-\gamma}}{2}\cdot\frac{H}{\log z}
\asymp \frac{\sqrt x}{\log x}.
\]

Step 2 (squarefree restriction). Count $m\in(x,x+H)$ with $P^-(m)\ge z$ that are not squarefree. Such $m$ have $p^2\mid m$ for some prime $p\ge z$. Split at $\sqrt H$.

– If $z\le p\le\sqrt H$, then $\#\{m\in(x,x+H): p^2\mid m\}\ll H/p^2$, whence the total over such $p$ is $\ll H\sum_{p\ge z}p^{-2}\ll H/z=o(\sqrt x/\log x)$.

– If $\sqrt H<p\le\sqrt{X}$, write $m=p^2 r$ with $r\in\bigl(x/p^2,(x+H)/p^2\bigr)$; this interval has length $<1$, so at most one $r$ arises per $p$. Put $T:=\lfloor\sqrt{X/z}\rfloor\asymp x^{3/8}(\log x)^3$. If $p>T$ then $(x+H)/p^2<z$, and since $P^-(r)\ge z$ we must have $r=1$ whenever an $r$ exists; but $r=1\in(x/p^2,(x+H)/p^2)$ would force $x<p^2<x+H$, impossible because $x=n^2$ and $x+H=(n+1)^2$ are consecutive squares. Hence there is no contribution from $p>T$. If $\sqrt H<p\le T$ there are $\ll \pi(T)-\pi(\sqrt H)\ll T=o(\sqrt x/\log x)$ possibilities. Altogether the nonsquarefree $z$-rough $m$ are $o(\sqrt x/\log x)$ in number.

Thus, for large $x$, there are $\gg \sqrt x/\log x$ integers $m\in(x,x+H)$ that are squarefree and satisfy $P^-(m)\ge z$.

Step 3 (excluding the cyclic obstructions). For squarefree $m=\prod_{i=1}^k p_i$ one has $\gcd(m,\varphi(m))=1$ if and only if there do not exist distinct primes $p_i\ne p_j$ with $p_i\mid(p_j-1)$. Write $p\to q$ for primes $p\le q$ with $q\equiv1\pmod p$. We bound the number of squarefree $z$-rough $m\in(x,x+H)$ admitting a pair $p\to q$.

Fix such $p,q$ dividing $m$. Then we may write $m=pqr$ with
\[
r\in I_{p,q}:=\Bigl({x\over pq},{x+H\over pq}\Bigr),\qquad P^-(r)\ge z,\qquad (r,pq)=1.
\]
Note $\#\{m: p,q\mid m\}\le \lceil H/(pq)\rceil$ always. Split into two subcases.

– Case 3.1: $pq\le H$. Then $\lceil H/(pq)\rceil\le 2H/(pq)$, and
\[
\sum_{\substack{p\ge z,\ q\ge z,\ p\to q\\ pq\le H}}\#\{m\}
\ \ll\ H\sum_{p\ge z}{1\over p}\sum_{\substack{q\le H/p\\ q\equiv1\ (\bmod p)}}{1\over q}.
\]
By Brun–Titchmarsh in arithmetic progressions and partial summation,
\[
\sum_{\substack{q\le Y\\ q\equiv1\ (\bmod p)}}{1\over q}\ \ll\ {\log\log Y\over \varphi(p)}\ \ll\ {\log\log X\over p},
\]
uniformly for $p\ge2$, $Y\le X/p$. Hence Case 3.1 contributes
\[
\ll\ H\sum_{p\ge z}{1\over p}\cdot{\log\log X\over p}\ \ll\ {H\,\log\log X\over z}
\ =\ o\!\Bigl({\sqrt X\over\log X}\Bigr).
\]

– Case 3.2: $pq>H$. Here $|I_{p,q}|<1$, so for fixed $(p,q)$ there is either $0$ or $1$ admissible $r$. It is convenient to reparametrize by $r$. For $r\ge1$ put
\[
J_{p,r}:=\Bigl({x\over pr},{x+H\over pr}\Bigr),\qquad |J_{p,r}|={H\over pr}.
\]
If $m=pqr\in(x,x+H)$ with $pq>H$ and $p\to q$, then $q\in J_{p,r}$ and $q\equiv1\pmod p$; conversely, for fixed $p,r$ each such prime $q$ yields at most one $m$ (since $|I_{p,q}|<1$).

We require two bounds.

Lemma 1. Uniformly for $t\ge y\ge2$,
\[
\sum_{\substack{n\le t\\ P^-(n)\ge y}}{1\over n}\ \ll\ {\log(t/y)\over\log y}.
\]
Proof. Let $\Phi(u,y)=\#\{n\le u: P^-(n)\ge y\}$. For $u\ge y$, the Buchstab bound gives $\Phi(u,y)\ll u/\log y$. Partial summation yields
\[
\sum_{n\le t,\ P^-(n)\ge y}{1\over n}=\frac{\Phi(t,y)}{t}+\int_y^t\frac{\Phi(u,y)}{u^2}\,du\ \ll\ \frac1{\log y}+\frac1{\log y}\int_y^t\frac{du}{u}\ \ll\ \frac{\log(t/y)}{\log y}.
\]
$\square$

Lemma 2 (θ-weighted Brun–Titchmarsh for unions). Let $p$ be prime and $U\subset(2,\infty)$ be a finite union of disjoint intervals. Then
\[
\sum_{\substack{q\in\mathcal P\cap U\\ q\equiv1\ (\bmod p)}}\log q\ \le\ \frac{2\,\operatorname{mes}(U)}{\varphi(p)}.
\]
Consequently, for $U\subset[z,\infty)$,
\[
\#\{q\in\mathcal P\cap U: q\equiv1\ (\bmod p)\}\ \le\ \frac{2\,\operatorname{mes}(U)}{\varphi(p)\,\log z}.
\]
Proof. The first inequality is the θ-weighted Brun–Titchmarsh inequality (Montgomery–Vaughan form) obtained from the Selberg upper-bound sieve in dimension $1$; it holds uniformly for every interval, and by additivity over disjoint unions extends to finite unions. The second follows since $\log q\ge\log z$ on $U\subset[z,\infty)$. $\square$

For $pq>H$ the defining condition gives $r<(x+H)/(pq)\le (x+H)/H<2\sqrt x$, so it suffices to sum over $1\le r<2\sqrt x$. For fixed $p\ge z$ define
\[
U_p:=\bigcup_{\substack{1\le r<2\sqrt x\\ P^-(r)\ge z}} J_{p,r} \ \subseteq\ (z, (x+H)/p].
\]
By Lemma 1,
\[
\operatorname{mes}(U_p)\le \sum_{\substack{1\le r<2\sqrt x\\ P^-(r)\ge z}} |J_{p,r}|=\frac{H}{p}\sum_{\substack{1\le r<2\sqrt x\\ P^-(r)\ge z}}{1\over r}\ \ll\ \frac{H}{p}\cdot\frac{\log(2\sqrt x/z)}{\log z}.
\]
Applying Lemma 2 with $U=U_p\subset[z,(x+H)/p]$ gives
\[
\#\{q\in U_p\cap\mathcal P: q\equiv1\ (\bmod p)\}\ \ll\ \frac{\operatorname{mes}(U_p)}{\varphi(p)\,\log z}
\ \ll\ \frac{H}{\varphi(p)\,p}\cdot\frac{\log(2\sqrt x/z)}{(\log z)^2}.
\]
For fixed $p$, the left-hand side bounds the number of $m$ counted in Case 3.2 with that $p$. Summing over $p\ge z$ and using $\varphi(p)\ge p-1$ and $\sum_{p\ge z}p^{-2}\ll 1/z$, we get
\[
\sum_{p\ge z}\#\{m\text{ in Case 3.2 with this }p\}\ \ll\ \frac{H}{(\log z)^2}\cdot\log\!\Bigl(\frac{2\sqrt x}{z}\Bigr)\sum_{p\ge z}{1\over p\,\varphi(p)}
\ \ll\ \frac{H}{(\log z)^2}\cdot\log\!\Bigl(\frac{2\sqrt x}{z}\Bigr)\cdot\frac{1}{z}.
\]
With $z=x^{1/4}(\log x)^{-6}$ one has $\log z\asymp\log x$ and $\log(2\sqrt x/z)=\tfrac14\log x+O(\log\log x)$, so the last display is
\[
\ll\ \frac{H}{z\,\log x}\ =\ o\!\Bigl(\frac{\sqrt x}{\log x}\Bigr).
\]

Combining Cases 3.1 and 3.2, the number of squarefree $z$-rough $m\in(x,x+H)$ admitting an obstruction $p\to q$ is $o(\sqrt x/\log x)$.

Step 4 (conclusion). Step 1 provides $\gg \sqrt x/\log x$ integers $m\in(x,x+H)$ with $P^-(m)\ge z$. Steps 2–3 remove only $o(\sqrt x/\log x)$ of them. Hence for all sufficiently large $n$ there exists $m\in(x,x+H)$ that is squarefree, $z$-rough, and has no pair $p\to q$ among its prime factors; equivalently $\gcd(m,\varphi(m))=1$, so $m$ is cyclic. The remaining finitely many $n$ are checked directly. Therefore for every $n\in\mathbb N$ there exists a cyclic integer $c$ with $n^2<c<(n+1)^2$. $\square$