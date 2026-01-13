# Coverage & Rejection — Quick Summary (v0.4 SCM)

- Singularities are represented by the single bottom element `⊥` (and a boolean mask in tensor code).
- **Coverage** measures the fraction of non-`⊥` outputs.
- **Rejection loss** penalises falling below a target coverage.
- `SCMTrainingLoss` combines fit + margin + sign + rejection into one callable.

Start here:
- Coverage / rejection: `zeroproof/losses/coverage.py`
- Combined loss: `zeroproof/losses/__init__.py` (`LossConfig`, `SCMTrainingLoss`)
- Training loop + early stop: `zeroproof/training/trainer.py`
