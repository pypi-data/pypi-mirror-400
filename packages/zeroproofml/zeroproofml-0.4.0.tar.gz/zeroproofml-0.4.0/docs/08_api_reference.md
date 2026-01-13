# ZeroProofML v0.4 API Reference (Phase 9)

This page collects the public Python API for the signed common meadow (SCM)
implementation described in `concept.tex`. The emphasis is on the functions
and classes that are stable for the v0.4 release; experimental helpers remain
internal.

## SCM Core (`zeroproof.scm`)

### `zeroproof.scm.value`
- `SCMValue`: immutable value container carrying either a numeric payload or the absorptive bottom `⊥`.
- `scm_real(x: float) -> SCMValue`: construct a finite SCM value from a real number.
- `scm_complex(z: complex) -> SCMValue`: construct a finite SCM value from a complex number.
- `scm_bottom() -> SCMValue`: return the absorptive bottom element.

### `zeroproof.scm.ops`
- Arithmetic helpers mirror common meadow semantics: `scm_add`, `scm_sub`, `scm_mul`, `scm_div`, `scm_inv`, `scm_neg`, `scm_pow`.
- Transcendental helpers respect the bottom element: `scm_log`, `scm_exp`, `scm_sqrt`, `scm_sin`, `scm_cos`, `scm_tan`.
- All functions accept `SCMValue` or plain Python scalars for ergonomic use in notebooks and examples.

## Autodiff (`zeroproof.autodiff`)

### Gradient policies (`zeroproof.autodiff.policies`)
- `GradientPolicy`: enum of gradient handling strategies (`CLAMP`, `PROJECT`, `REJECT`, `PASSTHROUGH`).
- `gradient_policy(policy: GradientPolicy)`: context manager to override the active policy.
- `register_policy(layer: str, policy: GradientPolicy)`: register layer-specific defaults.
- `apply_policy(gradient: float, is_bottom: bool, policy: GradientPolicy | None = None) -> float`: transform a gradient according to the active policy.
- `apply_policy_vector(...)`: vectorised version of `apply_policy`.

### Computation graph (`zeroproof.autodiff.graph`)
- `SCMNode`: lightweight computation node carrying a forward `SCMValue`, autodiff metadata, and an `is_bottom` flag for policy routing.
  - Constructors: `SCMNode.constant(value)`, `SCMNode.stop_gradient(node)`.
  - Primitives: `add`, `sub`, `mul`, `div`, each propagating bottom semantics.
  - Utilities: `backward(upstream=1.0, policy=None)`, `trace(depth=0)`.
- Functional helpers mirror the methods: `add`, `sub`, `mul`, `div`, `stop_gradient`.

### Projective tuples (`zeroproof.autodiff.projective`)
- `ProjectiveSample`: dataclass representing a homogeneous tuple `(N, D)`.
- `encode(value: SCMValue) -> ProjectiveSample`: lift an SCM value to projective coordinates (finite → `(x, 1)`, bottom → `(1, 0)`).
- `decode(sample: ProjectiveSample) -> SCMValue`: map a projective tuple back to SCM, emitting `⊥` when `D = 0`.
- `renormalize(numerator, denominator, gamma=1e-9, stop_gradient=None)`: detached renormalisation used in projective training (auto-detects Torch/JAX tensors and applies `detach`/`stop_gradient` to the norm).
- `projectively_equal(a, b, atol=1e-8) -> bool`: compare projective tuples up to scaling.

## Training helpers (`zeroproof.training`)

- `zeroproof.training.targets.lift_targets`: lift scalar targets to projective tuples for loss computation.
- `zeroproof.training.sampler.AdaptiveSampler`: wraps PyTorch dataloaders with singularity-aware sampling weights.
- `zeroproof.training.trainer.SCMTrainer`: v0.4 training loop integrating projective decoding, coverage tracking, and gradient policies.

## Losses (`zeroproof.losses`)

- `implicit_loss`, `margin_loss`, `sign_consistency_loss`, and `rejection_loss` implement the objectives described in `concept.tex`.
- `SCMTrainingLoss` combines the individual terms with configurable weights (`λ_margin`, `λ_sign`, `λ_rej`).

## How to read this page

The functions above intentionally mirror the conceptual contract from
`concept.tex`: **train on smooth, infer on strict**. Use the docstrings in each
module for parameter details and examples; this page is a signpost for the
available surfaces.
