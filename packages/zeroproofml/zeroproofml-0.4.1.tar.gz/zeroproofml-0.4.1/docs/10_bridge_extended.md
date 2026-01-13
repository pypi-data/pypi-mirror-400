# Extended IEEE/Array Bridge Documentation (SCM)

## Overview

ZeroProofML's bridge collapses IEEE NaN/Inf into the single SCM bottom element `⊥` and keeps mask semantics aligned across NumPy, PyTorch, and JAX arrays. The helpers live in `zeroproof.utils.ieee_bridge` for scalars and in `zeroproof.scm.ops` for vectorised math.

## Scalar Conversion

```python
from zeroproof.utils.ieee_bridge import from_ieee, to_ieee

scm_val = from_ieee(float("nan"))  # ⊥
print(scm_val.is_bottom)            # True
print(to_ieee(scm_val))             # nan
```

Use `batch_from_ieee`/`batch_to_ieee` when handling iterables.

## NumPy and Torch Masks

Vectorised helpers take parallel arrays of payloads and boolean ⊥ masks. Operations propagate masks instead of materialising infinities:

```python
import numpy as np
from zeroproof.scm.ops import scm_add_numpy, scm_div_numpy

payload = np.array([1.0, 0.0, -1.0])
mask = np.array([False, True, False])  # mark ⊥ locations

values, value_mask = scm_add_numpy(payload, payload, mask, mask)
quot, quot_mask = scm_div_numpy(payload, np.ones_like(payload), mask, np.zeros_like(mask))
```

Torch mirrors the same calling convention:

```python
import torch
from zeroproof.scm.ops import scm_mul_torch

x = torch.tensor([2.0, 0.0])
mask = torch.tensor([False, True])
prod, prod_mask = scm_mul_torch(x, mask, torch.tensor([3.0, 4.0]), mask)
```

All outputs return a `(payload, mask)` tuple. Masks stay boolean so they can be logged directly as coverage metrics.

## Projective Tuples

`SCMRationalLayer` exposes a bottom mask alongside its output so that singularities can be handled once at decode time:

```python
from zeroproof.layers import SCMRationalLayer
from zeroproof.autodiff.policies import GradientPolicy

layer = SCMRationalLayer(1, 1, gradient_policy=GradientPolicy.PROJECT)
y, bottom_mask = layer(x)
```

This keeps the forward graph free of control flow and lets you decide whether to drop, clamp, or project ⊥ values in the trainer.

## Design Notes

- **Single bottom element:** NaN and ±∞ collapse to `⊥`; there are no Transreal tags in v0.4.
- **Weak sign:** Orientation can be recovered with `zeroproof.scm.sign.weak_sign` after mapping values into SCM.
- **Deterministic masks:** Vectorised ops never branch on data values beyond explicit zero checks, making them compiler-friendly.
