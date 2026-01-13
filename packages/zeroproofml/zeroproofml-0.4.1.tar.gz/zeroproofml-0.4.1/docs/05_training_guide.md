# Training Guide

This guide covers the v0.4 trainer loop and how to combine SCM semantics with coverage-aware optimisation.

## Trainer Overview
- `training.trainer.SCMTrainer` implements the reference loop with mixed precision, gradient accumulation, and coverage-based early stopping.
- Targets are lifted to projective tuples via `training.targets.lift_targets` to unify finite and infinite labels.
- Thresholds are perturbed per batch (`perturbed_threshold`) to reduce train/infer gaps.

## Typical Flow
1. **Prepare data** with finite/infinite labels; lift to `(Y_n, Y_d)` inside the trainer.
2. **Select gradient policy** (usually `CLAMP` for SCM-only graphs or `PROJECT` for projective heads).
3. **Assemble losses**: implicit + margin + sign consistency + rejection (via `SCMTrainingLoss`).
4. **Train loop**:
   - forward pass (SCM or projective mode),
   - compute losses and coverage,
   - backprop using the active gradient policy,
   - update optimiser (supports AMP through `torch.cuda.amp`).
5. **Monitor coverage**; early stop when coverage stays below `coverage_threshold` for `coverage_patience` epochs.

## Tips
- Treat NaN outputs as ⊥ when computing coverage during training.
- Keep `τ_train_min` and `τ_train_max` close unless you specifically need stronger perturbations.
- Log `last_thresholds` from the trainer to understand how often the model sees near-singular regimes.
