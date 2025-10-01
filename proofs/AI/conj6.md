**Claim (counterexample for arbitrarily wide two-layer ReLU nets).** For every hidden width $m\ge 2$ there exist a dataset $\mathcal D$, a two-layer ReLU network of width $m$, and two trained parameter vectors $\theta_a,\theta_b$ (global minimizers of the empirical loss) such that for every hidden-channel permutation $g\in\mathcal G\cong S_m$, the straight segment $\{(1-t)\theta_a+t(g\!\cdot\!\theta_b):t\in[0,1]\}$ exhibits a strict loss barrier. In particular, at $t=\tfrac12$,
$$
L\big((1/2)\theta_a+(1/2)(g\!\cdot\!\theta_b)\big) \,>\, \max\{L(\theta_a),L(g\!\cdot\!\theta_b)\}=0.
$$
This refutes the linear mode-connectivity-up-to-permutation conjecture even for arbitrarily wide (hence “modern”) ReLU nets.

**Proof.** Consider a two-layer ReLU network with input and output dimension $2$ and hidden width $m\ge 2$. Parameters are $\theta=(W,V)$ with $W\in\mathbb R^{m\times 2}$, $V\in\mathbb R^{2\times m}$, realization
$$
 f_{W,V}(x)=V\,\sigma(Wx),\qquad \sigma(z)=\max\{z,0\}\ \text{coordinatewise},
$$
and squared empirical loss on the dataset $\mathcal D=\{(e_1,e_1),(e_2,e_2)\}$:
$$
L(W,V)=\tfrac12\sum_{i=1}^2\|V\,\sigma(W e_i)-e_i\|_2^2.
$$
Hidden-channel permutations act by $W\mapsto PW$ and $V\mapsto VP^{-1}$ with $P\in S_m$; by permutation invariance, $f_{P\!W,\,VP^{-1}}\equiv f_{W,V}$ and $L(g\!\cdot\!\theta)=L(\theta)$ for all $g\in\mathcal G$.

Fix $\lambda>1$ and write $D\coloneqq\operatorname{diag}(\lambda,\lambda^{-1})$, $D^{-1}=\operatorname{diag}(\lambda^{-1},\lambda)$. Define two trained (globally optimal) solutions by activating only the first two channels and zeroing the rest:
$$
W_a=\begin{bmatrix}I_2\\ 0_{(m-2)\times 2}\end{bmatrix},\quad V_a=\begin{bmatrix}I_2 & 0_{2\times (m-2)}\end{bmatrix},\qquad
W_b=\begin{bmatrix}D^{-1}\\ 0_{(m-2)\times 2}\end{bmatrix},\quad V_b=\begin{bmatrix}D & 0_{2\times (m-2)}\end{bmatrix}.
$$
For $i=1,2$, $W_a e_i\succeq0$ and $W_b e_i\succeq0$ componentwise, so $\sigma(W_a e_i)=W_a e_i$ and $\sigma(W_b e_i)=W_b e_i$. Thus $f_{\theta_a}(e_i)=V_a W_a e_i=e_i$ and $f_{\theta_b}(e_i)=V_b W_b e_i=e_i$, whence $L(\theta_a)=L(\theta_b)=0$. By permutation invariance, $L(g\!\cdot\!\theta_b)=0$ for all $g\in\mathcal G$.

Fix any $g\in\mathcal G$ and set $\theta'=(W',V')\coloneqq g\!\cdot\!\theta_b=(PW_b,\,V_bP^{-1})$. Consider the straight segment
$$
W_t=(1-t)W_a+tW',\qquad V_t=(1-t)V_a+tV',\qquad t\in[0,1].
$$
All entries of $W_a, W'$ and $V_a, V'$ are nonnegative, hence $W_t, V_t$ are nonnegative for all $t$. Therefore for the training inputs $e_1,e_2$ the preactivations remain nonnegative along the whole segment and $\sigma(W_t e_i)=W_t e_i$ for all $t$. Consequently, on $\mathcal D$ the network behaves linearly along the segment and
$$
L(\theta_t)=\tfrac12\big\|V_tW_t-I_2\big\|_F^2.
$$
At the midpoint $t=\tfrac12$ we have the identity
$$
V_{1/2}W_{1/2}=\tfrac14\big(V_aW_a+V_aW'+V'W_a+V'W'\big).
$$
We now analyze $\Delta\coloneqq V_{1/2}W_{1/2}-I_2$ by cases, according to the overlap between the two active channels of $\theta_a$ (indices $\{1,2\}$) and those of $\theta'$ (some two-element subset $T\subset\{1,\dots,m\}$), writing $r\coloneqq |\{1,2\}\cap T|\in\{0,1,2\}$.

- Case $r=2$ (the two active channels coincide as a set). There are two subcases on the restriction of $g$ to these channels:
  1) No swap on the pair: then $W'$ and $V'$ restricted to the pair equal $D^{-1}$ and $D$, respectively. Hence
     $$
     \Delta=\tfrac14\big(D+D^{-1}-2I_2\big),\quad L(\theta_{1/2})=\tfrac12\|\Delta\|_F^2=\frac{(\lambda+\lambda^{-1}-2)^2}{16}>0.
     $$
  2) Swap on the pair: with $P=\begin{psmallmatrix}0&1\\1&0\end{psmallmatrix}$,
     $$
     \Delta=\tfrac14\big(PD^{-1}+DP-2I_2\big)=\begin{psmallmatrix}-\tfrac12 & \tfrac{\lambda}{2}\\ \tfrac{\lambda^{-1}}{2} & -\tfrac12\end{psmallmatrix},\ 
     L(\theta_{1/2})=\tfrac12\|\Delta\|_F^2=\frac14+\frac{\lambda^2+\lambda^{-2}}{8}>0.
     $$

- Case $r=1$ (exactly one channel overlaps). Without loss of generality, suppose channel $1$ overlaps. If the overlapped channel preserves the same coordinate, then
  $$
  V_{1/2}W_{1/2}=\operatorname{diag}\Big(\tfrac{2+\lambda+\lambda^{-1}}{4},\ \tfrac12\Big),
  $$
  so
  $$
  L(\theta_{1/2})=\tfrac12\left[\Big(\tfrac{\lambda+\lambda^{-1}-2}{4}\Big)^2+\Big(\tfrac12\Big)^2\right]>0.
  $$
  If the overlapped channel swaps the coordinate, then
  $$
  V_{1/2}W_{1/2}=\tfrac12 I_2+\tfrac14\big(\lambda\,e_1e_2^\top+\lambda^{-1} e_2e_1^\top\big),
  $$
  whence
  $$
  L(\theta_{1/2})=\tfrac12\left[2\Big(\tfrac12\Big)^2+\Big(\tfrac{\lambda}{4}\Big)^2+\Big(\tfrac{\lambda^{-1}}{4}\Big)^2\right]=\frac14+\frac{\lambda^2+\lambda^{-2}}{32}>0.
  $$

- Case $r=0$ (the two active channels are disjoint). Then the cross terms vanish and
  $$
  V_{1/2}W_{1/2}=\tfrac14(I_2+I_2)=\tfrac12 I_2,\quad L(\theta_{1/2})=\tfrac12\left\|\tfrac12 I_2-I_2\right\|_F^2=\frac14>0.
  $$

In every case and for every $g\in\mathcal G$, $L(\theta_{1/2})>0$ while $L(\theta_a)=L(g\!\cdot\!\theta_b)=0$. Hence the straight segment between $\theta_a$ and $g\!\cdot\!\theta_b$ has a strict loss barrier (indeed at $t=\tfrac12$). Moreover, in the coincident-channel cases ($r=2$), the barrier can be made arbitrarily large by letting $\lambda\to\infty$.

Therefore, even for arbitrarily wide two-layer ReLU networks (a canonical modern architecture class), there exist trained parameter vectors $\theta_a,\theta_b$ for which no hidden-channel permutation $g$ renders the linear interpolation low-loss throughout. ∎