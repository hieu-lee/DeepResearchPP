**Proof.** Let $C(x):=\#\{n\le x:\gcd(n,\varphi(n))=1\}$, and write
\[
S(x):=\sum_{c\le x} c,\qquad J(x):=\sum_{c\le x} \log c,
\]
where the sums range over cyclic numbers $c$. By Abel’s summation (partial summation), for $x\ge 1$ we have
\[
S(x)=x\,C(x)-\int_1^x C(t)\,dt,\qquad J(x)=C(x)\log x-\int_1^x \frac{C(t)}{t}\,dt.
\]
It is known that (Erdős; Pollack’s refinement) 
\[
C(x)\sim \frac{e^{-\gamma}x}{\log_3 x}\qquad(x\to\infty),
\]
where $\log_3 x:=\log\log\log x$. Since $\log_3 x$ is slowly varying, Karamata’s integral theorem yields
\[
\int_1^x \frac{C(t)}{t}\,dt\sim e^{-\gamma}\int_1^x \frac{dt}{\log_3 t}\sim \frac{e^{-\gamma}x}{\log_3 x}\sim C(x),
\]
\[
\int_1^x C(t)\,dt\sim e^{-\gamma}\int_1^x \frac{t\,dt}{\log_3 t}\sim \frac{e^{-\gamma}x^2}{2\log_3 x}\sim \frac{x\,C(x)}{2}.
\]
Substituting into the Abel identities gives the two asymptotics
\[
S(x)\sim \frac{x\,C(x)}{2},\qquad J(x)\sim C(x)\,(\log x-1)\qquad(x\to\infty).
\]
Let $(c_n)_{n\ge 1}$ be the strictly increasing enumeration of cyclic numbers. Then $C(c_n)=n$, and
\[
A_n:=\frac{1}{n}\sum_{k=1}^n c_k=\frac{S(c_n)}{C(c_n)}\sim \frac{c_n}{2},
\]
\[
G_n:=\exp\!\Big(\frac{1}{n}\sum_{k=1}^n \log c_k\Big)=\exp\!\Big(\frac{J(c_n)}{C(c_n)}\Big)\sim \exp(\log c_n-1)=\frac{c_n}{e}.
\]
Therefore
\[
\frac{A_n}{G_n}\sim \frac{c_n/2}{c_n/e}=\frac{e}{2},\qquad n\to\infty,
\]
which proves
\[
\lim_{n\to\infty}\frac{(c_1+\cdots+c_n)/n}{(c_1c_2\cdots c_n)^{1/n}}=\frac{e}{2}.
\]
∎