# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Training-inference gap mitigation utilities."""

from __future__ import annotations

import torch

__all__ = ["perturbed_threshold"]


def perturbed_threshold(tau_min: float, tau_max: float) -> float:
    """Sample a stochastic threshold within ``[τ_min, τ_max]``.

    The perturbation follows the mitigation strategy described in
    ``concept.tex`` and ``todo.md``: draw uniformly within the specified
    bounds to prevent the network from overfitting to a single boundary.
    """

    if tau_min > tau_max:
        raise ValueError("tau_min must not exceed tau_max")
    if tau_min == tau_max:
        return float(tau_min)
    return float(torch.empty(1).uniform_(tau_min, tau_max).item())
