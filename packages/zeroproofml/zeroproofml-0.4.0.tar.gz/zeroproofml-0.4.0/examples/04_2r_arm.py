"""
Two-link planar arm inverse kinematics with SCM safety.
"""
from __future__ import annotations

import torch

from zeroproof.inference.mode import InferenceConfig, strict_inference


def forward_kinematics(theta1: torch.Tensor, theta2: torch.Tensor, length: float = 1.0) -> tuple[torch.Tensor, torch.Tensor]:
    x = length * (torch.cos(theta1) + torch.cos(theta1 + theta2))
    y = length * (torch.sin(theta1) + torch.sin(theta1 + theta2))
    return x, y


def pseudo_inverse_control(target_x: float, target_y: float) -> None:
    theta = torch.tensor([0.5, -0.5], requires_grad=True)
    optimizer = torch.optim.Adam([theta], lr=1e-2)

    for _ in range(200):
        x, y = forward_kinematics(theta[0], theta[1])
        numerator = torch.stack([x, y], dim=-1).sum()
        c1, s1 = torch.cos(theta[0]), torch.sin(theta[0])
        c12, s12 = torch.cos(theta.sum()), torch.sin(theta.sum())
        jacobian = torch.tensor(
            [[-s1 - s12, -s12], [c1 + c12, c12]], dtype=theta.dtype, device=theta.device
        )
        denominator = torch.linalg.det(jacobian)
        decoded, bottom_mask, _ = strict_inference(numerator, denominator, config=InferenceConfig(tau_infer=1e-3))
        finite_mask = ~bottom_mask
        loss = (decoded - torch.tensor(target_x + target_y)) ** 2
        loss = torch.where(finite_mask, loss, torch.zeros_like(loss))
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
    print(f"theta*: {theta.detach().tolist()}")


def main() -> None:
    pseudo_inverse_control(1.0, 0.5)


if __name__ == "__main__":
    main()
