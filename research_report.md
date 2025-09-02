## Preface
This report explores discrete convexity and monotonicity properties of iterates in proximal and gradient-based algorithms for convex optimization, extending classical descent lemmas to richer quantitative bounds. We compile trusted smoothness and convexity results from the literature and present new theorems on discrete convexity of proximal point, proximal gradient, and gradient descent methods, each supported by succinct proofs.

## Table of Contents
- [Annotations](#annotations)
- [Trusted Results](#trusted-results)
- [Theorem 1 (Quantitative Discrete Convexity of Proximal Point Method)](#theorem-1-quantitative-discrete-convexity-of-proximal-point-method)
- [Theorem 2 (Convexity of Proximal Gradient Objective Sequence)](#theorem-2-convexity-of-proximal-gradient-objective-sequence)
- [Theorem 3 (Monotonicity of Gradient Descent Decrements)](#theorem-3-monotonicity-of-gradient-descent-decrements)
- [Theorem 4 (Discrete Convexity of Distances to the Solution Set)](#theorem-4-discrete-convexity-of-distances-to-the-solution-set)

## Annotations
- Function $f\colon\mathbb{R}^n\to\mathbb{R}$ is convex and $L$-smooth, i.e., for all $x,y\in\mathbb{R}^n$  
  $$\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|.$$  
- Gradient descent (GD) iterates:  
  $$x_{n+1}=x_n-\eta\nabla f(x_n),\quad \eta>0.$$  
- Gradient flow (GF) trajectory: $x(t)$ solves  
  $$\dot x(t)=-\nabla f(x(t)),\quad x(0)=x_0.$$  
- Proximal operator for proper closed convex $f\colon\mathbb R^n\to(-\infty,+\infty]$:  
  $$\mathrm{prox}_{\eta f}(x)=\arg\min_{z}\Bigl\{f(z)+\tfrac1{2\eta}\|z-x\|^2\Bigr\}.$$  
- Euclidean norm denoted by $\|\cdot\|$.  
- Optimal value $f^*=\inf_x f(x)$ and solution set $S=\arg\min f$ when nonempty.  

## Trusted Results
- Smoothness and convexity imply  
  $$f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\tfrac L2\|y-x\|^2.$$  
  Source: xjiajiahao.github.io/2018/04/21/Convex-Optimization-Cheatsheet/
- For convex $L$-smooth $f$ and $\eta\in(0,2/L)$, GD satisfies  
  $$f(x_{n+1})\le f(x_n)-\eta\Bigl(1-\tfrac{L\eta}{2}\Bigr)\|\nabla f(x_n)\|^2\le f(x_n).$$  
  Source: engineeringdevotion.com/optimization/gradient-descent-method.html
- For convex $L$-smooth $f$,  
  $$\langle\nabla f(x)-\nabla f(y),x-y\rangle\ge\tfrac1L\|\nabla f(x)-\nabla f(y)\|^2.$$  
  Source: samuelvaiter.com/a-first-look-at-convex-analysis/
- For convex $L$-smooth $f$, gradient flow decreases:  
  $$\tfrac{d}{dt}f(x(t))=-\|\nabla f(x(t))\|^2,\quad\dot f<0.$$  
  Source: blog.ml.cmu.edu/2019/10/25/path-length-bounds-for-gradient-descent/
- Gradient mapping $I-\eta\nabla f$ is nonexpansive for $\eta\in(0,2/L]$ (Baillon–Haddad).
- Proximal operator $\mathrm{prox}_{\eta g}$ is firmly nonexpansive.
- For strongly convex $f$, GF converges linearly:  
  $$f(x(t))-f(x^*)\le(f(x(0))-f(x^*))e^{-2\sigma t}.$$  
  Source: awibisono.github.io/2016/06/13/gradient-flow-gradient-descent.html

### Theorem 1 (Quantitative Discrete Convexity of Proximal Point Method)
Let $f\colon\mathbb R^n\to(-\infty,+\infty]$ be a proper closed convex function. For any fixed step size $\eta>0$, the proximal point iterates
$$
x_{n+1}=\arg\min_x\Bigl\{f(x)+\tfrac1{2\eta}\|x-x_n\|^2\Bigr\}
$$
satisfy, for all $n\ge1$, the quantitative discrete‐convexity bound
$$
f(x_{n-1})-2f(x_n)+f(x_{n+1})
\;\ge\;\tfrac1\eta\|x_{n+1}-2x_n+x_{n-1}\|^2
\;\ge\;0.
$$
**Proof.** Denote $\mathrm{prox}_{\eta f}=(I+\eta\,\partial f)^{-1}$. By monotonicity of $\partial f$, for any $u,v$ setting
$$
p=\mathrm{prox}_{\eta f}(u),\quad q=\mathrm{prox}_{\eta f}(v)
$$
we have $u-p\in\eta\,\partial f(p)$, $v-q\in\eta\,\partial f(q)$ and hence the firm‐nonexpansiveness inequality
$$
\|p-q\|^2\le\langle p-q,\,u-v\rangle.
$$
Taking $u=x_n$, $v=x_{n-1}$, $p=x_{n+1}$, $q=x_n$ gives
$$
\|x_{n+1}-x_n\|^2\le\langle x_{n+1}-x_n,\,x_n-x_{n-1}\rangle.
$$
By the polarization identity with $a=x_{n+1}-x_n$, $b=x_n-x_{n-1}$, one obtains
$$
\|x_{n-1}-x_n\|^2-\|x_n-x_{n+1}\|^2
\;\ge\;\|x_{n+1}-2x_n+x_{n-1}\|^2
\;\ge\;0.
$$
Optimality gives $x_{n-1}-x_n=\eta g_n$, $x_n-x_{n+1}=\eta g_{n+1}$ with $g_n\in\partial f(x_n)$, $g_{n+1}\in\partial f(x_{n+1})$. Convexity of $f$ yields
$$
f(x_{n-1})-f(x_n)\ge\tfrac1\eta\|x_{n-1}-x_n\|^2,\quad
f(x_n)-f(x_{n+1})\ge\tfrac1\eta\|x_n-x_{n+1}\|^2.
$$
Subtracting and invoking the previous inequality gives the claim. ∎

### Theorem 2 (Convexity of Proximal Gradient Objective Sequence)
Let $f$ be convex and $L$-smooth, and $g$ be convex. For the proximal gradient iterates
$$
x_{n+1}=\prox_{\eta g}(x_n-\eta\nabla f(x_n)),\quad\eta\in(0,2/L],
$$
define $F_n=f(x_n)+g(x_n)$. Then the sequence $(F_n)$ is convex in $n$: for all $n\ge1$,
$$
F_{n-1}-2F_n+F_{n+1}\ge0.
$$
**Proof.** Firm nonexpansiveness of $\prox_{\eta g}$ and Baillon–Haddad nonexpansiveness of $I-\eta\nabla f$ imply the composite mapping $G=\prox_{\eta g}\circ(I-\eta\nabla f)$ is nonexpansive. Hence $d_n=\|x_{n+1}-x_n\|$ is nonincreasing. Optimality at $x_{n+1}$ gives for some $v\in\partial g(x_{n+1})$
$$
\langle\nabla f(x_n),x_{n+1}-x_n\rangle
+\tfrac1\eta\|x_{n+1}-x_n\|^2
+\langle v,x_{n+1}-x_n\rangle=0.
$$
Convexity of $g$ yields $\langle v,x_{n+1}-x_n\rangle\ge g(x_{n+1})-g(x_n)$. Smoothness of $f$ gives
$$
f(x_{n+1})\le f(x_n)+\langle\nabla f(x_n),x_{n+1}-x_n\rangle+\tfrac L2\|x_{n+1}-x_n\|^2.
$$
Adding these inequalities yields
$$
F_{n+1}\le F_n-\Bigl(\tfrac1\eta-\tfrac L2\Bigr)\|x_{n+1}-x_n\|^2.
$$
Since $\eta\le2/L$, $\tfrac1\eta-\tfrac L2\ge0$, so
$$
F_n-F_{n+1}\ge\Bigl(\tfrac1\eta-\tfrac L2\Bigr)\|x_{n+1}-x_n\|^2.
$$
Therefore
$$
F_{n-1}-2F_n+F_{n+1}
=(F_{n-1}-F_n)-(F_n-F_{n+1})
\ge\Bigl(\tfrac1\eta-\tfrac L2\Bigr)(\|x_n-x_{n-1}\|^2-\|x_{n+1}-x_n\|^2)\ge0,
$$
concluding the proof. ∎

### Theorem 3 (Monotonicity of Gradient Descent Decrements)
Let $f\colon\mathbb R^n\to\mathbb R$ be convex and $L$-smooth, and let $\eta\in(0,2/L)$. Define GD iterates $x_{n+1}=x_n-\eta\nabla f(x_n)$ and successive decreases
$$
\Delta_n:=f(x_n)-f(x_{n+1}).
$$
Then $(\Delta_n)$ is nonincreasing: for all $n\ge1$,
$$
\Delta_n\le\Delta_{n-1},
\quad\text{equivalently}\quad
f(x_{n-1})-2f(x_n)+f(x_{n+1})\ge0.
$$
**Proof.** Co-coercivity gives
$$
\langle\nabla f(x)-\nabla f(y),x-y\rangle\ge\tfrac1L\|\nabla f(x)-\nabla f(y)\|^2.
$$
Thus for $T(x)=x-\eta\nabla f(x)$,
$$
\|T(x)-T(y)\|^2
\le\|x-y\|^2-(2\eta/L-\eta^2)\|\nabla f(x)-\nabla f(y)\|^2
\le\|x-y\|^2.
$$
By induction $\|x_{n+1}-x_n\|\le\|x_n-x_{n-1}\|$, so
$\|\nabla f(x_n)\|=\tfrac1\eta\|x_{n+1}-x_n\|\le\|\nabla f(x_{n-1})\|.$
L-smoothness gives the descent lemma
$$
f(x_{n+1})\le f(x_n)-\eta\Bigl(1-\tfrac{L\eta}{2}\Bigr)\|\nabla f(x_n)\|^2.
$$
Set $C=\eta(1-L\eta/2)>0$, then
$$
\Delta_n\ge C\|\nabla f(x_n)\|^2\le C\|\nabla f(x_{n-1})\|^2\le\Delta_{n-1}.
$$
Hence the decree of successive decreases is nonincreasing, yielding the stated discrete convexity. ∎

### Theorem 4 (Discrete Convexity of Distances to the Solution Set)
Let $f\colon\mathbb R^n\to\mathbb R$ be convex with $L$-Lipschitz gradient and assume its minimizer set $S=\arg\min f$ is nonempty. Fix $\eta\in(0,2/L]$ and define GD iterates $x_{n+1}=x_n-\eta\nabla f(x_n)$ and distances
$$
d_n=\mathrm{dist}(x_n,S)=\inf_{z\in S}\|x_n-z\|.
$$
Then for all $n\ge0$:
1) Monotonicity: $d_{n+1}^2\le d_n^2$.  
2) Discrete convexity: for $n\ge1$, $d_{n+1}^2-2d_n^2+d_{n-1}^2\ge0$.

**Proof.** Define $T(x)=x-\eta\nabla f(x)$. For $\eta\le2/L$, $T$ is $\alpha$-averaged with $\alpha=\eta L/2\in(0,1]$ and $c=(1-\alpha)/\alpha$. Standard inequality for $\alpha$-averaged maps gives for all $z\in S$:
$$
\|T(x)-z\|^2+c\|T(x)-x\|^2\le\|x-z\|^2.
$$
Taking $x=x_n$ and infimizing over $z\in S$ yields
$$
d_{n+1}^2+c\|x_{n+1}-x_n\|^2\le d_n^2,
$$
which implies $d_{n+1}^2\le d_n^2$. Applying the same at the previous step and subtracting gives
$$
d_{n+1}^2-2d_n^2+d_{n-1}^2\ge c\bigl(\|x_n-x_{n-1}\|^2-\|x_{n+1}-x_n\|^2\bigr).
$$
Since $\|x_{n+1}-x_n\|\le\|x_n-x_{n-1}\|$, the right‐hand side is nonnegative, proving the discrete convexity. ∎