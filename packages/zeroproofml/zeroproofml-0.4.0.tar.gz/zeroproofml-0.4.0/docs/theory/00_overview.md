# Signed Common Meadows (SCM) Primer

ZeroProofML v0.4 grounds its semantics in **signed common meadows**: a
field of characteristic 0 extended with a total inverse and a single
absorptive bottom element (⊥). Division by zero yields ⊥, which then
absorbs addition and multiplication, allowing singularities to propagate
without ad-hoc guard branches (see `concept.tex`).

## Weak Sign Structure

SCM augments the meadow core with a sign operator that preserves
orientation even when magnitudes blow up. For real inputs the operator is
4-signed; for complex inputs it projects onto the unit circle, returning
⊥ unchanged and locking the last valid orientation when approaching the
origin (see `concept.tex`). This weak-sign construction makes the
library usable for higher-dimensional robotics where ordered-field
assumptions break down.

## Bottom-Aware Training and Inference

The SCM core already ensures total arithmetic, but training benefits from
explicit handling of singular paths. Gradient policies clamp, reject, or
project gradients that traverse ⊥ during the backward pass, while the
forward graph stays faithful to the algebra. The optional projective
extension lifts select subgraphs to homogeneous tuples (N, D), giving the
optimizer a smooth manifold and delaying any ⊥ instantiation to the
boundary decode step (see `concept.tex`). The guiding rule is:

> Train on smooth (policy- or projective-regularized) objects; infer on
> strict SCM semantics.

## Further Reading

- J.A. Bergstra and A. Ponse, *Common Meadows* (2015/2019) — defines the
  totalised field and absorptive bottom.
- J.A. Bergstra and A. Ponse, *Signed Meadows* (2017) — introduces the
  weak/4-signed operator layered on top of common meadows.
