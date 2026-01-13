# ZeroProofML

<div align="center">

**Machine learning that handles division by zero gracefully**

[![Tests (Ubuntu)](https://img.shields.io/github/actions/workflow/status/domezsolt/zeroproofml/tests-ubuntu.yml?branch=main&label=Tests%20(Ubuntu))](https://github.com/domezsolt/zeroproofml/actions/workflows/tests-ubuntu.yml)
[![Tests (Windows)](https://img.shields.io/github/actions/workflow/status/domezsolt/zeroproofml/tests-windows.yml?branch=main&label=Tests%20(Windows))](https://github.com/domezsolt/zeroproofml/actions/workflows/tests-windows.yml)
[![Lint](https://img.shields.io/github/actions/workflow/status/domezsolt/zeroproofml/lint.yml?branch=main&label=Lint)](https://github.com/domezsolt/zeroproofml/actions/workflows/lint.yml)
[![Coverage](https://img.shields.io/github/actions/workflow/status/domezsolt/zeroproofml/coverage.yml?branch=main&label=Coverage)](https://github.com/domezsolt/zeroproofml/actions/workflows/coverage.yml)

*Built on Signed Common Meadow (SCM) semantics for totalized arithmetic*

</div>

## What is ZeroProofML?

ZeroProofML is a PyTorch library that enables neural networks to learn functions with singularities—like `1/x` near zero or gravitational potentials—without numerical instabilities or undefined behavior. Instead of treating division by zero as an error, we use **Signed Common Meadow (SCM)** semantics to provide a mathematically rigorous foundation for arithmetic operations that remain well-defined everywhere.

### Key capabilities

- **Totalized arithmetic**: Singular operations map to an absorptive bottom element `⊥`, tracked by explicit masks (and optionally represented as `NaN` payloads at strict decode time)
- **Smooth training**: Optional projective mode with `⟨N,D⟩` tuples and "ghost gradients" keeps optimization stable near singularities
- **Strict inference**: Decode projective outputs with configurable thresholds (`τ_infer`, `τ_train`) and obtain `bottom_mask` / `gap_mask` for rejection or safe fallbacks
- **Orientation tracking**: Weak-sign protocol provides direction/orientation information near singularities
- **PyTorch integration**: Drop-in rational layers, SCM-aware losses, and JIT-compatible operations

## When to use ZeroProofML

ZeroProofML excels in domains where singularities arise naturally:

- **Physics**: Gravitational/electrostatic potentials (`1/r`), collision dynamics, quantum mechanics
- **Robotics**: Inverse kinematics with joint limits, collision avoidance fields
- **Computer vision**: Homogeneous coordinates, projective geometry, structure-from-motion
- **Scientific computing**: Learning differential equations with singular solutions, rational approximations

## Quick start

```bash
# install with a backend
pip install -e ".[torch]"
```

```python
import torch
from torch.utils.data import DataLoader, TensorDataset

from zeroproof.inference import InferenceConfig, SCMInferenceWrapper
from zeroproof.layers.projective_rational import ProjectiveRRModelConfig, RRProjectiveRationalModel
from zeroproof.losses.implicit import implicit_loss
from zeroproof.training import SCMTrainer, TrainingConfig

# Toy example: learn a 1D rational function (targets may include inf/NaN for singular labels).
x = torch.linspace(-1.0, 1.0, 2048).unsqueeze(-1)
y = 1.0 / (x + 0.1)
train_loader = DataLoader(TensorDataset(x, y), batch_size=256, shuffle=True)

model = RRProjectiveRationalModel(
    ProjectiveRRModelConfig(input_dim=1, output_dim=1, numerator_degree=3, denominator_degree=2)
)
wrapped = SCMInferenceWrapper(model, config=InferenceConfig(tau_infer=1e-6, tau_train=1e-4))

def loss_fn(outputs, lifted_targets):
    P, Q = outputs
    Y_n, Y_d = lifted_targets
    return implicit_loss(P, Q, Y_n, Y_d)

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
trainer = SCMTrainer(
    model=model,
    optimizer=optimizer,
    loss_fn=loss_fn,
    train_loader=train_loader,
    config=TrainingConfig(max_epochs=20),
)
trainer.fit()

# Strict inference (decoded uses NaN for ⊥ payloads; masks are authoritative).
wrapped.eval()
decoded, bottom_mask, gap_mask = wrapped(x)
```

See `examples/` and `documentation_full.md` for end-to-end demos and recommended patterns.

## How it works

ZeroProofML implements a two-phase training paradigm:

1. **Training mode (smooth/projective)**: Networks learn rational functions as projective tuples `⟨N,D⟩` with detached normalization, allowing smooth gradients even when denominators approach zero
2. **Inference mode (strict SCM)**: Outputs are decoded with configurable thresholds; small denominators trigger `⊥` and are surfaced via `bottom_mask` / `gap_mask` (decoded payloads use `NaN` for `⊥`)

This approach combines the stability of smooth optimization with the rigor of totalized arithmetic, enabling reliable deployment in safety-critical domains.

## Architecture

```
zeroproof/
├── scm/          # SCM values + totalized ops (⊥ semantics)
├── autodiff/     # Gradient policies + projective helpers
├── layers/       # PyTorch SCM layers (rational heads, normalization)
├── losses/       # SCM-aware losses (fit/margin/sign/rejection)
├── training/     # Trainer loop + target lifting utilities
├── inference/    # Export & deployment helpers
├── metrics/      # Pole & singularity metrics
└── utils/        # IEEE↔SCM bridge, visualization
```

Docs: `docs/00_getting_started.md` | Conceptual background: `concept.tex` | Full reference: `documentation_full.md` | Migration guide: `MIGRATION.md`

## Development

Install development dependencies and run tests:

```bash
pip install -e ".[dev,torch]"
pytest -m "scm and not benchmark" tests -v
```

Run linting and type checking:

```bash
ruff check zeroproof tests
mypy --strict zeroproof
```

Run benchmarks:

```bash
python benchmarks/run_benchmarks.py --output benchmark_results --suite all
```

## Acknowledgements

The theoretical foundation of this library builds on the pioneering work of **Jan A. Bergstra** and **John V. Tucker** on meadows and common meadows—algebraic structures that totalize the field of rational numbers by making division a total operation. Their formalization of division by zero as an absorptive element provides the mathematical rigor underlying our approach.

We extend these foundations to the neural network setting with weak sign tracking, projective training modes, and integration with modern deep learning frameworks.

## Citation

If you use ZeroProofML in your research, please cite:

```bibtex
@software{zeroproofml2025,
  title = {ZeroProofML: Signed Common Meadows for Stable Machine Learning},
  author = {{ZeroProof Team}},
  year = {2025},
  url = {https://github.com/domezsolt/zeroproofml},
  version = {0.4.0}
}
```

## License

MIT License. See `LICENSE` for details.
