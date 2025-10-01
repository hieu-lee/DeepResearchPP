**Claim (Disproof of the conjecture as stated).** The conjecture is false without additional dimensional assumptions: there exist balanced datasets and deep cross-entropy classifiers whose training loss tends to $0$ while item (ii) (class means collapse to a centered simplex ETF) is impossible, hence the conjunction (i)–(iv) fails.

**Proof.** We give a concrete counterexample for $K=3$ classes and last-layer feature dimension $d=1$.

1) Impossibility of a centered simplex ETF in $\mathbb R^1$ for $K\ge3$.
Let $\{v_c\}_{c=1}^K\subset\mathbb R^d$ be a centered simplex ETF, i.e., $\sum_c v_c=0$, $\lVert v_c\rVert=r$ for all $c$, and $\langle v_c,v_{c'}\rangle=-\tfrac{r^2}{K-1}$ for $c\ne c'$. The Gram matrix is
$$
G\equiv (\langle v_c,v_{c'}\rangle)_{c,c'} 
= r^2\Big(\tfrac{K}{K-1}I_K-\tfrac{1}{K-1}\mathbf 1\mathbf 1^\top\Big).
$$
Thus $G\mathbf 1=0$ and $G$ has eigenvalue $\tfrac{Kr^2}{K-1}$ with multiplicity $K-1$ on $\mathbf 1^\perp$, so $\operatorname{rank}(G)=K-1$. Since $\operatorname{rank}(G)\le d$, necessarily $d\ge K-1$. In particular, for $d=1$ we must have $K\le2$. Hence a centered simplex ETF of $K=3$ vectors cannot exist in $\mathbb R^1$.

2) A balanced dataset with distinct inputs and a deep CE classifier with train loss $\to0$ in $d=1$.
Fix any integer $m\ge1$ and set $n=3m$. Define a balanced training set in $\mathbb R$ by
$$
 x_i:=i\in\mathbb R\ (i=1,\dots,n),\qquad y_i:=1+((i-1)\bmod 3),
$$
so that $n_1=n_2=n_3=m$ and the inputs $x_i$ are pairwise distinct. Prescribe class-dependent target features
$$
 s_1:=2,\qquad s_2:=0,\qquad s_3:=-2,
$$
and define $h:\mathbb R\to\mathbb R$ as the continuous piecewise-linear function satisfying $h(x_i)=s_{y_i}$ for all $i$, obtained by linear interpolation on each interval $[x_i,x_{i+1}]$ and affine extension outside $[x_1,x_n]$. Because the $x_i$ are strictly increasing, this is single-valued. Any such continuous piecewise-linear function admits an exact 2-layer ReLU realization
$$
 h(x)=a_0+a_1x+\sum_{j=1}^{n-1} c_j\,(x-t_j)_+,
$$
so $h$ is realizable by a (shallow) neural net and hence by a deeper one (append identity layers).

For the softmax last layer, choose $W\in\mathbb R^{3\times 1}$ and $b\in\mathbb R^3$ as
$$
W=\begin{bmatrix}1\\0\\-1\end{bmatrix},\qquad b=\begin{bmatrix}1\\2.1\\1\end{bmatrix}.
$$
For any training sample with label $c$ and feature $t:=h(x_i)\in\{2,0,-2\}$, the logits are $z=Wt+b$ and the margins are:
- if $t=2$ ($c=1$): $z=(3,2.1,-1)$, so $m=z_1-\max(z_2,z_3)=0.9$;
- if $t=0$ ($c=2$): $z=(1,2.1,1)$, so $m=1.1$;
- if $t=-2$ ($c=3$): $z=(-1,2.1,3)$, so $m=0.9$.
Hence every training sample enjoys a uniform positive margin $m_0:=0.9$.

For the multiclass cross-entropy $\ell(z,c)=\log\sum_{k=1}^3 e^{z_k-z_c}$, scaling logits by $\alpha>0$ (i.e., $(W,b)\mapsto(\alpha W,\alpha b)$) yields
$$
\ell(\alpha z,c)=\log\Big(1+\sum_{k\ne c}e^{\alpha(z_k-z_c)}\Big)\le \log\big(1+2e^{-\alpha m_0}\big)\le 2e^{-\alpha m_0}.
$$
Summing over $n$ samples, the empirical loss satisfies $L_{\rm train}(\alpha)\le 2n e^{-\alpha m_0}\to0$ as $\alpha\to\infty$. Along this sequence, $h$ (hence the class means) is fixed.

3) Failure of item (ii).
The class means are
$$
\mu_c=\frac1{n_c}\sum_{y_i=c} h(x_i)=s_c\in\{2,0,-2\}.
$$
They are centered ($\mu_1+\mu_2+\mu_3=0$) and $\Sigma_W=0$ holds exactly (each class is mapped to a constant), so (i) is satisfied. However, by Step 1 no centered simplex ETF of $K=3$ vectors exists in $\mathbb R^1$, hence these means cannot satisfy (ii) (indeed their norms are $2,0,2$, not equal).

Therefore, along a sequence of parameters for which the cross-entropy training loss tends to $0$, item (ii) fails. Consequently, the conjecture (asserting simultaneous validity of (i)–(iv) as loss $\to0$) is false as stated.

Remark. The same obstruction shows that for any $K$ and $d$ with $K-1>d$, item (ii) is impossible a priori, so the conjecture cannot hold in full generality without at least the dimensional condition $d\ge K-1$. ∎