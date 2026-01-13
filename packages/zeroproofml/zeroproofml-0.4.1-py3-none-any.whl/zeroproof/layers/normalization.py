# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Normalization layers aware of Signed Common Meadows."""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch import Tensor

from zeroproof.autodiff.policies import GradientPolicy, get_policy, register_policy

register_policy("scm_norm", GradientPolicy.CLAMP)
register_policy("scm_softmax", GradientPolicy.CLAMP)


def _apply_policy_tensor(gradients: Tensor, mask: Tensor, policy: GradientPolicy) -> Tensor:
    """Apply a gradient policy elementwise respecting SCM masks."""

    zeroed = torch.zeros_like(gradients)

    if policy is GradientPolicy.REJECT:
        return zeroed

    if policy is GradientPolicy.PROJECT:
        return torch.where(mask, zeroed, gradients)

    if policy is GradientPolicy.CLAMP:
        masked = torch.where(mask, zeroed, gradients)
        if torch.is_complex(masked):
            return masked
        return torch.clamp(masked, -1.0, 1.0)

    return gradients


def _masked_mean_var(x: Tensor, mask: Tensor | None, dim: int) -> tuple[Tensor, Tensor, Tensor]:
    """Compute mean/var excluding masked entries."""

    if mask is None:
        valid = torch.ones_like(x, dtype=torch.bool)
    else:
        valid = ~mask

    count = valid.sum(dim=dim, keepdim=True)
    zero_count = count == 0
    safe_count = torch.where(zero_count, torch.ones_like(count), count)
    mean = (x * valid).sum(dim=dim, keepdim=True) / safe_count
    var = ((x - mean) ** 2 * valid).sum(dim=dim, keepdim=True) / safe_count
    return mean.squeeze(dim), var.squeeze(dim), zero_count.squeeze(dim)


@dataclass(eq=False)
class SCMNorm(nn.Module):  # type: ignore[misc]
    """Batch-style normalization that ignores ``⊥`` entries."""

    deterministic: bool = True
    eps: float = 0.0
    gradient_policy: GradientPolicy | None = None

    def __post_init__(self) -> None:  # pragma: no cover - handled by nn.Module
        super().__init__()

    def forward(self, x: Tensor, bottom_mask: Tensor | None = None) -> tuple[Tensor, Tensor]:
        mean, var, zero_count = _masked_mean_var(x, bottom_mask, dim=0)
        singular = (var <= 0) | zero_count.squeeze(0)
        denom = torch.sqrt(var + self.eps)
        normalised = (x - mean) / torch.where(singular, torch.ones_like(denom), denom)
        out_mask = singular | (
            bottom_mask if bottom_mask is not None else torch.zeros_like(x, dtype=torch.bool)
        )
        normalised = torch.where(out_mask, torch.full_like(normalised, float("nan")), normalised)
        policy = self.gradient_policy or get_policy("scm_norm")
        if policy is not GradientPolicy.PASSTHROUGH:
            normalised = normalised + torch.zeros_like(normalised, requires_grad=True)

            def _mask_grad(grad: Tensor) -> Tensor:
                return _apply_policy_tensor(grad, out_mask, policy)

            normalised.register_hook(_mask_grad)
        return normalised, out_mask


@dataclass(eq=False)
class SCMSoftmax(nn.Module):  # type: ignore[misc]
    """Softmax surrogate that respects singular logits."""

    gradient_policy: GradientPolicy | None = None

    def __post_init__(self) -> None:  # pragma: no cover - handled by nn.Module
        super().__init__()

    def forward(self, logits: Tensor, bottom_mask: Tensor | None = None) -> tuple[Tensor, Tensor]:
        if bottom_mask is None:
            bottom_mask = torch.zeros_like(logits, dtype=torch.bool)

        masked_logits = torch.where(bottom_mask, torch.full_like(logits, float("-inf")), logits)
        singular_rows = bottom_mask.any(dim=-1, keepdim=True)

        # Stable softmax
        shifted = masked_logits - masked_logits.max(dim=-1, keepdim=True).values
        probs = torch.softmax(shifted, dim=-1)

        # One-hot override for singular rows
        if singular_rows.any():
            argmax = torch.argmax(masked_logits, dim=-1, keepdim=True)
            one_hot = torch.zeros_like(probs).scatter_(-1, argmax, 1.0)
            probs = torch.where(singular_rows, one_hot, probs)

        policy = self.gradient_policy or get_policy("scm_softmax")
        if policy is not GradientPolicy.PASSTHROUGH:
            probs = probs + torch.zeros_like(probs, requires_grad=True)

            def _mask_grad(grad: Tensor) -> Tensor:
                # Softmax can carry both row-wise singular masks and explicit ⊥ masks.
                row_mask = singular_rows.squeeze(-1)
                combined_mask = row_mask | bottom_mask.any(dim=-1)
                mask = combined_mask.unsqueeze(-1).expand_as(grad)
                return _apply_policy_tensor(grad, mask, policy)

            probs.register_hook(_mask_grad)

        return probs, singular_rows.squeeze(-1)
