# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Loss functions tailored for Signed Common Meadows."""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor

from zeroproof.autodiff.policies import get_policy

from .coverage import coverage, rejection_loss
from .implicit import implicit_loss, implicit_loss_jax
from .margin import margin_loss
from .sign import sign_consistency_loss

__all__ = [
    "coverage",
    "implicit_loss",
    "margin_loss",
    "rejection_loss",
    "sign_consistency_loss",
    "implicit_loss_jax",
    "LossConfig",
    "SCMTrainingLoss",
]


@dataclass
class LossConfig:
    """Hyperparameters for combined SCM training loss."""

    gamma: float = 1e-9
    tau_train: float = 1e-4
    epsilon_sing: float = 1e-3
    lambda_margin: float = 0.1
    lambda_sign: float = 1.0
    lambda_rej: float = 0.01
    target_coverage: float = 0.95


class SCMTrainingLoss:
    """Aggregate SCM loss suitable for end-to-end training."""

    def __init__(self, config: LossConfig | None = None):
        self.config = config or LossConfig()

    def __call__(
        self,
        fit_loss: Tensor,
        P: Tensor,
        Q: Tensor,
        Y_n: Tensor,
        Y_d: Tensor,
        *,
        is_bottom: Tensor | None = None,
        mask_finite: Tensor | None = None,
        mask_singular: Tensor | None = None,
        tau_train: float | None = None,
    ) -> tuple[Tensor, dict[str, Tensor]]:
        """Combine fit loss with margin, sign, and rejection components."""

        tau = self.config.tau_train if tau_train is None else float(tau_train)
        margin = margin_loss(Q, tau_train=tau, mask_finite=mask_finite)
        sign = sign_consistency_loss(
            P,
            Q,
            Y_n,
            Y_d,
            gamma=self.config.gamma,
            mask_singular=mask_singular,
        )

        if is_bottom is None:
            rej = torch.zeros((), device=fit_loss.device, dtype=fit_loss.dtype)
        else:
            rej = rejection_loss(
                is_bottom,
                target_coverage=self.config.target_coverage,
                policy=get_policy("rejection_loss"),
            )

        total = (
            fit_loss
            + self.config.lambda_margin * margin
            + self.config.lambda_sign * sign
            + self.config.lambda_rej * rej
        )

        breakdown = {
            "fit": fit_loss.detach(),
            "margin": margin.detach(),
            "sign": sign.detach(),
            "rejection": rej.detach(),
            "total": total.detach(),
        }
        return total, breakdown
