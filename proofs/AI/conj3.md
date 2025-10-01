**Proof.** We give a counterexample (standard last-layer SGD over frozen deep features) in which training makes steady progress for a long phase while the empirical sharpness stays strictly above the stability threshold and does not self-adjust toward $2/\eta$.

Set-up (frozen deep features; last-layer training). Fix a deep feature map $x\mapsto\phi(x)\in\mathbb R^d$ (from a large pre-trained network); train only the last linear layer $w\in\mathbb R^d$. On data $\{(x_i,y_i)\}_{i=1}^n$, the squared loss is
$$
L(w)=\tfrac12\sum_{i=1}^n(\phi(x_i)^T w-y_i)^2=\tfrac12\,\|\Phi w-y\|^2,\qquad \Phi:=\begin{bmatrix}\phi(x_1)^T\\ \vdots \\ \phi(x_n)^T\end{bmatrix}\in\mathbb R^{n\times d}.
$$
The empirical Hessian is the constant matrix $H:=\nabla^2 L(w)\equiv\Phi^T\Phi\succeq0$, so the sharpness $\lambda_{\max}(t)\equiv\lambda_1(H)$ is constant along the run. We use mini-batch SGD with uniform-with-replacement sampling, batch size $b\in\{1,\ldots,n-1\}$, and fixed step size $\eta>0$.

Data geometry (one orthogonal outlier). Choose $n\ge d+1$ and construct feature rows $\phi_1,\ldots,\phi_{n-1}\in\mathbb R^d$ spanning a $(d-1)$-dimensional subspace $V$. Define
$$
H_{\rm bulk}:=\sum_{i=1}^{n-1}\phi_i\phi_i^T\ \succeq\ 0,\qquad \mathrm{rank}(H_{\rm bulk})=d-1.
$$
Thus $H_{\rm bulk}|_V\succ0$ and $H_{\rm bulk}v=0$ for $v\in V^{\perp}$. Let the positive eigenvalues of $H_{\rm bulk}|_V$ be $0<\lambda_d\le\cdots\le\lambda_2$ (so $\lambda_2=\lambda_{\max}(H_{\rm bulk}|_V)$). Pick a unit $v_1\in V^{\perp}$ and set the outlier feature $\phi_n:=\sqrt{\lambda_1}\,v_1$ with $\lambda_1\gg\lambda_2$. Then
$$
H\;=\;H_{\rm bulk}+\phi_n\phi_n^T\;=\;H_{\rm bulk}+\lambda_1\,v_1v_1^T,\qquad v_1\perp V,\qquad \lambda_{\max}(H)=\lambda_1,\ \lambda_2(H)=\lambda_2.
$$

Labels on the bulk. Fix $w_V^*\in V$ and set $y_i:=\phi_i^T w_V^*$ for $i\in S:=\{1,\ldots,n-1\}$; choose $y_n$ arbitrarily. Then the bulk loss $L_{\rm bulk}(w):=\tfrac12\sum_{i\in S}(\phi_i^T w-y_i)^2$ has unique minimizer over $V$ equal to $w_V^*$.

Step size (chosen below classical stability for the bulk dynamics but above the top-eigenvalue threshold). Let
$$
M^2\;:=\;\frac{1}{n-1}\sum_{i\in S}\|\phi_i\|^4,\qquad \mu\;:=\;\lambda_d,\qquad L\;:=\;\lambda_2.
$$
Choose $\eta$ so that
$$
\boxed{\quad \frac{2}{\lambda_1}\ <\ \eta\ \le\ \min\Big\{\frac{n-1}{nL},\ \frac{b\,\mu}{4n(n-1)\,M^2}\Big\}\quad}\tag{SS}
$$
This is feasible because $\lambda_1$ can be made arbitrarily large by scaling $\phi_n$ while leaving $M,\mu,L$ (which depend only on the bulk) unchanged.

A long phase without the outlier (corrected sampling probability). Let $\mathcal E_T$ be the event that none of the first $T$ mini-batches contains index $n$. Under uniform-with-replacement sampling with batch size $b$, a single batch omits a fixed index with probability $(1-1/n)^b$. Across independent steps,
$$
\mathbb P(\mathcal E_T)\;=\;\big((1-\tfrac{1}{n})^b\big)^{\!T}\;=\;(1-\tfrac{1}{n})^{bT}\;\ge\;\exp\Big(\!-\tfrac{bT}{n-1}\Big),
$$
using $\log(1-x)\ge -x/(1-x)$ for $x\in(0,1)$. For any fixed $c\in(0,1)$ and $T:=\lfloor c\,\tfrac{n}{b}\rfloor$, one has
$$
\mathbb P(\mathcal E_T)\ \ge\ \exp\Big(\!-\tfrac{c n}{n-1}\Big)\ \ge\ e^{-2c}\qquad(\text{for all }n\ge2).
$$
Hence with constant probability bounded away from $0$, there is a prefix of length $T=\Theta(n/b)$ containing no outlier.

Dynamics on $\mathcal E_T$. Fix $\mathcal E_T$. Gradients from the sampled indices lie in $V$, so the $v_1$-component of $w_t$ is constant, and the $V$-component evolves independently. Writing the bulk error $e_t:=\Pi_V(w_t-w_V^*)\in V$, one SGD step (conditioned on $\mathcal E_T$) satisfies
$$
 e_{t+1}\;=\;\big(I-\alpha\,H_{\rm bulk}|_V\big)e_t\; -\;\eta\,\zeta_t,\qquad \alpha:=\frac{n}{n-1}\eta,\qquad \mathbb E[\zeta_t\mid\mathcal F_t,\mathcal E_T]=0,
$$
where $\mathcal F_t$ is the natural filtration and we used that the estimator scales by $n/b$ while sampling is (conditionally) uniform on $S$.

Correct mini-batch variance bound (fixing (⋆)). Let $Y$ be a single-sample bulk gradient $g_i(w_t)=\phi_i\phi_i^T e_t$ with $i\sim\mathrm{Unif}(S)$, and $G_t:=\tfrac{n}{b}\sum_{j=1}^b Y_j$. Then $\zeta_t=G_t-\mathbb E[G_t\mid\mathcal F_t,\mathcal E_T]$ and
$$
\mathbb E\big[\,\|\zeta_t\|^2\mid\mathcal F_t,\mathcal E_T\big]\;=\;\mathrm{Var}(G_t)\;=\;\frac{n^2}{b}\,\mathrm{Var}(Y)\;\le\;\frac{n^2}{b}\,\mathbb E\big[\,\|Y\|^2\mid\mathcal F_t,\mathcal E_T\big].
$$
Since $Y=\phi_i\phi_i^T e_t$ and $i\sim\mathrm{Unif}(S)$,
$$
\mathbb E\big[\,\|Y\|^2\mid\mathcal F_t,\mathcal E_T\big]\;=\;\frac{1}{n-1}\sum_{i\in S}\|\phi_i\phi_i^T e_t\|^2\;\le\;\frac{1}{n-1}\sum_{i\in S}\|\phi_i\|^4\,\|e_t\|^2\;=\;M^2\,\|e_t\|^2.
$$
Therefore
$$
\boxed{\quad \mathbb E\big[\,\|\zeta_t\|^2\mid\mathcal F_t,\mathcal E_T\big]\ \le\ \frac{n^2}{b}\,M^2\,\|e_t\|^2.\quad}\tag{VB}
$$

Quadratic Lyapunov recursion with corrected constants. Let $A:=I-\alpha\,H_{\rm bulk}|_V$. Then, conditioning on $\mathcal E_T$ and using $\mathbb E[\zeta_t\mid\cdot]=0$ and (VB),
$$
\begin{aligned}
\mathbb E\big[\,\|e_{t+1}\|^2\mid\mathcal F_t,\mathcal E_T\big]
&\le\ \|A e_t\|^2\ +\ \eta^2\,\mathbb E\big[\,\|\zeta_t\|^2\mid\mathcal F_t,\mathcal E_T\big]\\
&\le\ \|A\|^2\,\|e_t\|^2\ +\ \eta^2\,\frac{n^2}{b}\,M^2\,\|e_t\|^2.
\end{aligned}
$$
For $\alpha\le 1/L$ (enforced by (SS)), the spectral norm of $A$ on $V$ obeys $\|A\|=\max\{\,|1-\alpha\mu|,\,|1-\alpha L|\,\}=1-\alpha\mu$, hence
$$
\mathbb E\big[\,\|e_{t+1}\|^2\mid\mathcal F_t,\mathcal E_T\big]\ \le\ \Big((1-\alpha\mu)^2\ +\ \eta^2\,\frac{n^2}{b}\,M^2\Big)\,\|e_t\|^2.
$$
Because $(1-x)^2\le 1-x$ for $x\in[0,1]$ and $\alpha\mu\in(0,1]$ under (SS), and because (SS) also enforces $\eta^2\,\tfrac{n^2}{b}M^2\le \tfrac14\alpha\mu$, we obtain
$$
\mathbb E\big[\,\|e_{t+1}\|^2\mid\mathcal F_t,\mathcal E_T\big]\ \le\ \Big(1-\alpha\mu\ +\ \tfrac14\alpha\mu\Big)\,\|e_t\|^2\ =\ \Big(1-\tfrac{3}{4}\,\alpha\mu\Big)\,\|e_t\|^2.
$$
Taking expectations and unrolling for $0\le t\le T$ yields geometric decay on $\mathcal E_T$:
$$
\mathbb E\big[\,\|e_t\|^2\mid\mathcal E_T\big]\ \le\ \Big(1-\tfrac{3}{4}\,\tfrac{n}{n-1}\,\mu\,\eta\Big)^{\!t}\,\|e_0\|^2.
$$
Consequently the bulk loss decreases geometrically:
$$
\mathbb E\big[\,L_{\rm bulk}(w_t)-L_{\rm bulk}(w_V^*)\mid\mathcal E_T\big]\ =\ \tfrac12\,\mathbb E[e_t^T H_{\rm bulk} e_t\mid\mathcal E_T]\ \le\ \tfrac{\lambda_2}{2}\,\Big(1-\tfrac{3}{4}\,\tfrac{n}{n-1}\,\mu\,\eta\Big)^{\!t}\,\|e_0\|^2.
$$

Sharpness stays above the threshold and does not self-adjust. Along the entire run, $H$ is constant, hence
$$
\eta\,\lambda_{\max}(t)\ \equiv\ \eta\,\lambda_1\ \ge\ 2+\varepsilon\qquad(\varepsilon:=\eta\lambda_1-2>0),
$$
by the left inequality in (SS). There is no mechanism that changes $\lambda_1$ (it is fixed by $\Phi$), so no “self-adjustment” of sharpness toward $2/\eta$ occurs at any time.

Conclusion. We have constructed a standard large-scale training setting (deep frozen features with last-layer mini-batch SGD) in which, with constant probability, there is a long phase of length $T=\Theta(n/b)$ during which training proceeds (the bulk loss decays at a linear rate) while the measured sharpness satisfies $\eta\,\lambda_{\max}(t)>2$ by a fixed margin and remains constant, far from $2/\eta$. Hence the conjectured “edge-of-stability sharpness law” does not hold as a general law across large-scale DL training. ∎