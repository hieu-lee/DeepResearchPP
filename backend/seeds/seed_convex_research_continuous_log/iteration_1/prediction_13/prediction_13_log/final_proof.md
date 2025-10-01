Proof. Let f(x)=\tfrac12 x^\top H x+b^\top x with H\succeq 0, and fix a constant stepsize \eta\ge 0 such that 2I-\eta H\succeq 0 (equivalently, 0\le\eta\le 2/\lambda_{\max}(H)). Run GD x_{k+1}=x_k-\eta\nabla f(x_k), and write g_k:=\nabla f(x_k)=H x_k+b.

Because f is quadratic, the exact descent identity holds for all x and all \eta\in\mathbb{R}:
$$
 f(x-\eta\nabla f(x))=f(x)-\eta\,\|\nabla f(x)\|^2+\tfrac{\eta^2}{2}\,\nabla f(x)^\top H\,\nabla f(x).
$$
Applying this at x=x_k gives
$$
\Delta_k:=f(x_k)-f(x_{k+1})=\frac{\eta}{2}\,g_k^\top(2I-\eta H)\,g_k.
$$
Since \eta\ge 0 and 2I-\eta H\succeq 0, we have \Delta_k\ge 0 for all k, so k\mapsto f(x_k) is nonincreasing.

Moreover, the gradients evolve linearly:
$$
 g_{k+1}=\nabla f(x_{k+1})=H(x_k-\eta g_k)+b=(I-\eta H)g_k.
$$
Therefore, using that polynomials in H commute,
$$
\Delta_{k+1}=\frac{\eta}{2}\,g_{k+1}^\top(2I-\eta H)g_{k+1}
=\frac{\eta}{2}\,g_k^\top(2I-\eta H)(I-\eta H)^2 g_k.
$$
Since H\succeq 0 and 2I-\eta H\succeq 0, every eigenvalue \lambda of H satisfies 0\le \eta\lambda\le 2, hence the spectrum of I-\eta H lies in [\!-1,1]. Thus
$$
0\preceq (I-\eta H)^2\preceq I.
$$
Because (2I-\eta H) and (I-\eta H)^2 commute and (2I-\eta H)\succeq 0, we obtain
$$
\Delta_{k+1}\;\le\;\frac{\eta}{2}\,g_k^\top(2I-\eta H)g_k\;=\;\Delta_k,
$$
so {\Delta_k} is nonincreasing and the optimization curve k\mapsto f(x_k) is convex. Equivalently, the discrete second differences are nonnegative; indeed,
$$
\Delta_k-\Delta_{k+1}
=\frac{\eta}{2}\,g_k^\top(2I-\eta H)\bigl[I-(I-\eta H)^2\bigr]g_k
=\frac{\eta^2}{2}\,g_k^\top(2I-\eta H)H(2I-\eta H)g_k\;\ge\;0,
$$
where we used $I-(I-\eta H)^2=\eta H(2I-\eta H)$ and that these matrices commute. This holds for every initialization $x_0$ and every such stepsize $\eta$.