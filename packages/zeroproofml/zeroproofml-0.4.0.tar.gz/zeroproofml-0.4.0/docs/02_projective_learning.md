# Projective Learning Mode

Projective learning lifts selected subgraphs to homogeneous tuples `(N, D)` so training occurs on a smooth manifold while inference retains strict SCM semantics.

## When to Use
- Rational heads that should avoid instantiating ⊥ during training.
- Safety-critical outputs where distinguishing `+∞` vs `−∞` matters (use with sign consistency loss).
- Scenarios where gradient dead zones around `Q ≈ 0` hurt convergence.

## Forward/Backward Contract
- **Encoding:** `φ(x) = (x, 1)` for finite values; `φ(⊥) = (1, 0)`.
- **Decoding:** `φ⁻¹(N, D) = N/D` when `D ≠ 0`, otherwise ⊥.
- **Detached renormalisation:** `(N, D) ← (N, D) / sg(√(N² + D²) + γ)` to keep tuples bounded without leaking gradients through the norm.
- **Gradients:** Standard autograd on `(N, D)`; coverage/penalties computed after decoding.

## Integration Steps
1. Lift targets to tuples with `training.targets.lift_targets`.
2. Use `GradientPolicy.PROJECT` inside projective regions to mask gradients when a path decodes to ⊥.
3. Combine implicit, margin, and sign-consistency losses to shape the tuple dynamics.
4. Decode to SCM at boundaries and apply coverage/rejection losses there.

## Gap Region
Training uses stochastic thresholds (`τ_train_min`, `τ_train_max`) to avoid learning a brittle boundary at exactly `τ_train`. Inference sets a fixed `τ_infer` and returns ⊥ when `|Q| < τ_infer`.

When `τ_train > τ_infer`, the interval `τ_infer ≤ |Q| < τ_train` is the *gap region* where inference still returns a finite value but the denominator is small enough to be numerically risky. Use `strict_inference(..., InferenceConfig(tau_infer=τ_infer, tau_train=τ_train))` to obtain an explicit `gap_mask` for monitoring.
