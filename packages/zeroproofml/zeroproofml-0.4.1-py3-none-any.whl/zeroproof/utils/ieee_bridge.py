# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Conversion helpers between IEEE-754 floats and SCM values."""

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

from zeroproof.scm.value import SCMValue, scm_bottom, scm_real

__all__ = ["from_ieee", "to_ieee", "batch_from_ieee", "batch_to_ieee"]


def from_ieee(x: float | int) -> SCMValue:
    """Convert an IEEE-754 scalar to :class:`~zeroproof.scm.value.SCMValue`.

    ``NaN`` and ``±inf`` collapse to the absorptive ``⊥`` element.
    ``bool`` is rejected to avoid ambiguity with integer inputs.
    """

    if isinstance(x, bool):
        raise TypeError("Boolean values are not valid SCM operands")
    value = float(x)
    if math.isnan(value) or math.isinf(value):
        return scm_bottom()
    return scm_real(value)


def to_ieee(value: SCMValue) -> float:
    """Convert an :class:`SCMValue` back to an IEEE-754 ``float``.

    The absorptive element maps to ``NaN`` to preserve downstream tooling
    expectations (e.g., coverage metrics interpreting NaN as ``⊥``).
    """

    if value.is_bottom:
        return float("nan")
    payload = value.payload
    if isinstance(payload, complex):
        if payload.imag != 0:
            return float("nan")
        return float(payload.real)
    return float(payload)


def batch_from_ieee(values: Iterable[float | int]) -> list[SCMValue]:
    """Vectorised :func:`from_ieee` over an iterable of scalars."""

    return [from_ieee(v) for v in values]


def batch_to_ieee(values: Iterable[SCMValue]) -> list[float]:
    """Vectorised :func:`to_ieee` over an iterable of SCM values."""

    return [to_ieee(v) for v in values]
