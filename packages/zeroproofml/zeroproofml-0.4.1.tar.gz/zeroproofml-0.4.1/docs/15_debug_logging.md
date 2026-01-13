# Debug Logging (v0.4 SCM)

ZeroProofML v0.4 keeps logging lightweight: the core trainer exposes a per-step `log_hook` callback, and most examples rely on standard Python logging / printing.

## Python logging basics

```python
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("zeroproof").setLevel(logging.INFO)
```

## Capturing per-step metrics from `SCMTrainer`

`zeroproof.training.trainer.TrainingConfig` accepts a `log_hook(metrics)` callable. The trainer calls it with a small dict containing at least:
- `loss` (float)
- `coverage` (float; fraction of non-⊥ predictions)

Example: write JSONL metrics.

```python
import json
from pathlib import Path

from zeroproof.training.trainer import TrainingConfig, SCMTrainer

log_path = Path("runs/scm_train_metrics.jsonl")
log_path.parent.mkdir(parents=True, exist_ok=True)

def log_hook(metrics):
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({k: (float(v) if hasattr(v, "__float__") else v) for k, v in metrics.items()}) + "\n")

cfg = TrainingConfig(log_hook=log_hook)
# trainer = SCMTrainer(..., config=cfg)
# trainer.fit()
```

## Debugging `⊥` propagation

- For Torch layers, inspect `bottom_mask` directly (e.g., from `SCMRationalLayer.forward`).
- For vectorised backends (`zeroproof.scm.ops`), log both `(payload, mask)`; the payload is intentionally zeroed at `mask=True` positions to keep tensor math stable.
