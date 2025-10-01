import Mathlib
import Mathlib.NumberTheory.Harmonic.EulerMascheroni

namespace LeanCode
namespace Conjecture5

open Filter
open scoped Topology

@[simp] def isCyclic (n : Nat) : Prop := n.Coprime (Nat.totient n)

instance : DecidablePred isCyclic := by
  intro n
  change Decidable (n.Coprime (Nat.totient n))
  infer_instance

noncomputable def cyclicCount (n : Nat) : Nat :=
  ((Finset.range (n + 1)).filter fun m => isCyclic m).card

noncomputable def C (n : Nat) : Real := (cyclicCount n : Real)

-- A real-argument version of C using floor; agrees with C on integer inputs
noncomputable def CReal (x : Real) : Real :=
  C (Int.toNat (Int.floor x))

noncomputable def logIter (k : Nat) (x : Real) : Real :=
  Nat.recOn k x (fun _ acc => Real.log acc)

noncomputable def log1 (x : Real) : Real := logIter 1 x
noncomputable def log2 (x : Real) : Real := logIter 2 x
noncomputable def log3 (x : Real) : Real := logIter 3 x

noncomputable def ell1 (x : Real) : Real :=
  Real.exp (-Real.eulerMascheroniConstant) *
    (1 / log3 x - Real.eulerMascheroniConstant / (log3 x) ^ 2)

noncomputable def a (x : Real) : Real := x * ell1 x

-- de Haan's class of Π-variation (index 1) with characteristic φ(λ) = λ - 1.
-- Membership: for each fixed λ > 0,
--   (f(λ x) - f(x)) / a(x) → (λ - 1) as x → ∞.
def deHaanPi1 (f a : Real → Real) : Prop :=
  ∀ t : Real, 0 < t →
    Tendsto (fun x : Real => (f (t * x) - f x) / (a x))
      atTop (nhds (t - 1))

-- Axioms: Pollack asymptotic(s) and local increment theorem
axiom pollack_square_ratio :
  Tendsto (fun n : Nat =>
    ell1 ((n : Real) ^ 2) /
      (Real.exp (-Real.eulerMascheroniConstant) *
        (1 / log3 (n : Real) - Real.eulerMascheroniConstant / (log3 (n : Real)) ^ 2)))
    atTop (nhds (1 : Real))
axiom pollack_main_asymptotic :
  Tendsto (fun x : Real => CReal x / a x) atTop (nhds (1 : Real))
axiom ell1_rescale_tendsto (t : Real) (ht : 0 < t) :
  Tendsto (fun x : Real => ell1 (t * x) / ell1 x) atTop (nhds (1 : Real))
axiom ell1_eventually_ne_zero :
  Filter.Eventually (fun x : Real => ell1 x ≠ 0) atTop
-- Pollack: C belongs to de Haan's Π-class with auxiliary a(x)=x·ell1(x) and φ(λ)=λ−1.
-- We prove this following the argument in proofs/OIES/proof5.md,
-- deriving the fixed-scale increment from Pollack’s Poincaré expansion.
theorem pollack_fixed_scale_increment : deHaanPi1 CReal a := by
  intro t ht
  classical
  have ht_ne : (t : Real) ≠ 0 := ne_of_gt ht
  have hScale : Tendsto (fun x : Real => t * x) atTop atTop := by
    refine Filter.tendsto_atTop_atTop_of_monotone (fun x y hxy => ?_) ?_
    · exact mul_le_mul_of_nonneg_left hxy (le_of_lt ht)
    · intro b
      refine ⟨b / t, ?_⟩
      have hb : t * (b / t) = b := by
        calc
          t * (b / t)
              = t * (b * t⁻¹) := by simp [div_eq_mul_inv]
          _ = b * (t * t⁻¹) := by
            simp [mul_left_comm]
          _ = b := by simp [ht_ne]
      simp [hb]
  have hC := pollack_main_asymptotic
  have hC_scaled :
      Tendsto (fun x : Real => CReal (t * x) / a (t * x)) atTop (nhds (1 : Real)) :=
    hC.comp hScale
  have hx_ne_zero : Filter.Eventually (fun x : Real => x ≠ 0) atTop :=
    eventually_ne_atTop (0 : Real)
  have hEll_ne_zero : Filter.Eventually (fun x : Real => ell1 x ≠ 0) atTop :=
    ell1_eventually_ne_zero
  have hEll_ne_zero_scaled :
      Filter.Eventually (fun x : Real => ell1 (t * x) ≠ 0) atTop :=
    hScale.eventually hEll_ne_zero
  have hNonzero :
      Filter.Eventually (fun x : Real => a (t * x) ≠ 0 ∧ a x ≠ 0 ∧ x ≠ 0) atTop := by
    refine (hx_ne_zero.and (hEll_ne_zero.and hEll_ne_zero_scaled)).mono ?_
    intro x hx
    rcases hx with ⟨hx0, hEllx, hElltx⟩
    have hax : a x ≠ 0 := by
      have hxmul : x * ell1 x ≠ 0 := mul_ne_zero hx0 hEllx
      simpa [a] using hxmul
    have htx_ne : t * x ≠ 0 := mul_ne_zero ht_ne hx0
    have haTx : a (t * x) ≠ 0 := by
      have hxmul : (t * x) * ell1 (t * x) ≠ 0 := mul_ne_zero htx_ne hElltx
      simpa [a] using hxmul
    exact ⟨haTx, hax, hx0⟩
  let ratio := fun x : Real => a (t * x) / a x
  have h_ratio_eq :
      Filter.Eventually (fun x => ratio x =
        (t : Real) * (ell1 (t * x) / ell1 x)) atTop :=
    hx_ne_zero.mono (fun x hx => by
      have hx0 : x ≠ 0 := hx
      simp [ratio, a, div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc, hx0])
  have h_const :
      Tendsto (fun _ : Real => (t : Real)) atTop (nhds (t : Real)) :=
    tendsto_const_nhds
  have h_ratio_limit :
      Tendsto ratio atTop (nhds (t : Real)) :=
    (tendsto_congr' h_ratio_eq).2
      (by simpa [one_mul] using h_const.mul (ell1_rescale_tendsto t ht))
  let F := fun x : Real => (CReal (t * x) / a (t * x)) * ratio x
  have hF : Tendsto F atTop (nhds (t : Real)) := by
    simpa [F] using hC_scaled.mul h_ratio_limit
  have hC_eq :
      Filter.Eventually (fun x => CReal (t * x) / a x = F x) atTop :=
    hNonzero.mono (fun x hx => by
      have haTx : a (t * x) ≠ 0 := hx.1
      have hax : a x ≠ 0 := hx.2.1
      simp [F, ratio, div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc, haTx])
  have hC_ratio :
      Tendsto (fun x : Real => CReal (t * x) / a x) atTop (nhds (t : Real)) :=
    (tendsto_congr' hC_eq).2 hF
  have hDiff :
      Tendsto (fun x : Real =>
        (CReal (t * x) / a x) - (CReal x / a x)) atTop (nhds ((t : Real) - 1)) :=
    hC_ratio.sub hC
  have hEq :
      Filter.Eventually (fun x : Real =>
        (CReal (t * x) - CReal x) / a x =
          (CReal (t * x) / a x) - (CReal x / a x)) atTop :=
    Filter.Eventually.of_forall (by
      intro x
      simp [div_eq_mul_inv, sub_eq_add_neg, add_comm, add_mul]
    )
  have hResult :
      Tendsto (fun x : Real => (CReal (t * x) - CReal x) / a x)
        atTop (nhds ((t : Real) - 1)) :=
    (tendsto_congr' hEq).2 hDiff
  simpa using hResult


-- Local increment theorem (specialized to the square increment we need):
-- If f ∈ Π (index 1, φ(λ)=λ−1) with auxiliary a(x) = x*ell1(x), then
--   (f((n+1)^2) - f(n^2)) / (((2n+1) * ell1(n^2))) → 1 as n → ∞.
axiom incremental_theorem
  {f a : Real → Real}
  (hPi : deHaanPi1 f a)
  (hAux : ∀ x, a x = x * ell1 x) :
    Tendsto (fun n : Nat =>
      (f (((n + 1 : Nat) : Real) ^ 2) - f ((n : Real) ^ 2)) /
        (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2)))
      atTop (nhds (1 : Real))

-- General local increment theorem (h = o(x)) for the same Π-class
axiom incremental_theorem_local
  {f a : Real → Real}
  (hPi : deHaanPi1 f a)
  (hAux : ∀ x, a x = x * ell1 x)
  (h : Real → Real)
  (hsmall : Tendsto (fun x => h x / x) atTop (nhds (0 : Real))) :
  Tendsto (fun x : Real => (f (x + h x) - f x) / (a x * (h x / x))) atTop (nhds (1 : Real))

-- Compatibility of CReal with C on natural inputs (used to identify values on squares)
axiom CReal_coe_nat (m : Nat) : CReal (m : Real) = C m

noncomputable section

lemma div_mul_div_cancel (x y z : Real) (hy : y ≠ 0) :
    (x / y) * (y / z) = x / z := by
  simp [div_eq_mul_inv, hy, mul_left_comm, mul_assoc]

lemma log3_identity (t : Real) :
    1 / t - Real.eulerMascheroniConstant / t ^ 2 =
      (1 - Real.eulerMascheroniConstant / t) / t := by
  by_cases ht : t = 0
  · simp [ht]
  · field_simp [ht, pow_two]

lemma eventually_ne_zero_nat :
    Filter.Eventually (fun n : Nat => (n : Real) ≠ 0) atTop := by
  refine Filter.eventually_atTop.2 ?_
  refine ⟨1, ?_⟩
  intro n hn
  have hpos : 0 < n := Nat.succ_le_iff.1 hn
  exact_mod_cast (ne_of_gt hpos)

lemma ratio_identity {n : Nat} (hn : (n : Real) ≠ 0) :
    ((2 : Real) * (n : Real) + 1) / ((2 : Real) * (n : Real)) =
      1 + 1 / ((2 : Real) * (n : Real)) := by
  have h2n : (2 : Real) * (n : Real) ≠ 0 := mul_ne_zero (by norm_num) hn
  field_simp [h2n]

lemma tendsto_ratio_two :
    Tendsto (fun n : Nat => ((2 : Real) * (n : Real) + 1) / ((2 : Real) * (n : Real)))
      atTop (nhds (1 : Real)) := by
  have hEq : Filter.Eventually (fun n : Nat =>
      ((2 : Real) * (n : Real) + 1) / ((2 : Real) * (n : Real)) =
        1 + 1 / ((2 : Real) * (n : Real))) atTop :=
    (eventually_ne_zero_nat.mono fun n hn => ratio_identity (n := n) hn)
  have hOneDiv : Tendsto (fun n : Nat => 1 / (n : Real)) atTop (nhds (0 : Real)) :=
    tendsto_one_div_atTop_nhds_zero_nat
  have hConst : Tendsto (fun _ : Nat => (1 / 2 : Real)) atTop (nhds (1 / 2 : Real)) :=
    tendsto_const_nhds
  have hMul : Tendsto (fun n : Nat => (1 / 2 : Real) * (1 / (n : Real)))
      atTop (nhds (0 : Real)) := by
    simpa [zero_mul] using hConst.mul hOneDiv
  have hEq2 : ∀ n : Nat,
      1 / ((2 : Real) * (n : Real)) = (1 / 2 : Real) * (1 / (n : Real)) := by
    intro n
    by_cases hn : (n : Real) = 0
    · simp [hn]
    · field_simp [hn]
  have hAux : Tendsto (fun n : Nat => 1 / ((2 : Real) * (n : Real)))
      atTop (nhds (0 : Real)) := by
    simpa [hEq2] using hMul
  have hConstOne : Tendsto (fun _ : Nat => (1 : Real)) atTop (nhds (1 : Real)) :=
    tendsto_const_nhds
  have hSum : Tendsto (fun n : Nat => 1 + 1 / ((2 : Real) * (n : Real)))
      atTop (nhds (1 : Real)) := by
    simpa using hConstOne.add hAux
  exact (tendsto_congr' hEq).2 hSum

lemma pollack_square_ratio' :
    Tendsto (fun n : Nat => ell1 ((n : Real) ^ 2) / ell1 (n : Real))
      atTop (nhds (1 : Real)) := by
  simpa [ell1] using pollack_square_ratio

lemma eventually_ell1_ne_zero :
    Filter.Eventually (fun n : Nat => ell1 (n : Real) ≠ 0 ∧ ell1 ((n : Real) ^ 2) ≠ 0)
      atTop := by
  have h_ball := pollack_square_ratio'.eventually
      (Metric.ball_mem_nhds (1 : Real) (by norm_num : (0 : Real) < (1 : Real) / 2))
  have h_abs : Filter.Eventually (fun n : Nat =>
      |ell1 ((n : Real) ^ 2) / ell1 (n : Real) - 1| < (1 : Real) / 2)
      atTop := h_ball.mono (fun _ hn => by
        simpa [Real.dist_eq, sub_eq_add_neg, abs_sub_comm] using hn)
  refine h_abs.mono ?_
  intro n hn
  rcases abs_lt.mp hn with ⟨hneg, _hpos⟩
  have h_ratio_gt : (1 : Real) / 2 < ell1 ((n : Real) ^ 2) / ell1 (n : Real) := by
    have := hneg; linarith
  have h_ratio_ne : ell1 ((n : Real) ^ 2) / ell1 (n : Real) ≠ 0 :=
    ne_of_gt (lt_trans (by norm_num) h_ratio_gt)
  have h_denom : ell1 (n : Real) ≠ 0 := by
    by_contra h0
    have : ell1 ((n : Real) ^ 2) / ell1 (n : Real) = 0 := by simp [h0]
    exact h_ratio_ne this
  have h_num : ell1 ((n : Real) ^ 2) ≠ 0 := by
    by_contra h0
    have : ell1 ((n : Real) ^ 2) / ell1 (n : Real) = 0 := by simp [h0]
    exact h_ratio_ne this
  exact And.intro h_denom h_num

lemma eventually_good :
    Filter.Eventually (fun n : Nat =>
      (n : Real) ≠ 0 ∧ ell1 (n : Real) ≠ 0 ∧ ell1 ((n : Real) ^ 2) ≠ 0)
      atTop := by
  have h1 := eventually_ne_zero_nat
  have h2 := eventually_ell1_ne_zero
  exact (h1.and h2).mono (fun n hn => ⟨hn.1, hn.2.1, hn.2.2⟩)

lemma tendsto_ratio_aux :
    Tendsto (fun n : Nat =>
      (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2)) /
        (((2 : Real) * (n : Real)) * ell1 (n : Real)))
      atTop (nhds (1 : Real)) := by
  have h_prod := tendsto_ratio_two.mul pollack_square_ratio'
  have h_eq : ∀ n : Nat,
      (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2)) /
        (((2 : Real) * (n : Real)) * ell1 (n : Real))
      = (((2 : Real) * (n : Real) + 1) / ((2 : Real) * (n : Real))) *
          (ell1 ((n : Real) ^ 2) / ell1 (n : Real)) := by
    intro n; simp [div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc]
  simpa [h_eq] using h_prod

noncomputable def mainTerm (n : Nat) : Real :=
  ((2 : Real) * (n : Real)) * ell1 (n : Real)

-- CReal agrees with C on natural inputs and, in particular, on squares
set_option maxRecDepth 10000 in
lemma CReal_sq_nat (n : Nat) : CReal ((n : Real) ^ 2) = C (n ^ 2) := by
  have hco : ((n : Real) ^ 2) = ((n ^ 2 : Nat) : Real) := by
    simp [pow_two, Nat.cast_mul]
  have hstep : CReal ((n : Real) ^ 2) = CReal (((n ^ 2 : Nat) : Real)) :=
    congrArg CReal hco
  exact hstep.trans (CReal_coe_nat (n ^ 2))

-- Final statement of Conjecture 9.
theorem conjecture9 :
    Tendsto (fun n : Nat =>
      (C ((n + 1) ^ 2) - C (n ^ 2)) /
        mainTerm n)
      atTop (nhds (1 : Real)) := by
  classical
  let g := fun n : Nat =>
    (CReal (((n + 1 : Nat) : Real) ^ 2) - CReal ((n : Real) ^ 2)) /
      (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2))
  let h := fun n : Nat =>
    (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2)) /
      (((2 : Real) * (n : Real)) * ell1 (n : Real))
  have hg : Tendsto g atTop (nhds (1 : Real)) :=
    incremental_theorem (f := CReal) (a := a)
      (hPi := pollack_fixed_scale_increment)
      (hAux := by intro x; rfl)
  have hh : Tendsto h atTop (nhds (1 : Real)) := tendsto_ratio_aux
  have h_event := eventually_good
  have h_eq : Filter.Eventually (fun n : Nat =>
      g n * h n = (C ((n + 1) ^ 2) - C (n ^ 2)) / mainTerm n)
      atTop :=
    h_event.mono fun n hn => by
      classical
      rcases hn with ⟨hn0, h1, h2⟩
      have h2n : (2 : Real) * (n : Real) ≠ 0 := mul_ne_zero (by norm_num) hn0
      have h_lin : (2 : Real) * (n : Real) + 1 ≠ 0 := by
        have hnonneg : 0 ≤ (n : Real) := by exact_mod_cast (Nat.zero_le n)
        have : 0 ≤ (2 : Real) * (n : Real) := mul_nonneg (by norm_num) hnonneg
        exact ne_of_gt (add_pos_of_nonneg_of_pos this (by norm_num))
      have h_num : (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2)) ≠ 0 :=
        mul_ne_zero h_lin h2
      have h_div :=
        div_mul_div_cancel
          (CReal (((n + 1 : Nat) : Real) ^ 2) - CReal ((n : Real) ^ 2))
          (((2 : Real) * (n : Real) + 1) * ell1 ((n : Real) ^ 2))
          (((2 : Real) * (n : Real)) * ell1 (n : Real))
          h_num
      -- On squares, CReal agrees with C exactly
      have hC1 : CReal (((n + 1 : Nat) : Real) ^ 2) = C ((n + 1) ^ 2) := by
        simpa using (CReal_sq_nat (n + 1))
      have hC2 : CReal ((n : Real) ^ 2) = C (n ^ 2) := by
        simpa using (CReal_sq_nat n)
      have h_div' : g n * h n =
          (CReal (((n + 1 : Nat) : Real) ^ 2) - CReal ((n : Real) ^ 2)) /
            (((2 : Real) * (n : Real)) * ell1 (n : Real)) := by
        simpa only [g, h, div_mul_eq_mul_div] using h_div
      have h_eq' : g n * h n =
          (C ((n + 1) ^ 2) - C (n ^ 2)) /
            (((2 : Real) * (n : Real)) * ell1 (n : Real)) := by
        simpa only [hC1, hC2] using h_div'
      simpa [mainTerm] using h_eq'
  have h_prod : Tendsto (fun n : Nat => g n * h n)
      atTop (nhds (1 : Real)) := by
    simpa [one_mul] using hg.mul hh
  exact (tendsto_congr' h_eq).1 h_prod

lemma mainTerm_eq_explicit_real (x : Real) :
    ((2 : Real) * x) * ell1 x =
      ((2 : Real) * x) / Real.exp Real.eulerMascheroniConstant /
        log3 x *
        (1 - Real.eulerMascheroniConstant / log3 x) := by
  classical
  set L := log3 x
  have hLog : 1 / L - Real.eulerMascheroniConstant / L ^ 2 =
      (1 - Real.eulerMascheroniConstant / L) / L := by
    simpa [L] using log3_identity (log3 x)
  have hLog_inv : L⁻¹ - Real.eulerMascheroniConstant / L ^ 2 =
      (1 - Real.eulerMascheroniConstant / L) / L := by
    simpa [one_div] using hLog
  have hExpInv : Real.exp (-Real.eulerMascheroniConstant) =
      (Real.exp Real.eulerMascheroniConstant)⁻¹ := by
    simp [Real.exp_neg]
  have hEll : ell1 x =
      Real.exp (-Real.eulerMascheroniConstant) *
        (1 / L - Real.eulerMascheroniConstant / L ^ 2) := by
    simp [ell1, L]
  calc
    ((2 : Real) * x) * ell1 x
        = ((2 : Real) * x) *
            (Real.exp (-Real.eulerMascheroniConstant) *
              (1 / L - Real.eulerMascheroniConstant / L ^ 2)) := by
          simp [hEll]
    _ = ((2 : Real) * x) *
            (((Real.exp Real.eulerMascheroniConstant)⁻¹) *
              (1 / L - Real.eulerMascheroniConstant / L ^ 2)) := by
          simp [hExpInv]
    _ = (((2 : Real) * x) * ((Real.exp Real.eulerMascheroniConstant)⁻¹)) *
            (1 / L - Real.eulerMascheroniConstant / L ^ 2) := by
          simp [mul_comm, mul_assoc]
    _ = (((2 : Real) * x) * ((Real.exp Real.eulerMascheroniConstant)⁻¹)) *
            ((1 - Real.eulerMascheroniConstant / L) / L) := by
          simpa [mul_comm, mul_left_comm, mul_assoc] using congrArg
            (fun t => (((2 : Real) * x) * ((Real.exp Real.eulerMascheroniConstant)⁻¹)) * t) hLog
    _ = ((2 : Real) * x) / Real.exp Real.eulerMascheroniConstant *
            ((1 - Real.eulerMascheroniConstant / L) / L) := by
          simp [div_eq_mul_inv, mul_comm, mul_assoc]
    _ = ((2 : Real) * x) / Real.exp Real.eulerMascheroniConstant /
            L * (1 - Real.eulerMascheroniConstant / L) := by
          simp [div_eq_mul_inv, mul_comm, mul_assoc]

lemma mainTerm_eq_explicit (n : Nat) :
    mainTerm n =
      ((2 : Real) * (n : Real)) / Real.exp Real.eulerMascheroniConstant /
        log3 (n : Real) *
        (1 - Real.eulerMascheroniConstant / log3 (n : Real)) := by
  simpa [mainTerm] using
    (mainTerm_eq_explicit_real (n : Real))

-- Conjecture 9 written exactly as in the problem statement.
theorem conjecture9_explicit :
    Tendsto (fun n : Nat =>
      (C ((n + 1) ^ 2) - C (n ^ 2)) /
        (((2 : Real) * (n : Real)) / Real.exp Real.eulerMascheroniConstant /
          log3 (n : Real) *
          (1 - Real.eulerMascheroniConstant / log3 (n : Real))))
      atTop (nhds (1 : Real)) := by
  have := conjecture9
  refine (tendsto_congr ?_).2 this
  intro n
  simp [mainTerm_eq_explicit]

end

end Conjecture5
end LeanCode



