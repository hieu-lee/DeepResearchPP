Proof. Assume, for contradiction, that there exists a stepsize $\eta\in(0,\tfrac{2}{L})$ such that for every convex $L$-smooth function $f$ and every initialization, gradient descent with this $\eta$ produces a sequence $\{\|g_n\|\}$ whose forward differences are nonincreasing, i.e., $\|g_n\|-\|g_{n+1}\|\ge \|g_{n+1}\|-\|g_{n+2}\|$ for all $n$.

Fix such $\eta$ and $L>0$. Choose any $g_0>0$ and any $x_0\in\mathbb{R}$. Define
$$x_1:=x_0-\eta g_0,\qquad x_2:=x_1-\eta g_0,$$
and define $f':\mathbb{R}\to\mathbb{R}$ by
$$
 f'(x):=\begin{cases}
 g_0, & x\ge x_1,\\[4pt]
 g_0+L(x-x_1), & x\in[x_2,x_1],\\[4pt]
 g_2, & x\le x_2,
 \end{cases}
$$
where $g_2:=g_0+L(x_2-x_1)=g_0-L\eta g_0=(1-\eta L)g_0$. Then $f'$ is continuous, nondecreasing, and $L$-Lipschitz (its a.e. derivative takes values in $\{0,L\}$). Hence its antiderivative $f\in C^{1,1}$ is convex and $L$-smooth.

Run gradient descent $x_{n+1}=x_n-\eta f'(x_n)$ and denote $g_n:=f'(x_n)$. By construction, $x_1=x_0-\eta g_0$ and $f'(x)\equiv g_0$ on $[x_1,\infty)$, so $g_0=f'(x_0)$ and $g_1=f'(x_1)=g_0$. Moreover, on $[x_2,x_1]$ we have $f''\equiv L$ a.e., hence
$$
 g_2=f'(x_2)=f'(x_1)+\int_{x_1}^{x_2}L\,dt=g_0-L(x_1-x_2)=g_0-L\eta g_1=(1-\eta L)g_1.
$$
Therefore
$$
 \|g_0\|-\|g_1\|=g_0-g_0=0,\qquad
 \|g_1\|-\|g_2\|=g_0-|1-\eta L|\,g_0=(1-|1-\eta L|)g_0.
$$
Because $0<\eta L<2$, we have $|1-\eta L|<1$, so $\|g_1\|-\|g_2\|>0=\|g_0\|-\|g_1\|$. Thus the forward differences are not nonincreasing at $n=0$, contradicting the assumption.

Hence no such $\eta$ exists. Equivalently, for every $\eta\in(0,\tfrac{2}{L})$ there exist a convex $L$-smooth $f$ and an initialization for which the forward differences of $\{\|g_n\|\}$ increase at $n=0$ (indeed, $\|g_0\|-\|g_1\|<\|g_1\|-\|g_2\|$). ∎