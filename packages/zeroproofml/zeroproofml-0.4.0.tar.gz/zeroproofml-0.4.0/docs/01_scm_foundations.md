# SCM Foundations

Signed Common Meadows (SCM) provide a totalised arithmetic with a single absorptive bottom value (⊥). The library follows the framework described in `concept.tex`.

## Algebraic Rules
- **Total inverse:** every element has an inverse; `0^{-1} = ⊥`.
- **Absorption:** `x + ⊥ = ⊥` and `x · ⊥ = ⊥` for all `x`.
- **Weak sign:** `s(x) = x/|x|` for non-zero inputs, `0` at the origin, `⊥` when the argument is ⊥; for complex numbers the sign lies on the unit circle.
- **History-aware sign:** when |z| falls below `ε_sign`, the last valid orientation is kept to prevent oscillation.

## Practical Implications
- Scalar SCM ops (`zeroproof.scm.value`, `zeroproof.scm.ops`) return `SCMValue(⊥)` on division-by-zero / domain errors instead of IEEE `NaN/Inf`.
- For arrays/tensors, SCM values are represented as a **numeric payload + bottom mask**. The mask is authoritative; payload values on masked entries are undefined and must be ignored (use strict decoding to map them to `NaN` if you need an IEEE sentinel).
- No layer-by-layer “guard mode” is required: singularity handling is pushed to explicit masks and a single decode at the output boundary.
- Numerical stability is handled by gradient policies and (optionally) projective tuples, rather than ad-hoc forward clamps.

## Fracterm Flattening
For rational heads we exploit fracterm flattening: small rational subgraphs are rewritten as `P(x) / Q(x)` to reduce singularity checks to the final denominator. Depth is capped (L ≤ 5) to avoid polynomial blow-up.

## Terminology
- **Bottom (⊥):** absorptive error element; any operation involving ⊥ yields ⊥.
- **Projective tuple:** pair `(N, D)` representing the same value as `N/D` with `(1, 0)` denoting ⊥.
- **Coverage:** fraction of predictions that remain finite (non-⊥) under SCM semantics.
