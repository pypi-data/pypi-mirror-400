# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Adaptive sampling utilities for SCM training.

The sampler follows the design sketched in ``todo.md`` Phase 5:

* Estimate the probability of hitting a singularity via a smooth sigmoid
  around the training threshold ``τ_train``.
* Smooth the probability estimate with an exponential moving average to
  avoid oscillations during training.
* Convert the smoothed probabilities into sampling weights with a
  configurable floor, so that rare but safety-critical regions are not
  ignored.
* Provide an ``AdaptiveSampler`` wrapper that can be plugged into a
  standard PyTorch ``DataLoader``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

import torch
from torch import Tensor
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

__all__ = [
    "singularity_prob",
    "ema_update",
    "sampling_weights",
    "AdaptiveSampler",
]


def singularity_prob(q_values: Tensor, tau_train: float, beta: float = 0.1) -> Tensor:
    """Estimate singularity probability using a sigmoid around ``τ_train``.

    The estimate follows the formula in the Phase 5 to-do list:

    ``sigmoid((τ_train - |Q_net|) / β)``.
    """

    return torch.sigmoid((tau_train - torch.abs(q_values)) / beta)


def ema_update(previous: Tensor, current: Tensor, gamma: float = 0.1) -> Tensor:
    """Exponential moving average used for smoothing probability estimates."""

    return gamma * current + (1 - gamma) * previous


def sampling_weights(
    probabilities: Tensor,
    bottom_mask: Optional[Tensor] = None,
    *,
    alpha: float = 1.0,
    s_min: float = 0.1,
) -> Tensor:
    """Compute sampling weights with a configurable floor.

    The weight formula mirrors the guidance from ``todo.md``:

    ``S_i ∝ max(S_min, 1 + α · |P̃_i - 𝟙(y_i = ⊥)|)``

    ``bottom_mask`` marks samples whose target is ``⊥``; if omitted it is
    treated as all zeros.
    """

    if bottom_mask is None:
        bottom_mask = torch.zeros_like(probabilities, dtype=probabilities.dtype)

    deviation = torch.abs(probabilities - bottom_mask)
    weights = 1 + alpha * deviation
    return torch.clamp(weights, min=s_min)


@dataclass
class AdaptiveSamplerConfig:
    """Configuration for :class:`AdaptiveSampler`."""

    tau_train: float = 1e-4
    beta: float = 0.1
    gamma: float = 0.1
    alpha: float = 1.0
    s_min: float = 0.1
    batch_size: int = 32
    num_workers: int = 0
    drop_last: bool = False
    pin_memory: bool = False


class AdaptiveSampler:
    """Wrap a dataset with adaptive sampling based on singularity risk."""

    def __init__(
        self,
        dataset: Dataset[object],
        config: AdaptiveSamplerConfig | None = None,
    ) -> None:
        self.dataset: Dataset[object] = dataset
        self.config = config or AdaptiveSamplerConfig()
        self._smoothed_prob = torch.zeros(len(dataset), dtype=torch.float32)
        self._weights = torch.ones(len(dataset), dtype=torch.float32)

    @property
    def weights(self) -> Tensor:
        return self._weights

    def update(self, q_values: Tensor, bottom_mask: Optional[Tensor] = None) -> None:
        """Update internal weights given model denominator estimates.

        ``q_values`` should be ordered consistently with the dataset's
        indexing. The call performs three steps:

        1. Estimate singularity probability using :func:`singularity_prob`.
        2. Smooth the estimate with :func:`ema_update`.
        3. Convert the smoothed values into sampling weights via
           :func:`sampling_weights`.
        """

        probs = singularity_prob(q_values, self.config.tau_train, self.config.beta)
        self._smoothed_prob = ema_update(self._smoothed_prob, probs, self.config.gamma)
        self._weights = sampling_weights(
            self._smoothed_prob,
            bottom_mask,
            alpha=self.config.alpha,
            s_min=self.config.s_min,
        )

    def _sampler(self) -> WeightedRandomSampler:
        return WeightedRandomSampler(self._weights, num_samples=len(self.dataset), replacement=True)

    def dataloader(self, **overrides: object) -> DataLoader[object]:
        """Build a ``DataLoader`` using the latest adaptive weights."""

        params: dict[str, object] = {
            "batch_size": self.config.batch_size,
            "num_workers": self.config.num_workers,
            "drop_last": self.config.drop_last,
            "pin_memory": self.config.pin_memory,
        }
        params.update(overrides)
        return DataLoader(
            self.dataset,
            sampler=self._sampler(),
            **params,
        )

    def __iter__(self) -> Iterator[object]:
        return iter(self.dataloader())

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self.dataset)
