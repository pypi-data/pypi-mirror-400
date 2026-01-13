"""
Train a single SCMRational layer on a simple rational target.
"""
from __future__ import annotations

import torch

from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.layers import SCMRationalLayer


def make_dataset(n: int = 256) -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.linspace(-2.0, 2.0, steps=n)
    target = torch.where(x == 0, torch.tensor(float("nan")), x / (x + 1))
    return x, target


def train_layer() -> SCMRationalLayer:
    x, target = make_dataset()
    layer = SCMRationalLayer(2, 2, gradient_policy=GradientPolicy.PROJECT)
    optimizer = torch.optim.Adam(layer.parameters(), lr=5e-3)

    for _ in range(400):
        pred, bottom = layer(x)
        finite_mask = ~bottom & torch.isfinite(target)
        safe_pred = torch.nan_to_num(pred, nan=0.0)
        safe_target = torch.nan_to_num(target, nan=0.0)
        mse = torch.mean((safe_pred - safe_target) ** 2)
        coverage_penalty = (1.0 - finite_mask.float().mean())
        loss = mse + 0.05 * coverage_penalty
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)

    return layer


def evaluate(layer: SCMRationalLayer) -> None:
    x, target = make_dataset()
    pred, bottom = layer(x)
    finite_mask = ~bottom & torch.isfinite(target)
    mse = torch.mean((pred[finite_mask] - target[finite_mask]) ** 2).item()
    print(f"finite coverage: {float(finite_mask.float().mean()):.3f}")
    print(f"finite mse     : {mse:.6f}")


def main() -> None:
    layer = train_layer()
    evaluate(layer)


if __name__ == "__main__":
    main()
