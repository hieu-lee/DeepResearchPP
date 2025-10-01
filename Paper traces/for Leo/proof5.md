**Proof.**
Write $L(x):=\log_3 x$ and recall Pollack’s Poincaré expansion (as $x\to\infty$)
$$
C(x)=e^{-\gamma}x\Big(\frac{1}{L(x)}-\frac{\gamma}{L(x)^2}+O\Big(\frac{1}{L(x)^3}\Big)\Big).
$$
Set
$$
\ell_1(x):=e^{-\gamma}\Big(\frac{1}{L(x)}-\frac{\gamma}{L(x)^2}\Big),\qquad a(x):=x\,\ell_1(x).
$$
We first prove the fixed-scale increment asymptotic.

Claim 1. For each fixed $\lambda>0$,
$$
\frac{C(\lambda x)-C(x)}{a(x)(\lambda-1)}\;\longrightarrow\;1\qquad (x\to\infty).
$$

Proof of Claim 1. Write $L:=L(x)$ and $L_\lambda:=L(\lambda x)$. Then
$$
C(\lambda x)-C(x)
=e^{-\gamma}x\Big(\lambda\Big(\frac{1}{L_\lambda}-\frac{\gamma}{L_\lambda^2}\Big)
-\Big(\frac{1}{L}-\frac{\gamma}{L^2}\Big)\Big)\;+
\;O\Big(\frac{x}{L^3}\Big),
$$
uniformly for $\lambda$ in compact subsets of $(0,\infty)$. Set $f(u):=u^{-1}-\gamma u^{-2}$. Then
$$
\lambda f(L_\lambda)-f(L)=(\lambda-1)f(L)+\lambda\bigl(f(L_\lambda)-f(L)\bigr).
$$
To handle $L_\lambda-L$, note that with $\log_1 x=\log x$ and $\log_2 x=\log\log x$,
$$
L_\lambda-L
=\log\Bigl(1+\frac{\log\bigl(1+\tfrac{\log\lambda}{\log x}\bigr)}{\log_2 x}\Bigr)
=:\Delta.
$$
Since $\lambda$ is fixed, $\log\lambda$ is constant and hence
$$
\Delta=O\!\Big(\frac{1}{\log x\,\log_2 x}\Big).
$$
By Taylor’s theorem,
$$
f(L_\lambda)-f(L)=f'(L)\,\Delta+O\Big(\frac{\Delta^2}{L^3}\Big),\qquad f'(L)=-\frac{1}{L^2}+\frac{2\gamma}{L^3}.
$$
Therefore
$$
C(\lambda x)-C(x)=(\lambda-1)a(x)\;+
\;e^{-\gamma}x\,\lambda f'(L)\,\Delta
\;+
\;O\Big(\frac{x\,\Delta^2}{L^3}\Big)
\;+
\;O\Big(\frac{x}{L^3}\Big).
$$
Divide by $a(x)(\lambda-1)=e^{-\gamma}x(\lambda-1)f(L)$. Since $f(L)\asymp 1/L$, $f'(L)=O(1/L^2)$, and $\Delta=O(1/(\log x\,\log_2 x))$, we obtain
$$
\frac{e^{-\gamma}x\,\lambda f'(L)\,\Delta}{a(x)(\lambda-1)}
\ll \frac{\Delta}{L}\;=\;O\!\Big(\frac{1}{\log x\,\log_2 x\,L}\Big)\to 0,
$$
while
$$
\frac{x\,\Delta^2/L^3}{a(x)(\lambda-1)}\ll \frac{\Delta^2}{L^2}\to 0,
\qquad
\frac{x/L^3}{a(x)(\lambda-1)}\ll \frac{1}{L^2}\to 0.
$$
Hence the ratio tends to $1$, proving Claim 1. ∎

By Claim 1, $C$ belongs to de Haan’s class of $\Pi$-variation of index $1$ with characteristic $\varphi(\lambda)=\lambda-1$ and auxiliary function $a(x)$ (see Bingham–Goldie–Teugels, Regular Variation, §3.7). The local increment theorem there yields
$$
C(x+h)-C(x)\sim a(x)\,\varphi\!\Big(1+\frac{h}{x}\Big)\sim a(x)\,\frac{h}{x}
\qquad (x\to\infty),\quad h=o(x),
$$
using $\varphi'(1)=1$ for the second asymptotic.

Apply this with $x=n^2$ and $h=(n+1)^2-n^2=2n+1\sim 2n$ to get
$$
C\big((n+1)^2\big)-C(n^2)\sim (2n)\,\ell_1(n^2)
=(2n)\,e^{-\gamma}\Big(\frac{1}{L(n^2)}-\frac{\gamma}{L(n^2)^2}\Big).
$$
Now set $L:=\log_3 n$. Then
$$
L(n^2)=\log_3(n^2)=\log\bigl(\log(2\log n)\bigr)=\log\bigl(\log_2 n+\log 2\bigr)
= L + \delta,
$$
where
$$
\delta=\log\Bigl(1+\frac{\log 2}{\log_2 n}\Bigr)=O\!\Big(\frac{1}{\log_2 n}\Big).
$$
Write $\ell_1(n^2)=e^{-\gamma}f(L(n^2))$ with $f(u)=u^{-1}-\gamma u^{-2}$. Since $f'(u)=-u^{-2}+2\gamma u^{-3}=O(1/u^2)$, the mean value theorem gives
$$
\ell_1(n^2)=e^{-\gamma}\Big(f(L)+O\Big(\frac{\delta}{L^2}\Big)\Big)
=e^{-\gamma}\Big(\frac{1}{L}-\frac{\gamma}{L^2}\Big)\Big(1+O\Big(\frac{\delta}{L}\Big)\Big).
$$
Because $\delta/L=O\big(1/(\log_2 n\,\log_3 n)\big)=o(1)$, we may replace $L(n^2)$ by $L=\log_3 n$ inside $\ell_1$ at a relative $o(1)$ cost. Therefore
$$
C\big((n+1)^2\big)-C(n^2)
\sim (2n)\,e^{-\gamma}\Big(\frac{1}{\log_3 n}-\frac{\gamma}{(\log_3 n)^2}\Big)
=\frac{2n}{e^{\gamma}\,\log_3 n}\Big(1-\frac{\gamma}{\log_3 n}\Big),
$$
which is exactly the asserted asymptotic. ∎