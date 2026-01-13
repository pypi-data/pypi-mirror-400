# Optimization Guide (SCM)

ZeroProofML v0.4 focuses on SCM-native performance rather than transreal profiling hooks. This guide highlights the current levers for efficient training and inference.

## 1. Prefer vectorised SCM ops

Use the backend factories in `zeroproof.scm.ops` to keep payloads and ⊥ masks aligned without Python loops. Example:

```python
import numpy as np
from zeroproof.scm.ops import scm_add_numpy, scm_div_numpy

values = np.array([1.0, 0.0, -2.0])
mask = np.array([False, True, False])
num, num_mask = scm_add_numpy(values, values, mask, mask)
den, den_mask = scm_div_numpy(num, np.ones_like(num), num_mask, np.zeros_like(num_mask))
```

Masks remain boolean, making it easy to accumulate coverage metrics.

## 2. Track coverage, not branches

SCM graphs avoid guard rails; instead, record how often the model predicts ⊥:

```python
bottom_rate = float(bottom_mask.float().mean())
if bottom_rate > 0.1:
    print("Too many singular predictions; adjust loss weights or epsilon.")
```

## 3. Use gradient policies intentionally

`GradientPolicy.PROJECT` zeros gradients on ⊥ paths; `CLAMP` caps finite gradients. Choose per-layer:

```python
from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.layers import SCMRationalLayer

head = SCMRationalLayer(1, 1, gradient_policy=GradientPolicy.PROJECT)
```

## 4. Projective tuples during training

Keep rational heads in projective form during optimisation and decode with the ⊥ mask at evaluation. This preserves stability near poles without hiding coverage gaps.

## 5. Keep IEEE ingress explicit

Map NaN/Inf to ⊥ at the boundary using `zeroproof.utils.ieee_bridge`. Avoid ad-hoc `nan_to_num` calls that would erase mask information.

## 6. Benchmark with real payloads

Scripts in `benchmarks/` exercise the SCM backends without any transreal tags. Start from `benchmarks/run_benchmarks.py` and track ⊥ throughput alongside wall-clock time.
