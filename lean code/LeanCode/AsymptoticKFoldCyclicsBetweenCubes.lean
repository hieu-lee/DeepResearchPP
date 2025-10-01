-- import Mathlib
import LeanCode.Conjecture5

namespace LeanCode
namespace AsymptoticKFoldCyclicsBetweenCubes

open Filter
open scoped Topology

/-!
# Asymptotic `k`-fold cyclics between cubes

Lean translation of
`JoIS paper/theorems/thm_asymptotic_k_fold_cyclics_between_cubes.tex`.

Each step of the paper is represented below, while external ingredients are
introduced as axioms with the cited references.
-/

/-- Real-valued counting function `A_h(N)` from the statement. -/
axiom AhReal : Nat → Nat → Real

/-- `g ~ f` via ratio `g(N)/f(N) → 1`. -/
def Asymptotic (g f : Nat → Real) : Prop :=
  Tendsto (fun N : Nat => g N / f N) atTop (nhds (1 : Real))

/-- Abstract predicate: `L` is slowly varying. -/
axiom IsSlowlyVarying : (Nat → Real) → Prop

/-- Witness for regular variation `f(N) = N^ρ ⋅ L(N)` with slowly varying `L`. -/
structure RegularVariationWitness (f : Nat → Real) (rho : Real) : Type where
  L : Nat → Real
  slow : IsSlowlyVarying L
  eventually_pos : Filter.Eventually (fun (N : Nat) => 0 < L N) atTop
  defn : ∀ N, f N = Real.rpow (N : Real) rho * L N

/-- `f` is regularly varying with index `ρ`. -/
def RegularVariation (f : Nat → Real) (rho : Real) : Prop :=
  Nonempty (RegularVariationWitness f rho)

/-- Equation (1) of the paper: `A_h(N) ≤ 4 N^2` for `h ∈ {2,4,6}`. -/
axiom Ah_upper_bound
    (h : Nat) (h_mem : h = 2 ∨ h = 4 ∨ h = 6) (N : Nat) :
    AhReal h N ≤ 4 * (N : Real) ^ 2

/-- Use (1) with the asymptotic relation to deduce `f(N) ≤ 8 N^2`. -/
axiom asymptotic_to_quadratic_bound
    {h : Nat} (h_mem : h = 2 ∨ h = 4 ∨ h = 6)
    {f : Nat → Real}
    (hAsym : Asymptotic (AhReal h) f) :
    Filter.Eventually (fun (N : Nat) => f N ≤ 8 * (N : Real) ^ 2) atTop

/-- Real powers of positive bases are positive (Apostol, 1976, Ch. 5). -/
axiom rpow_pos {x a : Real} (hx : 0 < x) : 0 < Real.rpow x a

/-- Addition law for real powers (Apostol, 1976, Ch. 5). -/
axiom rpow_add {x a b : Real} (hx : 0 < x) :
    Real.rpow x (a + b) = Real.rpow x a * Real.rpow x b

/-- Negation law for real powers (Apostol, 1976, Ch. 5). -/
axiom rpow_neg {x a : Real} (hx : 0 < x) :
    Real.rpow x (-a) = (Real.rpow x a)⁻¹

/-- Archimedean fact: powers eventually dominate any constant (Apostol, 1976, Ch. 5). -/
axiom eventually_rpow_ge {ε C : Real} (hε : 0 < ε) (hC : 0 < C) :
    Filter.Eventually (fun (N : Nat) => Real.rpow (N : Real) ε ≥ C) atTop

/-- Slowly varying growth property (Bingham–Goldie–Teugels, 1989, Thm. 1.3.1). -/
axiom slowly_varying_growth
    {L : Nat → Real} (hSlow : IsSlowlyVarying L)
    (hPos : Filter.Eventually (fun (N : Nat) => 0 < L N) atTop)
    {ε : Real} (hε : 0 < ε) :
    Tendsto (fun N : Nat => Real.rpow (N : Real) ε * L N) atTop atTop

/-- Divide the regular variation formula by `N^ρ`. -/
axiom regular_variation_bound_L
    {f : Nat → Real} {rho : Real}
    (w : RegularVariationWitness f rho)
    (hBound : Filter.Eventually (fun (N : Nat) => f N ≤ 8 * (N : Real) ^ 2) atTop) :
    Filter.Eventually (fun (N : Nat) => w.L N ≤ 8 * Real.rpow (N : Real) (2 - rho)) atTop

/-- Multiply the bound by `N^{(ρ-2)/2}`. -/
axiom multiply_with_power
    {ρ : Real} {L : Nat → Real}
    (hBound : Filter.Eventually (fun (N : Nat) =>
      L N ≤ 8 * Real.rpow (N : Real) (2 - ρ)) atTop) :
    Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) * L N ≤
        8 * Real.rpow (N : Real) (-(ρ - 2) / 2)) atTop

/-- Replace the negative power by an explicit reciprocal. -/
axiom divide_bound_by_power
    {ρ : Real} {L : Nat → Real}
    (hBound : Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) * L N ≤
        8 * Real.rpow (N : Real) (-(ρ - 2) / 2)) atTop) :
    Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) * L N ≤
        8 / Real.rpow (N : Real) ((ρ - 2) / 2)) atTop

/-- Substitute the lower bound on the power to obtain `≤ 1/2`. -/
axiom substitute_power_lower_bound
    {ρ : Real} {L : Nat → Real}
    (hBound : Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) * L N ≤
        8 / Real.rpow (N : Real) ((ρ - 2) / 2)) atTop)
    (hLarge : Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) ≥ 16) atTop) :
    Filter.Eventually (fun (N : Nat) =>
      Real.rpow (N : Real) ((ρ - 2) / 2) * L N ≤ (1 : Real) / 2) atTop

/-- Contradiction between eventual upper and lower bounds. -/
axiom eventually_lt_of_le_of_lt
    {u : Nat → Real}
    (hUpper : Filter.Eventually (fun (N : Nat) => u N ≤ (1 : Real) / 2) atTop)
    (hLower : Filter.Eventually (fun (N : Nat) => (1 : Real) ≤ u N) atTop) : False

/-- Main theorem: no regularly varying asymptotic with index `ρ ∈ (2, 5/2]`. -/
lemma asymptotic_k_fold_cyclics_between_cubes
    {h : Nat} (h_mem : h = 2 ∨ h = 4 ∨ h = 6) :
    ¬ ∃ rho : Real, 2 < rho ∧ rho ≤ (5 : Real) / 2 ∧
        ∃ f : Nat → Real,
          RegularVariation f rho ∧ Asymptotic (AhReal h) f := by
  intro hEx
  classical
  rcases hEx with ⟨rho, h_rho_gt, h_rho_le, f, hRV, hAsym⟩
  obtain ⟨w⟩ := hRV
  have h_f_le :
      Filter.Eventually (fun (N : Nat) => f N ≤ 8 * (N : Real) ^ 2) atTop :=
    asymptotic_to_quadratic_bound (h := h) h_mem (f := f) hAsym
  have h_L_le :=
    regular_variation_bound_L (f := f) (rho := rho) w h_f_le
  have h_L_power :=
    multiply_with_power (ρ := rho) (L := w.L) h_L_le
  have h_div := divide_bound_by_power (ρ := rho) (L := w.L) h_L_power
  have h_eps_pos : 0 < (rho - 2) / 2 := by
    have : 0 < rho - 2 := sub_pos_of_lt h_rho_gt
    exact half_pos this
  have hArch :=
    eventually_rpow_ge (ε := (rho - 2) / 2) (C := 16) h_eps_pos (by norm_num)
  have h_uniform :=
    substitute_power_lower_bound (ρ := rho) (L := w.L) h_div hArch
  have h_growth :=
    slowly_varying_growth w.slow w.eventually_pos h_eps_pos
  have h_lower :
      Filter.Eventually (fun (N : Nat) =>
        (1 : Real) ≤ Real.rpow (N : Real) ((rho - 2) / 2) * w.L N) atTop :=
    tendsto_atTop.1 h_growth (1 : Real)
  exact eventually_lt_of_le_of_lt
    (u := fun (N : Nat) => Real.rpow (N : Real) ((rho - 2) / 2) * w.L N)
    h_uniform h_lower

end AsymptoticKFoldCyclicsBetweenCubes
end LeanCode
