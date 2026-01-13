# Optimization and Testing Summary (SCM)

ZeroProofML v0.4 removed the transreal-specific profilers and fusers. The optimisation surface now centres on the SCM primitives that keep ⊥ visible without branching.

## Core Pieces

- **`zeroproof.scm.ops`** – Vectorised arithmetic for NumPy/Torch/JAX that carries `(payload, ⊥ mask)` pairs so kernels stay fuseable.
- **`zeroproof.autodiff.policies`** – Gradient policies (`PROJECT`, `CLAMP`, `REJECT`, `PASSTHROUGH`) to control how singular paths influence learning.
- **`zeroproof.layers.SCMRationalLayer`** – Projective rational head exposing a bottom mask for coverage tracking and post-hoc decoding.
- **`zeroproof.scm.sign`** – Weak sign projection with hysteresis to stabilise orientation near the singular band.
- **`zeroproof.utils.ieee_bridge`** – Deterministic ingress/egress that collapses NaN/Inf to ⊥ so instrumentation stays consistent.

## Testing Approach

- Unit tests in `tests/utils/test_ieee_bridge.py` verify IEEE round-trips and ⊥ construction.
- Examples in `examples/` exercise vectorised ops, gradient policies, and projective tuples as living documentation.
- Benchmarks under `benchmarks/` measure SCM throughput without any transreal tag handling.

## Practical Tips

1. Log ⊥ coverage per batch; use it as a gating signal in evaluation pipelines.
2. Prefer vectorised helpers over Python loops to keep masks aligned and JIT-friendly.
3. Clamp or project gradients when poles are expected; leave PASSTHROUGH for already-regularised layers.
4. Treat IEEE conversion as an explicit boundary to avoid silent loss of ⊥ information.
