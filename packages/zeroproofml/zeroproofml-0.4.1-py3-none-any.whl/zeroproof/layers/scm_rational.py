# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Rational neural layer with Signed Common Meadow semantics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import torch
import torch.nn as nn
from torch import Tensor

from zeroproof.autodiff.policies import GradientPolicy, get_policy, register_policy


class BasisFunction:
    """Callable basis interface returning feature columns."""

    def __call__(self, x: Tensor, degree: int) -> Tensor:  # pragma: no cover - interface
        raise NotImplementedError


class MonomialBasis(BasisFunction):
    """Standard monomial basis: ``[1, x, x^2, …]``."""

    def __call__(self, x: Tensor, degree: int) -> Tensor:
        exponents = torch.arange(degree + 1, device=x.device, dtype=x.dtype)
        return torch.pow(x.unsqueeze(-1), exponents)


class ChebyshevBasis(BasisFunction):
    """Chebyshev T_n basis for more stable high-degree features."""

    def __call__(self, x: Tensor, degree: int) -> Tensor:
        features = [torch.ones_like(x), x]
        for _ in range(2, degree + 1):
            features.append(2 * x * features[-1] - features[-2])
        return torch.stack(features[: degree + 1], dim=-1)


class CustomBasis(BasisFunction):
    """Wrap a user-provided callable as a ``BasisFunction``."""

    def __init__(self, fn: Callable[[Tensor, int], Tensor]):
        self.fn = fn

    def __call__(self, x: Tensor, degree: int) -> Tensor:
        return self.fn(x, degree)


register_policy("scm_rational", GradientPolicy.PROJECT)


@dataclass(eq=False)
class SCMRationalLayer(nn.Module):  # type: ignore[misc]
    """Parameterized rational function respecting SCM rules."""

    numerator_degree: int
    denominator_degree: int
    basis: BasisFunction = MonomialBasis()
    gradient_policy: GradientPolicy | None = None
    singular_epsilon: float = 1e-6

    def __post_init__(self) -> None:  # pragma: no cover - handled by nn.Module
        super().__init__()
        if self.numerator_degree < 0 or self.denominator_degree < 0:
            raise ValueError("Degrees must be non-negative")
        self.numerator = nn.Parameter(torch.empty(self.numerator_degree + 1))
        self.denominator = nn.Parameter(torch.zeros(self.denominator_degree + 1))

        # Break the scale-symmetry between numerator and denominator so the denominator
        # receives a learning signal even when using naive MSE on the ratio.
        with torch.no_grad():
            nn.init.normal_(self.numerator, mean=0.0, std=1e-2)
            self.denominator[0].fill_(1.0)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Evaluate the rational function and return ``(output, bottom_mask)``.

        ``bottom_mask`` flags denominator singularities, but the forward
        evaluation itself does **not** overwrite singular outputs. Downstream
        callers are responsible for interpreting ``bottom_mask`` as ⊥ during
        inference, keeping with the single-check design principle. Gradients
        on singular paths are filtered by :pyattr:`gradient_policy`.
        """

        basis_feats = self.basis(x, max(self.numerator_degree, self.denominator_degree))
        p_feats = basis_feats[..., : self.numerator_degree + 1]
        q_feats = basis_feats[..., : self.denominator_degree + 1]

        numerator = torch.sum(p_feats * self.numerator, dim=-1)
        denominator = torch.sum(q_feats * self.denominator, dim=-1)

        bottom_mask = torch.isclose(
            denominator,
            torch.zeros((), device=denominator.device, dtype=denominator.dtype),
            atol=self.singular_epsilon,
        )
        output = numerator / denominator

        policy = self.gradient_policy or get_policy("scm_rational")

        if policy is not GradientPolicy.PASSTHROUGH and output.requires_grad:

            def _mask_grad(grad: Tensor) -> Tensor:
                adjusted = apply_policy_vectorized(grad, bottom_mask=bottom_mask, policy=policy)
                return adjusted.reshape_as(grad)

            output.register_hook(_mask_grad)

        return output, bottom_mask


def apply_policy_vectorized(
    gradients: Tensor, bottom_mask: Tensor, policy: GradientPolicy
) -> Tensor:
    """Apply :func:`~zeroproof.autodiff.policies.apply_policy` elementwise."""

    if policy is GradientPolicy.PASSTHROUGH:
        return gradients

    zeroed = torch.zeros_like(gradients)

    if policy is GradientPolicy.REJECT:
        return zeroed

    if policy is GradientPolicy.PROJECT:
        return torch.where(bottom_mask, zeroed, gradients)

    # CLAMP mirrors :func:`apply_policy`: zero-out ⊥ paths then clamp real tensors.
    masked = torch.where(bottom_mask, zeroed, gradients)
    if torch.is_complex(masked):
        return masked
    return torch.clamp(masked, -1.0, 1.0)
