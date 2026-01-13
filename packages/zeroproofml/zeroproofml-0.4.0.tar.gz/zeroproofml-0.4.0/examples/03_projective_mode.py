"""
Demonstrate projective training vs. strict SCM inference.
"""
from __future__ import annotations

import torch

from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.inference.mode import InferenceConfig, SCMInferenceWrapper
from zeroproof.layers import SCMRationalLayer


def make_dataset(n: int = 128) -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.linspace(-4.0, 4.0, steps=n)
    y = torch.where(x == 0, torch.tensor(float("nan")), (x**2 - 1) / (x))
    return x, y


def train_projective_layer() -> SCMRationalLayer:
    x, y = make_dataset()
    layer = SCMRationalLayer(2, 2, gradient_policy=GradientPolicy.PROJECT)
    optimizer = torch.optim.SGD(layer.parameters(), lr=1e-2, momentum=0.9)

    for _ in range(200):
        pred, bottom = layer(x)
        finite_mask = ~bottom & torch.isfinite(y)
        safe_pred = torch.nan_to_num(pred, nan=0.0)
        safe_target = torch.nan_to_num(y, nan=0.0)
        loss = torch.mean((safe_pred - safe_target) ** 2)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
    return layer


def evaluate(layer: SCMRationalLayer) -> None:
    x, y = make_dataset()
    wrapper = SCMInferenceWrapper(layer.eval(), config=InferenceConfig(tau_infer=1e-3, tau_train=1e-2))
    decoded, bottom_mask, gap_mask = wrapper(x)
    finite_mask = ~bottom_mask & torch.isfinite(decoded) & torch.isfinite(y)
    mse = torch.mean((decoded[finite_mask] - y[finite_mask]) ** 2).item() if finite_mask.any() else float("nan")
    print(f"coverage: {float((~bottom_mask).float().mean()):.3f}")
    print(f"gap rate: {float(gap_mask.float().mean()):.3f}")
    print(f"mse     : {mse:.6f}")


def main() -> None:
    layer = train_projective_layer()
    evaluate(layer)


if __name__ == "__main__":
    main()
