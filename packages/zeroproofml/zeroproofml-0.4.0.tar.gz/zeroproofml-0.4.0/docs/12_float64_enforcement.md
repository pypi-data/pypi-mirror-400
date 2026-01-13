# Precision & Dtype Notes (v0.4 SCM)

ZeroProofML v0.4 is SCM-first and represents singularities via an explicit `⊥`/mask rather than IEEE `NaN`/`Inf` arithmetic. Precision still matters, especially for detecting “near-zero” denominators and for stable optimisation.

## Recommended defaults

- Prefer **float64** (`torch.float64`) for rational heads (`SCMRationalLayer`) when your workload is near-singular (robotics IK, stiff physics).
- Keep denominator singular detection explicit via the layer’s `singular_epsilon` (see `zeroproof/layers/scm_rational.py`).

Example:

```python
import torch
torch.set_default_dtype(torch.float64)
```

## What is (and isn’t) enforced

- There is **no global float64 enforcement layer** in the v0.4 core.
- The Torch examples set dtype explicitly; your application should do the same.
- Mixed precision is supported in the trainer (`zeroproof/training/trainer.py`) via AMP; for non-CUDA devices the default AMP dtype is adjusted away from `float16`.

## Practical guidance

- If you see unstable `bottom_mask` behaviour (too many / too few singular flags), tune:
  - `SCMRationalLayer.singular_epsilon` (forward detection)
  - trainer `tau_train_min`/`tau_train_max` (projective denominator thresholding)
- When exporting to IEEE floats, `⊥` maps to `NaN` (`zeroproof/utils/ieee_bridge.py`) so downstream metrics tooling can treat it as invalid.
