# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Projective tuple helpers for the optional projective learning mode.

The functions here mirror the conceptual mapping described in
``concept.tex``: finite SCM values are lifted to homogeneous tuples,
renormalised with a detached norm, and decoded back to SCM with the
absorptive bottom ``⊥`` exposed when the denominator vanishes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Tuple

from zeroproof.scm.value import SCMValue, scm_bottom

# This module is used with pure Python scalars and (optionally) Torch/JAX tensors.
# Keep the typing flexible so strict mypy does not require backend-specific stubs.
Numeric = Any
StopGradientFn = Callable[[Any], Any]


def _is_torch_tensor(x: Any) -> bool:
    try:  # pragma: no cover - optional dependency
        import torch

        return isinstance(x, torch.Tensor)
    except Exception:  # pragma: no cover - defensive
        return False


def _torch_stop_gradient() -> StopGradientFn:
    import torch

    def _detach(x: Any) -> Any:
        if isinstance(x, torch.Tensor):
            return x.detach()
        return torch.as_tensor(x).detach()

    return _detach


def _is_jax_array(x: Any) -> bool:
    try:  # pragma: no cover - optional dependency
        import jax

        return isinstance(x, jax.Array)
    except Exception:  # pragma: no cover - defensive
        return False


def _jax_stop_gradient() -> StopGradientFn:
    import jax

    def _stop(x: Any) -> Any:
        return jax.lax.stop_gradient(x)

    return _stop


@dataclass
class ProjectiveSample:
    """Represents an (N, D) tuple in projective space."""

    numerator: Any
    denominator: Any


def encode(value: SCMValue) -> ProjectiveSample:
    """Encode an ``SCMValue`` into a projective tuple."""

    if value.is_bottom:
        return ProjectiveSample(1.0, 0.0)
    return ProjectiveSample(value.payload, 1.0)


def decode(sample: ProjectiveSample) -> SCMValue:
    """Decode a projective tuple back into an ``SCMValue``."""

    if sample.denominator == 0:
        return scm_bottom()
    return SCMValue(sample.numerator / sample.denominator)


def renormalize(
    numerator: Any,
    denominator: Any,
    gamma: float = 1e-9,
    stop_gradient: StopGradientFn | None = None,
) -> Tuple[Any, Any]:
    """Detached renormalization used in projective training.

    Parameters
    ----------
    numerator, denominator:
        Raw tuple components.
    gamma:
        Numerical stability constant added to the norm.
    stop_gradient:
        Optional callable used to mimic framework-specific stop-gradient
        semantics. Defaults to identity.
    """

    if stop_gradient is None:
        if _is_torch_tensor(numerator) or _is_torch_tensor(denominator):
            stop_gradient = _torch_stop_gradient()
        elif _is_jax_array(numerator) or _is_jax_array(denominator):
            stop_gradient = _jax_stop_gradient()
        else:

            def stop_gradient(x: Any) -> Any:
                return x

    scale = (numerator**2 + denominator**2) ** 0.5
    scale = stop_gradient(scale) + gamma
    return numerator / scale, denominator / scale


def projectively_equal(a: ProjectiveSample, b: ProjectiveSample, *, atol: float = 1e-8) -> bool:
    """Check projective equality up to scaling."""

    return bool(abs(a.numerator * b.denominator - b.numerator * a.denominator) <= atol)
