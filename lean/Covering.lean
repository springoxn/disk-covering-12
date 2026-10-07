/-
  Formal (Lean 4 + Mathlib) proof of the geometric lemma on which the
  covering argument of this project rests.

  Main results:

  * `sum_weighted_dist_sq` : for points `a i` all lying on the circle of centre
    `c` and radius `R`, and `x` a convex combination of the `a i`,
        ∑ i, lam i * ‖x - a i‖^2 = R^2 - ‖x - c‖^2 .
  * `triangle_covering` : consequently some `a i` satisfies ‖x - a i‖ ≤ R, i.e.
    a triangle is covered by the three disks of radius R centred at its
    vertices whenever its circumradius is at most R.

  This is the "triangle covering lemma" used in docs/RESULT.md section 3
  (Lemma T).  Everything is stated for a real inner product space.
-/
import Mathlib

open Finset

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Weighted-average identity behind the triangle covering lemma. -/
theorem sum_weighted_dist_sq {n : ℕ} (a : Fin n → E) (c x : E) (R : ℝ)
    (hR : ∀ i, ‖a i - c‖ = R) (lam : Fin n → ℝ) (hsum : ∑ i, lam i = 1)
    (hx : x = ∑ i, lam i • a i) :
    ∑ i, lam i * ‖x - a i‖ ^ 2 = R ^ 2 - ‖x - c‖ ^ 2 := by
  have hL : x - c = ∑ i, lam i • a i - (∑ i, lam i) • c := by
    rw [hx, hsum, one_smul]
  have hy : x - c = ∑ i, lam i • (a i - c) := by
    rw [hL, Finset.sum_smul, ← Finset.sum_sub_distrib]
    simp only [smul_sub]
  have hterm : ∀ i, lam i * ‖x - a i‖ ^ 2
      = lam i * ‖x - c‖ ^ 2 - 2 * (lam i * inner ℝ (x - c) (a i - c))
        + lam i * ‖a i - c‖ ^ 2 := by
    intro i
    have hsub : x - a i = (x - c) - (a i - c) := by abel
    rw [hsub, norm_sub_sq_real]
    ring
  have hinner : (∑ i, lam i * inner ℝ (x - c) (a i - c))
      = inner ℝ (x - c) (∑ i, lam i • (a i - c)) := by
    rw [inner_sum]
    refine Finset.sum_congr rfl ?_
    intro i _
    rw [real_inner_smul_right]
  have hthird : (∑ i, lam i * ‖a i - c‖ ^ 2) = R ^ 2 := by
    have h1 : ∀ i, lam i * ‖a i - c‖ ^ 2 = lam i * R ^ 2 := by
      intro i
      rw [hR i]
    rw [Finset.sum_congr rfl (fun i _ => h1 i), ← Finset.sum_mul, hsum, one_mul]
  calc ∑ i, lam i * ‖x - a i‖ ^ 2
      = ∑ i, (lam i * ‖x - c‖ ^ 2 - 2 * (lam i * inner ℝ (x - c) (a i - c))
              + lam i * ‖a i - c‖ ^ 2) :=
        Finset.sum_congr rfl (fun i _ => hterm i)
    _ = (∑ i, lam i * ‖x - c‖ ^ 2) - 2 * (∑ i, lam i * inner ℝ (x - c) (a i - c))
          + (∑ i, lam i * ‖a i - c‖ ^ 2) := by
        rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.mul_sum]
    _ = ‖x - c‖ ^ 2 - 2 * inner ℝ (x - c) (x - c) + R ^ 2 := by
        rw [hinner, hthird, ← Finset.sum_mul, hsum, one_mul, ← hy]
    _ = R ^ 2 - ‖x - c‖ ^ 2 := by
        rw [real_inner_self_eq_norm_sq]
        ring

/-- Triangle covering lemma: if every vertex `a i` lies on the circle of centre
`c` and radius `R`, and `x` is a convex combination of the vertices, then some
vertex is within distance `R` of `x`. -/
theorem triangle_covering {n : ℕ} (a : Fin n → E) (c x : E) (R : ℝ)
    (hR : ∀ i, ‖a i - c‖ = R) (lam : Fin n → ℝ) (hlam : ∀ i, 0 ≤ lam i)
    (hsum : ∑ i, lam i = 1) (hx : x = ∑ i, lam i • a i) (hne : ∃ i, 0 < lam i) :
    ∃ i, ‖x - a i‖ ≤ R := by
  have hRnn : 0 ≤ R := by
    obtain ⟨i⟩ := hne
    rw [← hR i]
    exact norm_nonneg _
  have hid := sum_weighted_dist_sq a c x R hR lam hsum hx
  by_contra hcon
  simp only [not_exists, not_le] at hcon
  have hsq : ∀ i, R ^ 2 < ‖x - a i‖ ^ 2 := by
    intro i
    have h1 := hcon i
    nlinarith [hRnn, norm_nonneg (x - a i)]
  have hle2 : ∀ i, lam i * R ^ 2 ≤ lam i * ‖x - a i‖ ^ 2 := by
    intro i
    exact mul_le_mul_of_nonneg_left (le_of_lt (hsq i)) (hlam i)
  obtain ⟨i0, hi0⟩ := hne
  have hlt2 : lam i0 * R ^ 2 < lam i0 * ‖x - a i0‖ ^ 2 :=
    mul_lt_mul_of_pos_left (hsq i0) hi0
  have hsum_lt : ∑ i, lam i * R ^ 2 < ∑ i, lam i * ‖x - a i‖ ^ 2 :=
    Finset.sum_lt_sum (fun i _ => hle2 i) ⟨i0, Finset.mem_univ _, hlt2⟩
  have hsumR : ∑ i, lam i * R ^ 2 = R ^ 2 := by
    rw [← Finset.sum_mul, hsum, one_mul]
  rw [hid, hsumR] at hsum_lt
  nlinarith [sq_nonneg (‖x - c‖)]
