**Claim (Counterexample).** The stated conjecture is false: for $(m,n)=(5,7)$ one has
$$c_{35}=c_5\,c_7=91,$$
so neither the asserted inequality $c_{mn}<c_mc_n$ nor the listed “reverse strict inequality” holds.

**Proof.** Recall that $n$ is cyclic iff $n$ is squarefree and, writing $n=\prod p_i$, no prime divisor $p_i$ divides $p_j-1$ for any $i\ne j$. Also, $1$ is cyclic, all primes are cyclic, and the only even cyclic is $2$.

From these facts the increasing enumeration $(c_n)$ begins
$$c_1=1,\ c_2=2,\ c_3=3,\ c_4=5,\ c_5=7,\ c_6=11,\ c_7=13.$$
Hence $c_5c_7=7\cdot13=91$.

We now show $c_{35}=91$. Since $3\cdot5\cdot7=105>91$, every odd composite $\le91$ that is squarefree is a product $pq$ of two odd primes with $pq\le91$. By the characterization above, such $pq$ is cyclic iff $p\nmid(q-1)$ and $q\nmid(p-1)$. A complete check of possibilities gives:
- For $p=3$, the products $3q\le91$ are $15,21,33,39,51,57,69,87$; among these, $15,33,51,69,87$ are cyclic (since $3\nmid q-1$ for $q=5,11,17,23,29$), while $21,39,57$ are not (since $3\mid q-1$ for $q=7,13,19$).
- For $p=5$, the products $5q\le91$ are $35,55,65,85$; among these, $35,65,85$ are cyclic, while $55$ is not (since $5\mid 11-1$).
- For $p=7$, the products $7q\le91$ are $77,91$, and both are cyclic (as $7\nmid 10,12$ and $11,13\nmid 6$).
- For $p\ge11$, any $pq\le91$ forces $q\le\lfloor 91/11\rfloor=8$, impossible for an odd prime $q$.

Thus the odd composite cyclic numbers $\le91$ are exactly
$$15,33,35,51,65,69,77,85,87,91.$$
Including $1$, $2$, and the odd primes up to $91$ (namely $3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89$), the set of cyclic integers $\le91$ is
$$\{1,2,3,5,7,11,13,15,17,19,23,29,31,33,35,37,41,43,47,51,53,59,61,65,67,69,71,73,77,79,83,85,87,89,91\},$$
which has cardinality $2+23+10=35$. Therefore $c_{35}=91$.

Combining with $c_5=7$ and $c_7=13$, we get $c_{35}=91=c_5c_7$. Since $(m,n)=(5,7)$ lies among the listed exceptions in the conjecture (which demands the reverse strict inequality $c_{mn}>c_mc_n$ there), this equality contradicts the statement. Hence the conjecture is false. ∎