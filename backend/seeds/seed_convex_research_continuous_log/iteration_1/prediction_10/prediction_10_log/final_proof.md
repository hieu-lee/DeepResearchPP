\begin{proof}
Fix $L>0$ and let $f:\mathbb{R}^d\to\mathbb{R}$ be convex and $L$-smooth. Fix a stepsize $\eta\in\big(\tfrac{7}{4L},\tfrac{2}{L}\big)$. Define tentative updates $\widetilde x_{n+1}:=x_n-\eta\nabla f(x_n)$ and attempted decreases $\Delta_n:=f(x_n)-f(\widetilde x_{n+1})$. The scheme accepts step $n$ iff $\Delta_n\le \Delta_{n-1}$ (with the convention that at the beginning of each block of accepted steps the comparison threshold is $+\infty$); if rejected, it restarts by setting $x_{n+1}:=x_n$ and reinitializes the comparison threshold.

Claim 1 (convexity between restarts). Consider any maximal block $I=\{a,\dots,b\}$ of consecutive accepted steps. For every $n\in I$ with $n>a$, acceptance gives $\Delta_n\le \Delta_{n-1}$. Since for accepted steps $f(x_n)-f(x_{n+1})=\Delta_n$, the forward differences $f(x_n)-f(x_{n+1})$ are nonincreasing on $I$. Hence the discrete optimization curve $n\mapsto f(x_n)$ is convex on $I$.

Claim 2 (no universal rate-preserving constant). Assume, toward a contradiction, that there exists a universal constant $C>0$ such that for every convex $L$-smooth $f$, every $\varepsilon>0$, every starting point, and every choice of $\eta\in(\tfrac{7}{4L},\tfrac{2}{L})$, the restarted scheme reaches $f(x_n)-f_\star\le\varepsilon$ in at most $C$ times as many iterations as the best fixed stepsize gradient descent with $\eta\in(0,\tfrac{2}{L}]$ chosen in hindsight.

Take $d=1$ and $f(x)=\tfrac{L}{2}x^2$, whose unique minimizer is $x_\star=0$. Let $x_0\ne 0$ and fix any target $\varepsilon\in(0,f(x_0))$. For any $\delta\in(0,\tfrac14)$ set $\eta=\tfrac{2-\delta}{L}\in\big(\tfrac{7}{4L},\tfrac{2}{L}\big)$. Plain gradient descent with this $\eta$ satisfies
$$
x_{n+1}=(1-\eta L)x_n=-(1-\delta)\,x_n,\qquad f(x_n)=\tfrac{L}{2}(1-\delta)^{2n}x_0^2.
$$
The attempted decreases obey
$$
\Delta_n=f(x_n)-f(x_{n+1})=f(x_n)\big(1-(1-\delta)^2\big),\qquad \frac{\Delta_{n+1}}{\Delta_n}=(1-\delta)^2\in(0,1),
$$
so $\{\Delta_n\}$ is strictly decreasing. Therefore the restart condition $\Delta_n>\Delta_{n-1}$ never occurs, and the realized run coincides with plain GD at stepsize $\eta$. Let $K$ be the first index with $f(x_K)\le\varepsilon$. Then
$$
(1-\delta)^{2K}\le \frac{\varepsilon}{f(x_0)} \quad\Longrightarrow\quad K\;\ge\;\frac{\log\big(f(x_0)/\varepsilon\big)}{2\,\log\big(1/(1-\delta)\big)}\;\ge\;\frac{1-\delta}{2\delta}\,\log\!\Big(\frac{f(x_0)}{\varepsilon}\Big),
$$
where we used $\log(1/(1-\delta))\le \delta/(1-\delta)$. In contrast, for the same $f$ the fixed stepsize $\eta_\star=1/L\in(0,2/L]$ attains $x_1=0$ and hence reaches $\varepsilon$ in one step; thus the best fixed-stepsize complexity in hindsight is $k_{\mathrm{best}}(\varepsilon)=1$. Since $K\to\infty$ as $\delta\downarrow 0$, for the assumed constant $C>0$ we can choose $\delta\in(0,\tfrac14)$ so small that $K> C\,k_{\mathrm{best}}(\varepsilon)=C$, contradicting the assumption.

Combining the two claims proves that the restart rule enforces convexity of the optimization curve on each block between restarts, but no universal constant-factor comparison with the best fixed stepsize method holds.
\end{proof}