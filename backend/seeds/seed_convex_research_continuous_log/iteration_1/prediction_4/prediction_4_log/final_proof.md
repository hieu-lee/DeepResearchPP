Work in one dimension and fix $f(x)=\tfrac12 x^2$, which is convex and $1$-smooth. For any stepsize $\eta\in[\tfrac32,2)$, let $\rho:=1-\eta\in(-1,-\tfrac12]$ and run gradient descent
$$
x_{n+1}=x_n-\eta\nabla f(x_n)=(1-\eta)x_n=\rho\,x_n,
$$
so $x_n=\rho^n x_0$ for all $n\ge0$. The Cesàro averages are
$$
\bar x_n=\frac1{n+1}\sum_{k=0}^n x_k=x_0\,\frac{1-\rho^{n+1}}{(n+1)(1-\rho)}=:x_0\,s_n.
$$
Because $|\rho|<1$, we have $1-\rho>0$ and $1-\rho^{n+1}>0$, hence $s_n>0$ for all $n$.

Consequently,
$$
f(\bar x_n)=\tfrac12 x_0^2 s_n^2.
$$
For a real sequence, convexity is equivalent to nondecreasing forward differences $\Delta_n:=f(\bar x_{n+1})-f(\bar x_n)$. Here
$$
\Delta_n=\tfrac12 x_0^2\big(s_{n+1}^2-s_n^2\big)=\tfrac12 x_0^2\,(s_{n+1}-s_n)(s_{n+1}+s_n),
$$
so $\operatorname{sign}(\Delta_n)=\operatorname{sign}(s_{n+1}-s_n)$ because $s_{n+1}+s_n>0$.

Compute
$$
s_1=\frac{1+\rho}{2},\quad s_2=\frac{1+\rho+\rho^2}{3},\quad s_3=\frac{1+\rho+\rho^2+\rho^3}{4},
$$
so
$$
s_2-s_1=\frac{2\rho^2-\rho-1}{6}=\frac{(2\rho+1)(\rho-1)}{6},\qquad
s_3-s_2=\frac{3\rho^3-\rho^2-\rho-1}{12}=\frac{(\rho-1)(3\rho^2+2\rho+1)}{12}.
$$
For $\rho\in(-1,-\tfrac12]$, we have $\rho-1<0$, $2\rho+1\le0$, and $3\rho^2+2\rho+1>0$ (its discriminant is $4-12<0$), hence
$$
s_2-s_1\ge0\quad\text{and}\quad s_3-s_2<0.
$$
Therefore $\Delta_1\ge0$ while $\Delta_2<0$, so the forward differences are not nondecreasing. It follows that the sequence $n\mapsto f(\bar x_n)$ is not convex. This conclusion holds for every nonzero $x_0$ because $x_0^2$ is a positive factor in all $\Delta_n$.

Finally, the gradients are $g_n=\nabla f(x_n)=x_n=\rho^n x_0$, so $\|g_n\|=|\rho|^n\,|x_0|>0$ for all $n$ and $\|g_n\|$ is strictly decreasing to $0$ since $|\rho|<1$. Thus the nonconvexity occurs even though the gradient norms are never zero and decay strictly.