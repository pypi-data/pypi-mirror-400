# IEEE / Array Bridge (SCM) — Summary

ZeroProofML v0.4 uses **Signed Common Meadows (SCM)**: all domain errors and division-by-zero collapse to a single absorptive bottom element `⊥`. There are no Transreal tags (`+∞`, `−∞`, `Φ`) in the v0.4 core.

The bridge story is therefore:
- **Scalars:** map IEEE-754 `NaN`/`±inf` ↔ `⊥`
- **Arrays/tensors:** carry a numeric payload plus an explicit boolean **bottom mask**

## Scalar conversion (`zeroproof.utils.ieee_bridge`)

Use this when you ingest external floats that may contain `NaN`/`Inf`.

```python
from zeroproof.utils.ieee_bridge import from_ieee, to_ieee

v = from_ieee(float("nan"))  # -> SCMValue(⊥)
assert v.is_bottom

out = to_ieee(v)             # -> nan (tooling-friendly sentinel)
```

Batch helpers are available for iterables: `batch_from_ieee`, `batch_to_ieee`.

## Vectorised operations with masks (`zeroproof.scm.ops`)

For numerical backends, SCM values are represented as:
- `payload`: `float`/`complex` array (NumPy/JAX) or tensor (Torch)
- `mask`: boolean array/tensor marking `⊥` positions

Vectorised operators propagate `⊥` by combining masks (and for division/inverse also checking for zeros).

```python
import numpy as np
from zeroproof.scm.ops import scm_div_numpy

x = np.array([1.0, 2.0, 3.0])
x_mask = np.array([False, False, False])
y = np.array([1.0, 0.0, 1.0])
y_mask = np.array([False, False, False])

q, q_mask = scm_div_numpy(x, y, x_mask, y_mask)  # q_mask[1] == True (division by zero -> ⊥)
```

Backends:
- NumPy: `scm_*_numpy`
- PyTorch: `scm_*_torch`
- JAX: `scm_*_jax`

All vectorised functions return `(payload, mask)`.

## Torch rational layers: `bottom_mask` as the SCM boundary

Torch SCM layers follow a single-check pattern: forward passes return a **mask** that you treat as `⊥` at the boundary (loss, logging, inference decode).

Example: `SCMRationalLayer` returns `(output, bottom_mask)` where `bottom_mask` flags denominator singularities.

```python
import torch
from zeroproof.layers import SCMRationalLayer

layer = SCMRationalLayer(1, 1)
x = torch.tensor([-1.0, 0.0, 1.0])
y, bottom = layer(x)
decoded = torch.where(bottom, torch.full_like(y, float("nan")), y)
```

## Design choices

- `⊥` maps to IEEE `NaN` on export (`to_ieee`) so downstream tooling (NumPy/Pandas/metrics) can treat it as “invalid”.
- Array/tensor SCM semantics stay compiler-friendly: the “special value” is in the **mask**, not in the payload.
- Coverage metrics are naturally expressed as `1 - bottom_mask.float().mean()`.
