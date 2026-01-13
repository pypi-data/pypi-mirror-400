# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Utilities for preparing training targets in projective form."""

from __future__ import annotations

from typing import Any

import torch
from torch import Tensor

__all__ = ["lift_targets", "lift_targets_torch", "lift_targets_jax"]


def _is_jax_array(x: Any) -> bool:
    try:  # pragma: no cover - lazy import for optional dependency
        import jax

        return isinstance(x, jax.Array)
    except Exception:  # pragma: no cover - defensive
        return False


def lift_targets_torch(targets: Tensor) -> tuple[Tensor, Tensor]:
    """Torch implementation of projective lifting."""

    is_inf = torch.isinf(targets)
    is_nan = torch.isnan(targets)

    numer = torch.where(is_inf, torch.sign(targets), targets)
    numer = torch.where(is_nan, torch.ones_like(numer), numer)

    denom = torch.where(is_inf | is_nan, torch.zeros_like(numer), torch.ones_like(numer))
    return numer, denom


def lift_targets_jax(targets: Any) -> tuple[Any, Any]:
    """JAX implementation of projective lifting."""

    import jax.numpy as jnp

    is_inf = jnp.isinf(targets)
    is_nan = jnp.isnan(targets)

    numer = jnp.where(is_inf, jnp.sign(targets), targets)
    numer = jnp.where(is_nan, jnp.ones_like(numer), numer)

    denom = jnp.where(is_inf | is_nan, jnp.zeros_like(numer), jnp.ones_like(numer))
    return numer, denom


def lift_targets(targets: Any) -> tuple[Any, Any]:
    """Convert scalar targets to projective tuples ``(Y_n, Y_d)``.

    Dispatches to the appropriate backend (Torch or JAX) so demos and
    integration tests can share the same lifting API.
    """

    if isinstance(targets, torch.Tensor):
        return lift_targets_torch(targets)
    if _is_jax_array(targets):  # pragma: no branch - cheap predicate
        return lift_targets_jax(targets)
    raise TypeError("lift_targets expects a torch.Tensor or jax.Array")
