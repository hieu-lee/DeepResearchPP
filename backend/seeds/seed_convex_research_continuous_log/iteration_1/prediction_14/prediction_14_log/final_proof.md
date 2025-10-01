Consider f(x)=\tfrac{L}{2}\|x\|^2, which is convex and L-smooth, and fix any x_0\ne 0. For a stepsize \eta\in(1/L,2/L), gradient descent yields
\[
 x_{n+1}=x_n-\eta\nabla f(x_n)=x_n-\eta L x_n=(1-\eta L)x_n=:\rho x_n,
\]
so that \(\rho\in(-1,0)\), \(x_n=\rho^n x_0\), \(g_n:=\nabla f(x_n)=L\rho^n x_0\), and \(f_n:=f(x_n)=\tfrac{L}{2}\rho^{2n}\|x_0\|^2\).

The quadratic model at \(x_n\) is
\[
 Q_n(y)=f_n+\langle g_n,y-x_n\rangle+\tfrac{1}{2\eta}\|y-x_n\|^2.
\]
Evaluating at \(y=x_{n+1}=x_n-\eta g_n\),
\[
 Q_n(x_{n+1})=f_n-\eta\|g_n\|^2+\tfrac{\eta}{2}\|g_n\|^2=f_n-\tfrac{\eta}{2}\|g_n\|^2.
\]
Since \(\|g_n\|^2=L^2\|x_n\|^2=2L f_n\), we obtain
\[
 Q_n(x_{n+1})=f_n-\eta L f_n=(1-\eta L)f_n=\rho f_n,\qquad f_{n+1}=\rho^2 f_n.
\]
Hence
\[
 \delta_n=Q_n(x_{n+1})-f_{n+1}=\rho f_n-\rho^2 f_n=\rho(1-\rho)f_n=\frac{\eta L^2}{2}\,\rho^{2n+1}\|x_0\|^2.
\]
Because \(\rho\in(-1,0)\), we have \(\delta_n<0\) for all n. Moreover,
\[
 \delta_{n+1}-\delta_n=(\rho^2-1)\,\delta_n>0,
\]
since \(\rho^2-1<0\) and \(\delta_n<0\). Thus {\delta_n} is strictly increasing, so it is not nonincreasing.

For second differences,
\[
 \delta_{n+2}-2\delta_{n+1}+\delta_n=(1-\rho^2)^2\,\delta_n<0,
\]
because \(1-\rho^2>0\) and \(\delta_n<0\). Therefore the sequence n\mapsto\delta_n is strictly concave, in particular not convex. ∎