# Loss Functions in v0.4

ZeroProofML v0.4 combines multiple losses to stabilise training near singularities and to distinguish projective orientations.

## Implicit Loss
Cross-product form that avoids direct division:
\[ E = (P \cdot Y_d - Q \cdot Y_n)^2, \quad L = \operatorname{mean}\left( \frac{E}{\operatorname{sg}(Q^2 Y_d^2 + P^2 Y_n^2) + \gamma} \right) \]
Handles poles by keeping gradients defined even when `Q → 0`.

## Margin Loss
Encourages denominators to stay away from zero during training:
\[ L_{\text{margin}} = \operatorname{mean}(\max(0, \tau_{train} - |Q|)^2) \]
Optionally masked to finite paths.

## Sign Consistency Loss (Critical)
Projective cosine similarity to disambiguate `+∞` vs `−∞` by aligning `(P, Q)` with target tuples `(Y_n, Y_d)`.

## Coverage & Rejection
- **Coverage metric:** fraction of outputs that are finite (non-⊥).
- **Rejection loss:** penalises coverage below a target threshold, typically paired with adaptive sampling.

## Combined Training Objective
`SCMTrainingLoss` mixes the components:
\[ L = L_{fit} + \lambda_{margin} L_{margin} + \lambda_{sign} L_{sign} + \lambda_{rej} L_{rej} \]
Default hyperparameters follow Appendix B in `todo.md` (`γ=1e-9`, `τ_{train}=1e-4`, `ε_{sing}=1e-3`, `λ_{margin}=0.1`, `λ_{sign}=1.0`).
