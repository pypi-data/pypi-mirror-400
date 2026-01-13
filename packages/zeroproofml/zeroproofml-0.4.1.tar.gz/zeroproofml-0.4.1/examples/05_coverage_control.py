"""
Demonstrate coverage-aware loss shaping for SCM outputs.
"""
from __future__ import annotations

import torch

from zeroproof.layers import SCMRationalLayer


def synthetic_batch(batch_size: int = 64) -> torch.Tensor:
    return torch.linspace(-2.0, 2.0, steps=batch_size)


def coverage_loss(predictions: torch.Tensor, bottom_mask: torch.Tensor, target_coverage: float = 0.95) -> torch.Tensor:
    actual = 1.0 - bottom_mask.float().mean()
    gap = torch.relu(target_coverage - actual)
    return gap**2


def train_with_coverage(target_coverage: float = 0.9) -> None:
    x = synthetic_batch()
    target = torch.tanh(x)
    model = SCMRationalLayer(2, 2)
    optim = torch.optim.Adam(model.parameters(), lr=1e-2)

    for _ in range(200):
        pred, bottom = model(x)
        finite_mask = ~bottom
        safe_pred = torch.nan_to_num(pred, nan=0.0)
        mse = torch.mean((safe_pred[finite_mask] - target[finite_mask]) ** 2)
        loss = mse + 0.5 * coverage_loss(pred, bottom, target_coverage)
        loss.backward()
        optim.step()
        optim.zero_grad(set_to_none=True)

    pred, bottom = model(x)
    coverage = 1.0 - bottom.float().mean()
    print(f"target coverage: {target_coverage:.2f}")
    print(f"achieved       : {float(coverage):.3f}")


def main() -> None:
    train_with_coverage()


if __name__ == "__main__":
    main()
