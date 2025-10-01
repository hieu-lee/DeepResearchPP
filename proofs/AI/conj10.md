**Claim.** The Conjecture (Heavy-Tailed Mechanistic Universality) is false: there exists a family of deep nets trained with mini-batch SGD for which no internal mechanistic feature—weights, circuits, activations (on bounded data), Jacobians, or Hessians—exhibits heavy-tailed (power-law) coefficients or singular values with exponent $\mu\in(0,2)$ across layers/scales.

**Proof.** Fix depth $L\ge 1$. For each width $d\in\mathbb N$, consider an $L$-layer feedforward network with linear activation $\varphi(x)\equiv x$ (so the network as a function is linear). Parameterize each weight matrix in layer $\ell$ by the Cayley transform
$$
W_\ell(U_\ell) := (I-A_\ell)(I+A_\ell)^{-1},\qquad A_\ell:=U_\ell-U_\ell^\top,\quad U_\ell\in\mathbb R^{d\times d}.
$$
For any real skew-symmetric $A_\ell$, $I+A_\ell$ is invertible (the eigenvalues of $A_\ell$ are purely imaginary), hence $W_\ell\in O(d)$ and $\sigma_i(W_\ell)=1$ for all singular values $\sigma_i$. Train the free parameters $U_1,\dots,U_L$ by mini-batch SGD (the chain rule applies to the smooth map $U\mapsto W(U)$). Thus, at every iterate and for every trained parameter $\widehat U_\ell$, the realized weight $\widehat W_\ell=W_\ell(\widehat U_\ell)$ is orthogonal.

We now verify, feature by feature, that all relevant internal mechanisms have uniformly bounded coefficients/singular values, hence cannot be heavy-tailed.

1) Weights. Let $\mathsf S_d$ be the multiset of all singular values of $\{\widehat W_\ell\}_{\ell\le L}$. Then $\mathsf S_d=\{1,\dots,1\}$, so if $X_d$ denotes a uniform sample from $\mathsf S_d$, $\mathbb P(X_d>t)=0$ for all $t>1$. Therefore $X_d\notin\mathrm{RV}_\mu$ for any $\mu\in(0,2)$.

2) Circuits (path- or subcircuit-level linear operators). A standard formalization of a circuit is the linear operator obtained by inserting diagonal gating/selection matrices between layers; concretely, for any diagonal $G_1,\dots,G_{L-1}$ with operator norms $\|G_k\|_2\le 1$ (e.g., $0$–$1$ selectors of units or data-dependent gates), define
$$
C:=\widehat W_L G_{L-1}\widehat W_{L-1}\cdots G_1\widehat W_1.
$$
Then $\|C\|_2\le\prod_\ell \|\widehat W_\ell\|_2\prod_k\|G_k\|_2\le 1$, hence every singular value of $C$ lies in $[0,1]$. Consequently, if $Y_d$ denotes any sampling scheme over singular values of such circuit operators across layers/scales, $\mathbb P(Y_d>t)=0$ for all $t>1$. No power-law tail with index $\mu\in(0,2)$ is possible.

3) Input–output Jacobians. Because $\varphi\equiv\mathrm{id}$, the input–output Jacobian is constant in $x$ and equals
$$
J:=\widehat W_L\widehat W_{L-1}\cdots\widehat W_1\in O(d),
$$
so $\sigma_i(J)=1$ for all $i$. If $Z_d$ samples singular values of Jacobians across layers/scales, then $\mathbb P(Z_d>t)=0$ for all $t>1$, hence $Z_d\notin\mathrm{RV}_\mu$ for any $\mu\in(0,2)$.

4) Input–output Hessians. With $\varphi\equiv\mathrm{id}$ the network is globally linear, so the input–output Hessian is identically zero. All its singular values are $0$, and no heavy tail is possible.

5) Activations (on bounded data). For any input $x\in\mathbb R^d$, the layer-$\ell$ activation is $h_\ell(x)=\widehat W_\ell\cdots\widehat W_1 x$, whence $\|h_\ell(x)\|_2=\|x\|_2$. If the training data lie in a bounded set (e.g., images normalized to $\|x\|_2\le R$), then for every coordinate and every layer, $|h_\ell(x)_i|\le R$. Any random variable formed by sampling activation coordinates across layers/scales thus has compact support $[-R,R]$ and cannot be heavy-tailed. This rules out heavy tails in activations for such modalities; one counter-modality suffices to refute the universal claim “across modalities.”

Each item above is uniform in the width $d$ (and depth $L$): all operator-norm/singular-value bounds are $\le 1$ (or $=0$ for the Hessian) and independent of scale. In particular, for any of the random variables $V_d$ obtained by uniformly sampling coefficients or singular values from any of these internal mechanisms across layers/scales, there exists a deterministic constant $C<\infty$ (here $C=1$ or $C=R$ for bounded-data activations) such that $\mathbb P(|V_d|>t)=0$ for all $t>C$. By the definition of regular variation, this precludes $V_d\in\mathrm{RV}_\mu$ for any $\mu\in(0,2)$.

Because this construction works for every width $d$ (hence across model sizes) and, as shown, rules out heavy-tailed statistics not only for weights but also for circuits, Jacobians, Hessians, and (on bounded-data modalities) activations, it contradicts the conjectured universal heavy-tailed mechanistic behavior. Therefore the stated universality conjecture is false. ∎