# Implementation Verification Report (v0.4 SCM)

This report summarises what is implemented in the **v0.4 Signed Common Meadows (SCM)** codebase and what the current contracts are.

Scope: the v0.4 Python packages `zeroproof/` and `zeroproofml/` (compatibility shim).

## ✅ Core domain: `SCMValue` and `⊥`

**Code:** `zeroproof/scm/value.py`

- `SCMValue` represents either a numeric payload (`float`/`complex`) or the absorptive bottom element `⊥` (`is_bottom=True`).
- Bottom is **absorptive** for `+` and `·`; division by zero yields bottom.
- Factories: `scm_real`, `scm_complex`, `scm_bottom`.

## ✅ Scalar arithmetic helpers

**Code:** `zeroproof/scm/ops.py`

- Scalar helpers implement totalised arithmetic: `scm_add`, `scm_sub`, `scm_mul`, `scm_div`, `scm_inv`, `scm_neg`, `scm_pow`.
- Transcendentals are bottom-aware with domain checks: `scm_log`, `scm_exp`, `scm_sqrt`, `scm_sin`, `scm_cos`, `scm_tan`.

## ✅ Vectorised SCM + masks (NumPy / Torch / JAX)

**Code:** `zeroproof/scm/ops.py`

Vectorised entry points propagate a separate boolean bottom mask:
- NumPy: `scm_*_numpy`
- Torch: `scm_*_torch`
- JAX: `scm_*_jax`

Each returns `(payload, mask)` and treats:
- `mask=True` as `⊥`
- division by zero / inverse of zero as `⊥` (adds to the mask)

## ✅ IEEE-754 bridge (scalar)

**Code:** `zeroproof/utils/ieee_bridge.py`

- `from_ieee`: collapses `NaN` and `±inf` to `⊥`
- `to_ieee`: maps `⊥` to `NaN` (tooling-friendly sentinel)

## ✅ Gradient policies (SCM semantics)

**Code:** `zeroproof/autodiff/policies.py`

- Policy enum: `CLAMP`, `PROJECT`, `REJECT`, `PASSTHROUGH`
- Context manager: `gradient_policy(...)`
- Utilities: `apply_policy`, `apply_policy_vector`

## ✅ Torch SCM rational layer with bottom mask + policy hook

**Code:** `zeroproof/layers/scm_rational.py`

- `SCMRationalLayer.forward(x) -> (output, bottom_mask)`
- Singularities are detected via `denominator ≈ 0` and surfaced as `bottom_mask`
- Policies are applied by registering a backward hook on `output` gradients

## ✅ Trainer loop: coverage-aware early stopping

**Code:** `zeroproof/training/trainer.py`

- `SCMTrainer.fit()` returns per-step logs including `loss` and `coverage`
- Coverage is estimated from `NaN` on decoded tensors or from projective denominators
- Supports gradient accumulation and mixed precision (AMP)

## Intentional non-goals (v0.4)

- No Transreal tags (`+∞`, `−∞`, `Φ`) in the v0.4 core; the archived v0.3 stack lives under `legacy/zeroproof_v0_3/`.
- No “Mask‑REAL”/“Hybrid” transreal modes in the v0.4 public API; use gradient policies and/or projective tuples instead.
