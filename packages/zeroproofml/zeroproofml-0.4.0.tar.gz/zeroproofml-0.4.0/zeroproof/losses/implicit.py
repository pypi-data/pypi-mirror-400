# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Implicit cross-product loss for projective tuples."""

from __future__ import annotations

import torch
from torch import Tensor
from typing import Any


def implicit_loss(
    P: Tensor,
    Q: Tensor,
    Y_n: Tensor,
    Y_d: Tensor,
    gamma: float = 1e-9,
    *,
    detach_scale: bool = True,
) -> Tensor:
    """Measure fit between predicted and target projective tuples.

    The loss penalises the squared cross-product of ``(P, Q)`` and ``(Y_n, Y_d)``
    while normalising by a scale factor that discourages tiny denominators.
    ``gamma`` guards against degenerate cases where both tuples are at the
    origin.
    """

    cross = P * Y_d - Q * Y_n
    error = cross**2

    # Use a detached squared-norm scale factor (concept.tex / todo.md): this makes the loss
    # invariant to projective re-scaling of (P, Q) in the regime where `gamma` is negligible,
    # and prevents gradients from "optimizing the scale" rather than the direction.
    scale_sq = Q.pow(2) * Y_d.pow(2) + P.pow(2) * Y_n.pow(2)
    if bool(detach_scale):
        scale_sq = scale_sq.detach()
    scale_sq = scale_sq + gamma
    return (error / scale_sq).mean()


def implicit_loss_jax(P: Any, Q: Any, Y_n: Any, Y_d: Any, gamma: float = 1e-9) -> Any:
    """JAX-compatible implicit loss."""

    import jax.numpy as jnp
    import jax

    cross = P * Y_d - Q * Y_n
    error = cross**2

    scale_sq = jax.lax.stop_gradient(Q**2 * Y_d**2 + P**2 * Y_n**2) + gamma
    return jnp.mean(error / scale_sq)
