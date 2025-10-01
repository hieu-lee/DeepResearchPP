\begin{proof}
Let $f:\mathbb{R}^d\to\mathbb{R}$ be convex and $L$-smooth, and run gradient descent with constant step size $\eta\in(0,\tfrac{2}{L}]$:
$$
 x_{n+1}=x_n-\eta\nabla f(x_n),\qquad f_n:=f(x_n),\qquad g_n:=\nabla f(x_n).
$$
Define $s_n:=\tfrac12(f_n+f_{n+1})$.

1) Monotonicity of $(s_n)$. By the descent lemma, for any $k\ge0$,
$$
 f_{k+1}\;\le\; f_k-\tfrac{\eta}{2}(2-\eta L)\,\|g_k\|^2\;\le\; f_k.
$$
Hence $(f_n)$ is nonincreasing, so $f_{n+2}\le f_n$ and therefore
$$
 s_n-s_{n+1}=\tfrac12\,(f_n-f_{n+2})\;\ge\;0.
$$
Thus $(s_n)$ is nonincreasing.

2) Convexity of $(s_n)$. The sequence $(s_n)$ is convex iff
$$
 s_n-s_{n+1}=\tfrac12\,(f_n-f_{n+2})\;\ge\;\tfrac12\,(f_{n+1}-f_{n+3})=s_{n+1}-s_{n+2},
$$
that is, iff for all $n\ge0$,
$$
 f_n-f_{n+2}\;\ge\; f_{n+1}-f_{n+3}. \tag{1}
$$
Apply the descent lemma at indices $n$ and $n+2$ and subtract:
$$
 f_{n+1}-f_{n+3}\;\le\;\big(f_n-f_{n+2}\big)\;-
 \tfrac{\eta}{2}(2-\eta L)\big(\|g_n\|^2-\|g_{n+2}\|^2\big).
$$
Equivalently,
$$
 \big(f_n-f_{n+2}\big)-\big(f_{n+1}-f_{n+3}\big)\;\ge\;\tfrac{\eta}{2}(2-\eta L)\big(\|g_n\|^2-\|g_{n+2}\|^2\big). \tag{2}
$$
Since $f$ is convex and $L$-smooth, $\nabla f$ is $1/L$-cocoercive (Baillon–Haddad):
$$
 \langle g_{k}-g_{k+1},\, x_k-x_{k+1}\rangle\;\ge\;\tfrac1L\,\|g_{k}-g_{k+1}\|^2.
$$
Using $x_k-x_{k+1}=\eta g_k$ gives $\langle g_k, g_k-g_{k+1}\rangle\ge\tfrac{1}{\eta L}\|g_k-g_{k+1}\|^2$. Hence
$$
\|g_{k+1}\|^2 = \|g_k\|^2 - 2\langle g_k,g_k-g_{k+1}\rangle + \|g_k-g_{k+1}\|^2
\le \|g_k\|^2 - \Big(\tfrac{2}{\eta L}-1\Big)\|g_k-g_{k+1}\|^2 \le \|g_k\|^2,
$$
for $\eta\le 2/L$. Thus $\|g_{k+1}\|\le\|g_k\|$, and in particular $\|g_{n+2}\|\le\|g_n\|$. With $(2-\eta L)\ge0$, the right-hand side of (2) is nonnegative, and (1) follows. (When $\eta=2/L$, the factor $(2-\eta L)$ is zero, so (1) follows from (2) even without using the monotonicity of $\|g_k\|$.)

Therefore $(s_n)$ is convex and nonincreasing for all $\eta\in(0,\tfrac{2}{L}]$.
\end{proof}