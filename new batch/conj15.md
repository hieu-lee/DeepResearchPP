**Claim.** For every $k\in\mathbb{N}$ there exists $N(k)$ such that for all $n>N(k)$ both half-square intervals $[n^2-n,n^2]$ and $[n^2,n^2+n]$ contain at least $k$ primes; equivalently, $N^{-}_{\mathcal P}(n)\ge k$ and $N^{+}_{\mathcal P}(n)\ge k$ for all $n>N(k)$.

**Proof.** Fix $\theta=23/42>1/2$. By the Iwaniec–Pintz theorem, there exists $X_\theta\ge 2$ such that for all $x\ge X_\theta$ and all $y\le x^{\theta}$,
\[
\pi(x)-\pi(x-y)\;>\;\frac{y}{100\,\log x}.
\]

Apply this with $x=n^2$ and $y=n$. Since $\theta>1/2$, we have $y=n\le (n^2)^{1/2}\le (n^2)^{\theta}$, so for all sufficiently large $n$ (namely $n\ge \sqrt{X_\theta}$),
\[
N^{-}_{\mathcal P}(n)
\;=\;\pi(n^2)-\pi(n^2-n)
\;>\;\frac{n}{100\,\log(n^2)}
\;=\;\frac{n}{200\,\log n}.
\]
For the right half-interval, set $x'=n^2+n$ and $y'=n$, so that $[n^2,n^2+n]=[x'-y',x']$. Again $y'=n\le (n^2+n)^{1/2}\le (n^2+n)^{\theta}$ for $\theta>1/2$, hence for all sufficiently large $n$ (so that $x'\ge X_\theta$),
\[
N^{+}_{\mathcal P}(n)
\;=\;\pi(x')-\pi(x'-y')
\;>\;\frac{n}{100\,\log(n^2+n)}.
\]
For $n\ge 2$ one has $\log(n^2+n)=\log n+\log(n+1)\le 2\log n+\log 2\le 3\log n$, whence
\[
\frac{1}{\log(n^2+n)}\;\ge\;\frac{1}{3\,\log n},
\]
and therefore, for all sufficiently large $n$,
\[
N^{-}_{\mathcal P}(n)\;>\;\frac{n}{200\,\log n}
\quad\text{and}\quad
N^{+}_{\mathcal P}(n)\;>\;\frac{n}{300\,\log n}.
\]
Thus there exists $N_0$ such that for all $n\ge N_0$,
\[
\min\bigl\{N^{-}_{\mathcal P}(n),\,N^{+}_{\mathcal P}(n)\bigr\}
\;>\;\frac{n}{300\,\log n}.
\]
Since $n/(300\log n)\to\infty$ as $n\to\infty$, for any given $k\in\mathbb{N}$ we may choose $N(k)\ge N_0$ such that $n/(300\log n)\ge k$ for all $n\ge N(k)$. It follows that for all $n\ge N(k)$,
\[
N^{-}_{\mathcal P}(n)\ge k\quad\text{and}\quad N^{+}_{\mathcal P}(n)\ge k,
\]
as desired. ∎