# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Gradient handling strategies for signed common meadow autodiff.

Phase 9 emphasises clear documentation of the gradient policies that govern
how paths involving the absorptive bottom ``⊥`` contribute to learning. These
helpers are intentionally lightweight so they can be referenced directly in
the user guides and API reference.
"""

from __future__ import annotations

import enum
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Iterator

Numeric = float | complex
PolicyFn = Callable[[Numeric, bool], Numeric]


class GradientPolicy(enum.Enum):
    """Enumeration of gradient handling strategies."""

    CLAMP = "clamp"
    PROJECT = "project"
    REJECT = "reject"
    PASSTHROUGH = "pass"


@dataclass
class GradientPolicyConfig:
    """Configuration stub for gradient handling."""

    policy: GradientPolicy = GradientPolicy.CLAMP


# A lightweight registry for layer- and module-specific defaults. The values
# are stored as policy names to keep the registry serialisable for config
# dumps.
_DEFAULT_POLICIES: Dict[str, GradientPolicy] = {
    "scm_rational": GradientPolicy.PROJECT,
    "scm_norm": GradientPolicy.CLAMP,
    "scm_softmax": GradientPolicy.CLAMP,
    # Coverage metrics and rejection losses operate on SCM masks; defaults
    # keep gradients finite while allowing contextual overrides.
    "coverage": GradientPolicy.CLAMP,
    "rejection_loss": GradientPolicy.CLAMP,
}
POLICY_REGISTRY: Dict[str, GradientPolicy] = dict(_DEFAULT_POLICIES)


def register_policy(layer: str, policy: GradientPolicy) -> None:
    """Register a default policy for a given layer type."""

    POLICY_REGISTRY[layer] = policy


def get_policy(layer: str | None = None) -> GradientPolicy:
    """Return the currently active gradient policy.

    A layer-specific default can be provided; otherwise the active
    context-managed policy is used.
    """

    if layer and layer in POLICY_REGISTRY:
        return POLICY_REGISTRY[layer]
    return _POLICY_STACK[-1]


# ---------------------------------------------------------------------------
# Policy context manager
# ---------------------------------------------------------------------------

_POLICY_STACK: list[GradientPolicy] = [GradientPolicy.CLAMP]


@contextmanager
def gradient_policy(policy: GradientPolicy) -> Iterator[None]:
    """Temporarily override the global gradient policy.

    Examples
    --------
    >>> from zeroproof.autodiff.policies import GradientPolicy, gradient_policy
    >>> with gradient_policy(GradientPolicy.REJECT):
    ...     ...  # computation using reject policy
    """

    _POLICY_STACK.append(policy)
    try:
        yield
    finally:
        _POLICY_STACK.pop()


# ---------------------------------------------------------------------------
# Policy application utilities
# ---------------------------------------------------------------------------


def _clamp(value: Numeric, lo: float = -1.0, hi: float = 1.0) -> Numeric:
    if isinstance(value, complex):
        return value
    return max(lo, min(hi, value))


def apply_policy(
    gradient: Numeric, is_bottom: bool, policy: GradientPolicy | None = None
) -> Numeric:
    """Transform a gradient according to the active policy.

    Parameters
    ----------
    gradient:
        Incoming gradient from the downstream node.
    is_bottom:
        Whether the current node carried the absorptive ``⊥`` value.
    policy:
        Explicit policy override; falls back to the active context if
        omitted.
    """

    policy = policy or get_policy()

    if policy is GradientPolicy.REJECT:
        return 0.0

    if policy is GradientPolicy.PROJECT:
        # Projective mode masks singular paths; finite paths are untouched.
        return 0.0 if is_bottom else gradient

    if policy is GradientPolicy.CLAMP:
        if is_bottom:
            return 0.0
        return _clamp(gradient)

    # PASSTHROUGH keeps gradients intact, even through ⊥.
    return gradient


def apply_policy_vector(
    gradients: Iterable[Numeric], is_bottom: bool, policy: GradientPolicy | None = None
) -> list[Numeric]:
    """Vectorised helper for applying a policy to a collection of gradients."""

    return [apply_policy(g, is_bottom=is_bottom, policy=policy) for g in gradients]
