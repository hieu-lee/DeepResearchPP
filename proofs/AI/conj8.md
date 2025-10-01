**Claim (Counterexample to universality of the Frequency Principle).** The conjecture “Across architectures/losses/datasets, DNNs fit $f^*$ by first matching low-frequency components and only later high-frequency components” is false as stated.

**Proof.** Work entirely over real-valued functions. Let $\mathbb T:=\mathbb R/\mathbb Z$ be the one-dimensional flat torus with the uniform probability measure $\rho_X$. Denote the complex Fourier characters by $e_k(x):=e^{2\pi i kx}$, $k\in\mathbb Z$, which form an orthonormal basis of $L^2(\rho_X;\mathbb C)$. For real-valued functions, Fourier coefficients satisfy $\widehat f[-k]=\overline{\widehat f[k]}$ and energies on bands $B\subset\mathbb Z$ are $\mathcal E_B(f)=\sum_{k\in B}|\widehat f[k]|^2$.

Fix an integer $k_0\ge 1$ and constants $\alpha,\varepsilon>0$ with $\alpha>2\varepsilon$. Consider the two-layer network with fixed hidden features
$$
 z(x):=\big(\sqrt\varepsilon,\ \sqrt\alpha\cos(2\pi k_0 x),\ \sqrt\alpha\sin(2\pi k_0 x)\big)\in\mathbb R^3,
$$
trainable output weights $w\in\mathbb R^3$, and prediction $h(x;w):=w\cdot z(x)$. Train $w$ by gradient flow on the population square loss $\mathcal L(w)=\tfrac12\int\big(h(x;w)-f^*(x)\big)^2\,d\rho_X(x)$, with initialization $w_0=0$ (so $h_0\equiv 0$). A direct computation gives the function-valued gradient flow (valid in $L^2(\rho_X;\mathbb R)$):
$$
\partial_t h_t(x)= -\int K(x,x')\big(h_t(x')-f^*(x')\big)\,d\rho_X(x'),\quad K(x,x')=z(x)\cdot z(x')=\varepsilon+\alpha\cos\big(2\pi k_0(x-x')\big).
$$
Hence the residual $r_t:=h_t-f^*$ solves $\partial_t r_t=-T_K r_t$, where $(T_K g)(x)=\int K(x,x')g(x')\,d\rho_X(x')$.

The kernel $K$ is translation-invariant, so by Fourier diagonalization of convolution operators on $\mathbb T$, the eigenfunctions are $\{e_k\}_{k\in\mathbb Z}$ with eigenvalues given by the Fourier coefficients of $K$:
$$
\lambda_k=\widehat K[k]=\int_0^1\!\big(\varepsilon+\alpha\cos(2\pi k_0\tau)\big)e^{-2\pi i k\tau}\,d\tau
=\begin{cases}
\varepsilon,&k=0,\\[2pt]
\tfrac{\alpha}{2},&k=\pm k_0,\\[2pt]
0,&\text{otherwise.}
\end{cases}
$$
Choose a real-valued target with nontrivial low and high components,
$$
 f^*(x)=a\,e_0(x)+\tfrac{b}{2}\,e_{k_0}(x)+\tfrac{b}{2}\,e_{-k_0}(x)=a+b\cos(2\pi k_0 x),\qquad a,b\in\mathbb R\setminus\{0\}.
$$
With $h_0\equiv 0$, the Fourier coefficients of the residual satisfy for each $k\in\mathbb Z$,
$$
\widehat{r_t}[k]=e^{-\lambda_k t}\,\widehat{r_0}[k],\qquad r_0=-f^*.
$$
In particular, using $\widehat{r_0}[0]=-a$ and $\widehat{r_0}[\pm k_0]=-\tfrac{b}{2}$, define the residual energies on the low and high bands $B_{\mathrm{low}}=\{0\}$ and $B_{\mathrm{high}}=\{\pm k_0\}$ by
$$
\mathcal E_{\mathrm{low}}(t):=\sum_{k\in B_{\mathrm{low}}}|\widehat{r_t}[k]|^2,\qquad
\mathcal E_{\mathrm{high}}(t):=\sum_{k\in B_{\mathrm{high}}}|\widehat{r_t}[k]|^2.
$$
Then
$$
\mathcal E_{\mathrm{low}}(t)=e^{-2\varepsilon t}a^2,\qquad
\mathcal E_{\mathrm{high}}(t)=2\Big(e^{-\frac{\alpha}{2}t}\,\tfrac{|b|}{2}\Big)^2=e^{-\alpha t}\,\tfrac{b^2}{2}.
$$
Since $\mathcal E_{\mathrm{low}}(0)=a^2>0$ and $\mathcal E_{\mathrm{high}}(0)=\tfrac{b^2}{2}>0$, for any fixed $\delta\in(0,1)$ the hitting times are
$$
T_{\mathrm{low}}(\delta):=\inf\{t\ge 0:\ \mathcal E_{\mathrm{low}}(t)\le \delta\,\mathcal E_{\mathrm{low}}(0)\}=\frac{1}{2\varepsilon}\log\frac{1}{\delta},
\qquad
T_{\mathrm{high}}(\delta):=\inf\{t\ge 0:\ \mathcal E_{\mathrm{high}}(t)\le \delta\,\mathcal E_{\mathrm{high}}(0)\}=\frac{1}{\alpha}\log\frac{1}{\delta}.
$$
Because $\alpha>2\varepsilon$, we have $T_{\mathrm{high}}(\delta)<T_{\mathrm{low}}(\delta)$ for every $\delta\in(0,1)$. Thus the high-frequency band $\{\pm k_0\}$ is matched (in residual-energy terms) strictly earlier than the low-frequency band $\{0\}$, contradicting the conjectured universal low-to-high learning order.

The same ordering persists for discrete-time gradient descent (for small enough step size), replacing $e^{-\lambda t}$ by $(1-\eta\lambda)^t$.

Since this construction uses a (shallow) DNN, a standard square loss, and a valid dataset/initialization, the purported universality “across architectures/losses/datasets” is false. ∎