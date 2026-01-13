"""
Quick Torch TRRational demo with TensorBoard logging.

Generates a synthetic 1D dataset (y = sin(x)) and trains a TorchTRRational.
Logs scalars and histograms to TensorBoard if available.

Usage:
  python examples/torch_quick_demo.py
Then:
  tensorboard --logdir runs/torch_demo
"""

from __future__ import annotations

import hashlib
import os


def _require_torch():
    try:
        import torch  # type: ignore

        return torch
    except Exception as e:
        print("PyTorch not available:", e)
        raise SystemExit(0)


def dataset_checksum(x, y) -> str:
    m = hashlib.sha256()
    m.update(x.detach().cpu().numpy().tobytes())
    m.update(y.detach().cpu().numpy().tobytes())
    return m.hexdigest()[:16]


def main() -> None:
    torch = _require_torch()
    from zeroproof.layers import TorchTRRational
    from zeroproof.training import TorchTrainingConfig, train_torch_rational

    torch.set_default_dtype(torch.float64)

    # Synthetic dataset
    x = torch.linspace(-2.0, 2.0, 1024, dtype=torch.float64)
    y = torch.sin(x)
    x = x.requires_grad_(True)

    # Model
    model = TorchTRRational(d_p=3, d_q=2)

    # Run dir for TB
    run_dir = os.environ.get("ZP_TB_DIR", "runs/torch_demo")
    ds_hash = dataset_checksum(x, y)

    cfg = TorchTrainingConfig(
        learning_rate=1e-3,
        max_epochs=200,
        seed=42,
        enable_tensorboard=True,
        tb_log_dir=run_dir,
    )

    print("Training TorchTRRational on y=sin(x) ...")
    metrics = train_torch_rational(model, x, y, cfg)
    print("Final metrics:", metrics)
    print("Dataset checksum:", ds_hash)
    print("Run dir:", run_dir)


if __name__ == "__main__":
    main()

