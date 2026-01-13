# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Coverage and rejection losses for SCM outputs."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from torch import Tensor

from zeroproof.autodiff.policies import GradientPolicy, get_policy, register_policy

register_policy("coverage", GradientPolicy.CLAMP)
register_policy("rejection_loss", GradientPolicy.CLAMP)


def coverage(outputs: Tensor, is_bottom: Tensor, *, policy: GradientPolicy | None = None) -> Tensor:
    """Compute fraction of non-bottom outputs."""

    # ``outputs`` is present for API symmetry; current metric relies on mask only.
    del outputs
    policy = policy or get_policy("coverage")
    coverage_val = 1.0 - is_bottom.float().mean()

    if policy in (GradientPolicy.PROJECT, GradientPolicy.REJECT):
        return coverage_val.detach()

    return coverage_val


def rejection_loss(
    is_bottom: Tensor,
    target_coverage: float = 0.95,
    *,
    policy: GradientPolicy | None = None,
) -> Tensor:
    """Penalise coverage falling below the desired target."""

    import torch

    policy = policy or get_policy("rejection_loss")

    if policy is GradientPolicy.REJECT:
        return torch.zeros((), device=is_bottom.device, dtype=is_bottom.dtype)

    actual = 1.0 - is_bottom.float().mean()
    if policy is GradientPolicy.PROJECT:
        actual = actual.detach()

    return torch.relu(target_coverage - actual) ** 2
