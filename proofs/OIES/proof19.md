**Proof.** Let $C$ be the set of cyclic numbers (those $n\ge1$ with $\gcd(n,\varphi(n))=1$), and let $(c_n)_{n\ge1}$ be their increasing enumeration. Every prime is cyclic, and $2$ is the only even cyclic number.

We use a dyadic prime-gap lemma that guarantees two prime predecessors of a large cyclic $x$ inside $(x/2,x)$.

Lemma. For every $x\ge 50$ one has $\pi(x)-\pi(x/2)\ge 2$.

Proof of the lemma. By Nagura’s theorem, for every $y\ge25$ there is a prime in $(y,1.2y]$. Apply this with $y_1=x/2\ge25$ to get a prime $p_1\in(x/2,0.6x]$, and with $y_2=0.6x\ge25$ to get a prime $p_2\in(0.6x,0.72x]$. These intervals are disjoint and both lie in $(x/2,x]$, hence two distinct primes lie in $(x/2,x]$, proving $\pi(x)-\pi(x/2)\ge2$. ∎

Fix $n$ and write $x:=c_{n+2}$. If $x\ge50$, the lemma yields two primes in $(x/2,x)$, hence at least two cyclic numbers in $(x/2,x)$; together with $x$ (which is cyclic), the interval $(x/2,x]$ contains at least three cyclic numbers. Therefore the two largest cyclic numbers below $x$, namely $c_n$ and $c_{n+1}$, both lie in $(x/2,x)$, giving
$$
c_n+c_{n+1}>x=c_{n+2}.
$$
Thus $c_n+c_{n+1}>c_{n+2}$ holds for every $n$ with $c_{n+2}\ge50$.

It remains to verify the finite initial range with $c_{n+2}<50$. By Szele’s criterion (or the prime-factor reformulation), the cyclic numbers up to $117$ are exactly
$$
1,2,3,5,7,11,13,15,17,19,23,29,31,33,35,37,41,43,47,51,53,59,61,65,67,69,71,73,77,79,83,85,87,89,91,95,97,101,103,107,109,113,115.
$$
From this list one checks directly that the inequality holds for $n=3,4,\dots,21$:
\[
3+5>7,\ 5+7>11,\ 7+11>13,\ 11+13>15,\ 13+15>17,\ 15+17>19,\ 17+19>23,\ 19+23>29,
\]
\[
23+29>31,\ 29+31>33,\ 31+33>35,\ 33+35>37,\ 35+37>41,\ 37+41>43,\ 41+43>47,\ 43+47>51,
\]
\[
47+51>53,\ 51+53>59,\ 53+59>61.
\]
For the remaining $n$ with $c_{n+2}<118$ (hence also with $c_{n+2}<50$ included), we necessarily have $n\ge22$. Then $c_n\ge c_{22}=59$ and $c_{n+1}\ge c_{23}=61$, so
$$
c_n+c_{n+1}\ge59+61=120>c_{n+2}\qquad(\text{since }c_{n+2}\le115).
$$
Finally, $c_1+c_2=1+2=3=c_3$ and $c_2+c_3=2+3=5=c_4$, giving the stated equalities at $n=1,2$. For $n\ge3$ the inequality is strict because $2$ is the only even cyclic number, so $c_n,c_{n+1}$ are odd and $c_n+c_{n+1}$ is even, whereas $c_{n+2}$ is odd.

Therefore $c_n+c_{n+1}>c_{n+2}$ for all $n>2$, with equalities only at $n=1,2$. ∎