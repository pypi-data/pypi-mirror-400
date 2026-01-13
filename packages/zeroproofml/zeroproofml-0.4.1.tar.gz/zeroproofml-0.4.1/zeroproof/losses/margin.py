# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Margin loss to enforce denominator safety."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from torch import Tensor


def margin_loss(Q: Tensor, tau_train: float = 1e-4, mask_finite: Tensor | None = None) -> Tensor:
    """Penalise denominators that approach the singular region.

    Args:
        Q: Predicted denominators.
        tau_train: Safety margin threshold.
        mask_finite: Optional mask of finite targets to suppress penalties where
            the target itself is singular.
    """

    import torch

    margin = torch.relu(tau_train - torch.abs(Q)) ** 2
    if mask_finite is not None:
        margin = margin * mask_finite
    return margin.mean()
