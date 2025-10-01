Proof (by contradiction). Assume that for every \mu-strongly convex and L-smooth function f and every \eta\in(0,2/L), along gradient descent the ratios r_n:=\tfrac{f(x_{n+1})-f_\star}{f(x_n)-f_\star} are nonincreasing.

Consider the quadratic in dimension 2:
$$
 f(x)=\tfrac12\big(\mu x_1^2+L x_2^2\big),\qquad 0<\mu<L.
$$
Then f is \mu-strongly convex and L-smooth, with unique minimizer x_\star=0 and f_\star=f(x_\star)=0. Gradient descent with stepsize \eta\in(0,2/L) evolves coordinate-wise as
$$
 x_{n+1,1}=(1-\eta\mu)\,x_{n,1},\qquad x_{n+1,2}=(1-\eta L)\,x_{n,2}.
$$
Let $m_1:=1-\eta\mu$, $m_2:=1-\eta L$, and $\rho_i:=m_i^2\in[0,1)$, $i=1,2$. For any initialization $x_0=(a,b)$ with $a,b\ne0$, set $c_1:=\mu a^2>0$, $c_2:=L b^2>0$, and define $a_n:=c_1\rho_1^{\,n}+c_2\rho_2^{\,n}$. Then
$$
 f(x_n)-f_\star=\tfrac12 a_n,\qquad r_n=\frac{a_{n+1}}{a_n}.
$$
By Cauchy–Schwarz,
$$
 a_{n+1}^2=\Big(\sum_{i=1}^2\sqrt{c_i}\,\rho_i^{\,n/2}\cdot\sqrt{c_i}\,\rho_i^{\,n/2+1}\Big)^2\le\Big(\sum_{i=1}^2 c_i\rho_i^{\,n}\Big)\Big(\sum_{i=1}^2 c_i\rho_i^{\,n+2}\Big)=a_n a_{n+2},
$$
with strict inequality whenever $\rho_1\ne\rho_2$ and $c_1,c_2>0$. Hence $r_n\le r_{n+1}$ for all n, and in fact $r_n<r_{n+1}$ for all n under $\rho_1\ne\rho_2$ and $a,b\ne0$. This contradicts the assumed nonincreasing property. Therefore, there exist \mu, L, \eta, f, and x_0 for which \{r_n\} is strictly increasing.

Finally, in this quadratic example,
- if $\rho_1\ne\rho_2$ and, say, $\rho_2>\rho_1$, then
$$
 r_n=\frac{c_1\rho_1^{\,n+1}+c_2\rho_2^{\,n+1}}{c_1\rho_1^{\,n}+c_2\rho_2^{\,n}}=\rho_2\,\frac{c_2+c_1(\rho_1/\rho_2)^{n+1}}{c_2+c_1(\rho_1/\rho_2)^n}\longrightarrow \rho_2=\max\{\rho_1,\rho_2\};
$$
- if $\rho_1=\rho_2=:\rho$, then $r_n\equiv\rho$.

Since $\lambda\mapsto |1-\eta\lambda|^2$ is convex on $[\mu,L]$, its maximum over $[\mu,L]$ is attained at an endpoint, so
$$
 q=\max_{\lambda\in[\mu,L]}|1-\eta\lambda|^2=\max\{|1-\eta\mu|^2,|1-\eta L|^2\}=\max\{\rho_1,\rho_2\}.
$$
Thus $\lim_{n\to\infty} r_n=q$ in this example. ∎