# Integrations Guide (v0.4 SCM)

This guide explains how to integrate ZeroProofML’s **Signed Common Meadow (SCM)** semantics with common ML stacks.

The key contract in v0.4:
- Use `⊥` (and/or a boolean mask) to represent singular/domain-error states.
- Keep the payload numeric and treat the mask as the “special value” channel.

## Installing backends

ZeroProofML keeps backends optional. From a repo checkout:

```bash
pip install -e ".[torch]"  # PyTorch integration
pip install -e ".[jax]"    # JAX integration
```

You can also run a minimal integration check without `pytest`:

```bash
.venv/bin/python scripts/smoke_integrations.py
```

## Python / NumPy

### Ingesting external floats

Use the IEEE bridge to collapse `NaN`/`Inf` to `⊥` at the boundary:

```python
from zeroproof.utils.ieee_bridge import from_ieee

v = from_ieee(float("inf"))  # -> ⊥
```

### Vectorised arithmetic (payload + mask)

Use the `scm_*_numpy` helpers in `zeroproof.scm.ops`:

```python
import numpy as np
from zeroproof.scm.ops import scm_mul_numpy

payload = np.array([1.0, 2.0, 3.0])
mask = np.array([False, True, False])  # mark ⊥

out, out_mask = scm_mul_numpy(payload, payload, mask, mask)
```

## PyTorch

### SCM rational heads

`SCMRationalLayer` returns an explicit bottom mask:

```python
import torch
from zeroproof.layers import SCMRationalLayer

layer = SCMRationalLayer(3, 2)  # degrees (P, Q)
y, bottom = layer(torch.randn(128))
```

Use `bottom` for:
- coverage metrics (`1 - bottom.float().mean()`)
- inference decoding (`NaN` sentinel or explicit rejection)
- rejection loss inputs (`zeroproof.losses.rejection_loss`)

### Loss wiring pattern

Most training loops follow:
1) model returns `(y, bottom_mask)` (or projective tuple outputs)
2) compute fit loss on decoded values
3) add SCM regularisers (margin/sign/rejection) using `zeroproof.losses.SCMTrainingLoss`

## JAX

The v0.4 core provides vectorised SCM ops for JAX via `scm_*_jax` (payload + mask).
Projective tuple tooling is implemented in `zeroproof/autodiff/projective.py` for the conceptual contract; for high-performance JAX training, treat it as a reference implementation and port the same mask/threshold logic into your JIT-ed code.

## Export / tooling

- `⊥` is exported as IEEE `NaN` by default (`zeroproof/utils/ieee_bridge.py`) so standard tooling can ignore/reject invalid predictions.
- Keep raw `bottom_mask` alongside payloads if you need to distinguish “model refused” vs “numerically NaN” in downstream systems.
