# Gradient Policies

Gradient policies control how backpropagation interacts with the absorptive bottom ⊥. They live in `zeroproof.autodiff.policies` and can be set globally via the `gradient_policy` context manager.

## Available Policies
- **CLAMP (default):** Zeroes gradients on ⊥ paths and clamps finite gradients to `[-1, 1]`.
- **PROJECT:** Masks gradients when the forward value is ⊥; used for projective heads where ⊥ indicates points at infinity.
- **REJECT:** Always returns zero gradient, forcing learning to occur through coverage/rejection losses instead of local signals.
- **PASSTHROUGH:** For debugging; gradients propagate even through ⊥.

## Usage
```python
from zeroproof.autodiff.policies import GradientPolicy, gradient_policy, apply_policy

with gradient_policy(GradientPolicy.PROJECT):
    loss.backward()
```

## Design Notes
- Policies are deterministic and compatible with XLA/TorchScript because they avoid Python-side branching on tensors.
- Policy defaults can be registered per-layer using `register_policy(layer, policy)`.
- Projective mode typically pairs `GradientPolicy.PROJECT` with detached renormalisation to avoid NaN gradients.
