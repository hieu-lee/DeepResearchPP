\begin{proof}
Fix a nonincreasing usage spectrum $(p_k)$ with
$$p_k = C k^{-(1+\alpha)}\,\ell(k),\qquad \alpha>0,$$
where $\ell$ is slowly varying. For $n\in\mathbb N$ let $T(n):=\sum_{k>n}p_k$ and let $L_\infty$ denote the Bayes loss. We analyze a stylized learner that selects a subset of quanta and incurs loss equal to the total usage mass of the unlearned quanta.

Step 1 (Tail mass, best-$n$ selection, and decay $n^{-\alpha}$).
- For any selection $S\subset\mathbb N$ with $|S|=n$, the loss equals $L(S)-L_\infty=\sum_{k\notin S}p_k$. Since $(p_k)$ is nonincreasing, the choice $S=\{1,\dots,n\}$ minimizes this sum (swap any $i\le n$ omitted from $S$ with some $j>n$ included in $S$ to decrease the loss; iterate). Hence
$$L_{\mathrm{best}}(n)-L_\infty\;=\;\min_{|S|=n}\sum_{k\notin S}p_k\;=\;\sum_{k>n}p_k\;=\;T(n).$$
In an $L^2$ Hilbert model with an orthonormal basis $(\psi_k)$ and a target $f_*=\sum_k\theta_k\psi_k$ with decreasing rearrangement $|\theta|_k^*=\sqrt{p_k}$, this identity is exact by Parseval and “best $m$-term equals thresholding”.
- By the discrete Karamata tail-sum theorem and slow variation of $\ell$,
$$T(n)\sim \frac{C}{\alpha}\, n^{-\alpha}\,\ell(n),\qquad n\to\infty.$$

Step 2 (Resource–to–quanta maps require best/near-best selection; composition). Let a resource $s\mapsto n(s)$ (parameters $N$, data $D$, steps $t$) be monotone and regularly varying: $n(s)= s^{\beta_s}\,\ell_s(s)$ with $\beta_s>0$ and $\ell_s$ slowly varying.

Selection principle. For the achieved selection $S(s)$ of size $n(s)$, we always have the lower bound
$$L(s)-L_\infty\;\ge\;L_{\mathrm{best}}(n(s))-L_\infty\;=\;T(n(s)).$$
Equality holds if, at resource $s$, the learner keeps the top $n(s)$ quanta. More generally, if the learner is $c$-near-best for some $c\ge1$ (i.e., $\sum_{k\notin S(s)}p_k\le c\,\min_{|S|=n(s)}\sum_{k\notin S}p_k$), then for all large $s$,
$$T(n(s))\;\le\;L(s)-L_\infty\;\le\;c\,T(n(s)).$$

Composition. Since $T\in\mathrm{RV}_{-\alpha}$ and $n\in\mathrm{RV}_{\beta_s}$ with $\beta_s>0$, we have
$$T(n(s))\sim \frac{C}{\alpha}\,[n(s)]^{-\alpha}\,\ell(n(s))
\;=\; s^{-\alpha\beta_s}\,\widetilde\ell(s),$$
where $\widetilde\ell(s):=(C/\alpha)\,[\ell_s(s)]^{-\alpha}\,\ell(n(s))$ is slowly varying (Potter bounds). Consequently:
- If the learner performs best-$n(s)$ selection, then $L(s)-L_\infty\sim s^{-\alpha\beta_s}\,\widetilde\ell(s)$.
- If it is $c$-near-best, then $L(s)-L_\infty\asymp s^{-\alpha\beta_s}$ up to a slowly varying and constant factor. In either case, the scaling exponent equals $\alpha\beta_s$.

Step 3 (Instantiations under the selection principle).
- Parameters $N$. If the class allows $m$-term representations with $m\asymp N$ and training attains best (or near-best) $m$-term selection, then $\beta_N=1$ and
$$L(N)-L_\infty\sim (C/\alpha)\,N^{-\alpha}\,\ell(N)\quad\text{(best)}\qquad\text{or}\qquad L(N)-L_\infty\asymp N^{-\alpha}\quad\text{(near-best)},$$
so $\alpha_N=\alpha$.
- Optimization steps $t$. A greedy $m$-term procedure in a Hilbert orthonormal basis selects one new largest coefficient per step and attains the best $m$-term error; after $t$ steps, $n(t)=t$ and
$$L(t)-L_\infty\sim (C/\alpha)\,t^{-\alpha}\,\ell(t),\qquad \alpha_t=\alpha.$$
- Data $D$ (occupancy/species-sampling; Poissonization and a refined de-Poissonization). After $D$ i.i.d. samples from $(p_k)$, in the stylized “learn-if-seen” model the loss equals the missing mass
$$M_D:=\sum_{k\ge1} p_k\,\mathbf 1\{k\notin S_D\},\qquad S_D:=\{k:\text{seen at least once}\},$$
so
$$\mathbb E[L(D)]-L_\infty=\mathbb E[M_D]=\sum_{k\ge1} p_k(1-p_k)^D=\mathbb P\{\text{the $(D{+}1)$st draw is new}\}=\mathbb E[K_{D+1}-K_D].$$
Let $\rho(t):=\#\{k: p_k\ge 1/t\}$. From $p_k\sim C k^{-(1+\alpha)}\ell(k)$, monotone inversion gives
$$\rho(t)\sim (C t)^{\delta}\,\ell_\rho(t),\qquad \delta=\frac{1}{1+\alpha}\in(0,1),$$
with $\ell_\rho$ slowly varying.

Poissonization. Define the Poissonized distinct-count mean
$$F(\lambda):=\mathbb E[K_{\mathrm{Poi}(\lambda)}]=\sum_{k\ge1}\bigl(1-e^{-\lambda p_k}\bigr).$$
By the Karlin–Gnedin–Hansen–Pitman theorem, $F(\lambda)\sim \Gamma(1-\delta)\,\rho(\lambda)$; in particular $F\in\mathrm{RV}_\delta$. Differentiating termwise,
$$F'(\lambda)=\sum_{k\ge1} p_k e^{-\lambda p_k},$$
and by Karamata’s monotone density theorem (Bingham–Goldie–Teugels, Th. 1.7.2),
$$F'(\lambda)\sim \delta\,\frac{F(\lambda)}{\lambda}\sim \delta\,\Gamma(1-\delta)\,\frac{\rho(\lambda)}{\lambda}\sim \delta\,\Gamma(1-\delta)\,C^{\delta}\,\lambda^{\delta-1}\,\ell_\rho(\lambda).$$

Refined de-Poissonization to the fixed-$D$ missing mass. We now prove the asymptotic equivalence
$$\mathbb E[M_D]\sim F'(D)=\sum_{k\ge1} p_k e^{-D p_k}.$$
Pick a cutoff $\tau_D:=D^{-3/4}\in(0,1/2)$, so that $D\tau_D\to\infty$ and $D\tau_D^2\to0$. For $x\in[0,1/2]$, Taylor’s formula with remainder yields
$$\log(1-x)=-x-\tfrac{x^2}{2}-R(x),\qquad 0\le R(x)\le 2x^3.$$ 
Therefore, for $x\in[0,\tau_D]$,
$$e^{-Dx-\frac{D x^2}{2}-2D x^3}\le (1-x)^D\le e^{-Dx-\frac{D x^2}{2}}\le e^{-Dx}.$$
Since $D\tau_D^2\to0$ and $D\tau_D^3\to0$, the factor $e^{-\frac{D x^2}{2}-2D x^3}=1+o(1)$ uniformly in $x\in[0,\tau_D]$. Hence
$$\sum_{p_k\le \tau_D} p_k (1-p_k)^D\;=\;\bigl(1+o(1)\bigr)\sum_{p_k\le \tau_D} p_k e^{-D p_k}.$$
For the complementary part, $(1-x)^D\le e^{-Dx}$ and therefore
$$\sum_{p_k>\tau_D} p_k (1-p_k)^D\le e^{-D\tau_D}\sum_{k} p_k\le e^{-D^{1/4}}=o\bigl(F'(D)\bigr),$$
where the final $o(\cdot)$ uses $F'(D)\asymp D^{\delta-1}\ell_\rho(D)$ (polynomial decay) versus $e^{-D^{1/4}}$ (super-polynomial). The same bound gives $\sum_{p_k>\tau_D} p_k e^{-D p_k}\le e^{-D^{1/4}}=o(F'(D))$. Combining,
\[\begin{aligned}
\mathbb E[M_D]
&=\sum_{p_k\le \tau_D} p_k (1-p_k)^D\; +\; \sum_{p_k>\tau_D} p_k (1-p_k)^D\\
&=\bigl(1+o(1)\bigr)\sum_{p_k\le \tau_D} p_k e^{-D p_k}\; +\; o\bigl(F'(D)\bigr)\\
&=\bigl(1+o(1)\bigr)\sum_{k\ge1} p_k e^{-D p_k}\;=\;\bigl(1+o(1)\bigr)F'(D).
\end{aligned}\]
Thus
$$\mathbb E[M_D]\sim F'(D)\sim \delta\,\Gamma(1-\delta)\,C^{\delta}\,D^{\delta-1}\,\ell_\rho(D).$$
Equivalently, there exist $B>0$ and a slowly varying $\ell_D(D)$ (absorbing $\ell_\rho$) such that
$$\mathbb E[L(D)]-L_\infty\sim B\, D^{-\frac{\alpha}{1+\alpha}}\,\ell_D(D),\qquad B=\delta\,\Gamma(1-\delta)\,C^{\delta},\quad \delta=\tfrac{1}{1+\alpha}.$$

Conclusion. Under the quantization hypothesis with heavy-tailed usage $p_k\propto k^{-(1+\alpha)}$, learning the $n$ most-used quanta yields $L_{\mathrm{best}}(n)-L_\infty\sim (C/\alpha) n^{-\alpha}\ell(n)$. Any regularly varying resource–to–quanta map $s\mapsto n(s)$ combined with best (or near-best) selection implies $L(s)\approx A_s\, s^{-\alpha\beta_s}$ (up to slowly varying and constant factors). In particular, $\alpha_N=\alpha$ when $n\asymp N$, $\alpha_t=\alpha$ for greedy $t$-step selection, and—independently—under “learn-if-seen”, the expected loss obeys $\mathbb E[L(D)]-L_\infty\approx B D^{-\alpha/(1+\alpha)}$ (up to slow variation), with the explicit constant $B=\delta\,\Gamma(1-\delta)\,C^{\delta}$ tied to the usage spectrum.\qedhere
\end{proof}