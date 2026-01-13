# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""History-aware weak sign operator for SCM values.

This module implements the weak sign protocol described in
``concept.tex``. The operator exposes a stable orientation even when the
value approaches the singular region by remembering the last valid sign
and applying a small hysteresis band to avoid oscillation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .value import SCMValue, scm_bottom

DEFAULT_EPSILON = 1e-9
DEFAULT_HYSTERESIS = 0.25


@dataclass
class WeakSignState:
    """Mutable carrier for sign history and thresholds.

    Attributes
    ----------
    last_sign:
        Last non-singular sign that was observed. Used to lock the
        orientation when the value enters the singular band.
    epsilon:
        Entry threshold ``ε`` for the singular band ``|z| < ε``.
    hysteresis:
        Relative expansion factor for the release threshold. The sign
        stays locked until ``|z|`` exceeds ``ε * (1 + hysteresis)``.
    """

    last_sign: Optional[complex] = None
    epsilon: float = DEFAULT_EPSILON
    hysteresis: float = DEFAULT_HYSTERESIS


def weak_sign(value: SCMValue, state: Optional[WeakSignState] = None) -> SCMValue:
    """Compute the weak sign of ``value`` with hysteresis.

    Behaviour follows the four-signed real / unit-circle complex
    projection with special handling for the absorptive bottom and the
    singular region:

    - ``s(⊥) = ⊥``
    - ``s(0) = 0``
    - ``s(x) = x/|x|`` otherwise

    When ``state`` is provided, the operator becomes history-aware: on
    entering the singular band ``|x| < ε`` the sign locks to the last
    observed orientation and is only released after exiting the
    hysteresis band ``|x| >= ε * (1 + hysteresis)``.
    """

    if value.is_bottom:
        return scm_bottom()

    payload = value.payload
    magnitude = abs(payload)

    # Stateless behaviour: direct projection with standard SCM cases.
    if state is None:
        if magnitude == 0:
            return SCMValue(0.0)
        return SCMValue(payload / magnitude)

    epsilon = state.epsilon
    release = epsilon * (1.0 + max(state.hysteresis, 0.0))

    if magnitude == 0 or magnitude <= epsilon:
        if state.last_sign is not None:
            return SCMValue(state.last_sign)
        return SCMValue(0.0)

    if state.last_sign is not None and magnitude < release:
        return SCMValue(state.last_sign)

    sign = payload / magnitude
    state.last_sign = sign
    return SCMValue(sign)
