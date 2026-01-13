# Coverage Control & Rejection Loss (v0.4 SCM)

In v0.4, singularities are represented by `⊥` (bottom). Training must balance:
- **fit quality** on finite regions, and
- **coverage** (how often the model produces a finite output instead of `⊥`)

ZeroProofML provides:
- a coverage metric (`zeroproof.losses.coverage`)
- a rejection loss (`zeroproof.losses.rejection_loss`)
- an aggregate objective (`zeroproof.losses.SCMTrainingLoss`)

## Coverage metric

Coverage is the fraction of samples that are **not** bottom:

```python
import torch
from zeroproof.losses import coverage

# bottom_mask: True means ⊥
bottom_mask = torch.tensor([False, True, False])
cov = coverage(outputs=torch.empty(3), is_bottom=bottom_mask)
```

In Torch SCM layers, the mask often comes directly from the model (e.g. `SCMRationalLayer`).

## Rejection loss

`rejection_loss` penalises coverage falling below a target:

```python
from zeroproof.losses import rejection_loss

rej = rejection_loss(bottom_mask, target_coverage=0.95)
```

This is designed to be combined with your fit loss. The default form is a simple squared hinge on `(target_coverage - actual_coverage)`.

## Using `SCMTrainingLoss`

`SCMTrainingLoss` mixes:
- implicit fit loss (division-free)
- margin loss on denominators
- sign consistency (projective orientation)
- rejection loss (coverage control)

```python
from zeroproof.losses import LossConfig, SCMTrainingLoss

loss_fn = SCMTrainingLoss(LossConfig(target_coverage=0.95, lambda_rej=0.01))
# total, breakdown = loss_fn(fit_loss, P, Q, Y_n, Y_d, is_bottom=bottom_mask, ...)
```

## Notes

- v0.4 does **not** ship an “adaptive λ” controller in the core. If you want a true Lagrange-multiplier style update, implement it outside the library by adjusting `lambda_rej` over time based on observed coverage.
- For training loops, `SCMTrainer` can early-stop when coverage remains below a threshold (`TrainingConfig.coverage_threshold` and `coverage_patience`).
