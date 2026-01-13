# Projective Training Developer Guide

This guide shows how the `(N, D)` projective tuples flow through training and how they are decoded back to SCM values during inference.

## Tuple Lifecycle
- **Encoding:** Lift finite SCM values with `φ(x) = (x, 1)` and represent absorptive bottom as `φ(⊥) = (1, 0)` (or `(s, 0)` when sign metadata is tracked).
- **Detached renormalization:** Keep tuples bounded with a stop-gradient scale:
  ```python
  S = sg(torch.sqrt(N ** 2 + D ** 2)) + gamma
  N_hat, D_hat = N / S, D / S
  ```
  `sg(·)` prevents gradients from leaking through the norm; `gamma` avoids division by zero when tuples sit on the equator.
- **Denominator anchoring (recommended):** For finite-target regression heads, anchor denominators around 1 to avoid drift into tiny-but-nonzero values that amplify decoded ratios:
  ```python
  Q = 1 + delta_Q
  P, Q = projective.renormalize(P, Q, gamma=1e-9)
  ```
  This keeps the projective direction learnable while biasing the representation toward the finite chart.
- **Gradient flow:** Autograd runs on `(N_hat, D_hat)`. Losses that depend on decoded SCM values should decode after renormalization to avoid biasing the tuple scale.

## Decoding Back to SCM
- **Inference decode:** Use the inverse map `φ⁻¹(N, D) = N / D` when `D ≠ 0`; emit `⊥` when `D = 0`. Apply any inference-time gap thresholds (e.g., `|Q| < τ_infer`) after decoding.
- **Bridge boundaries:** When projective regions hand off to SCM-only layers, decode immediately after the last renormalization step to maintain the training distribution seen by downstream components.
- **Logging:** Surface both the tuple norm `‖(N, D)‖` and the decoded SCM value in debug logs so divergence between training tuples and inference values is visible.

## Minimal Training Skeleton
```python
from zeroproof.autodiff import projective

# Forward: lift and renormalize
N, D = projective.encode(batch)              # φ(x)
N, D = projective.renormalize(N, D, gamma=1e-9)

# Losses on tuples or decoded SCM values
outputs = projective.decode(N, D)            # φ⁻¹(N, D)
loss = loss_fn(outputs, targets)
loss.backward()

# Inference: decode only
with torch.no_grad():
    outputs = projective.decode(N, D)
```
Keep a single renormalization site per forward pass to avoid scale drift, and ensure inference uses the same decode path invoked during training.

## Note on the Implicit Loss Scale
When using the implicit cross-product fit loss, use a detached *squared-norm* scale factor (not a square root):
```python
cross = P * Y_d - Q * Y_n
scale_sq = sg(Q**2 * Y_d**2 + P**2 * Y_n**2) + gamma
loss = mean((cross**2) / scale_sq)
```
This matches the projective invariance contract described in `concept.tex` and prevents scale-sensitive collapse modes.
