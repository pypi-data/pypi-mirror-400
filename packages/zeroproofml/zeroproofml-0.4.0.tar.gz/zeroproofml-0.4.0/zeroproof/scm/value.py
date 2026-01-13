# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Core value object for Signed Common Meadows.

Implements the Phase 1 semantics for the absorptive bottom element and
basic arithmetic propagation rules. Arithmetic helpers in
:mod:`zeroproof.scm.ops` will delegate to this lightweight container.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union, cast

Numeric = Union[float, complex]
Payload = Union[Numeric, None]


def _coerce(value: "SCMValue | Numeric") -> "SCMValue":
    """Convert numeric inputs into ``SCMValue`` instances.

    The public API prefers explicit ``SCMValue`` construction, but
    allowing numeric operands simplifies ergonomic usage and tests.
    """

    if isinstance(value, SCMValue):
        return value
    if isinstance(value, bool):
        # Explicitly reject booleans to avoid ambiguity with integers.
        raise TypeError("Boolean values are not valid SCM operands")
    if isinstance(value, (int, float)):
        return SCMValue(float(value))
    if isinstance(value, complex):
        return SCMValue(complex(value))
    raise TypeError(f"Unsupported operand type: {type(value)!r}")


@dataclass(frozen=True)
class SCMValue:
    """Lightweight representation of a meadow element.

    Attributes
    ----------
    value:
        Numeric payload for regular elements. ``0.0`` is stored for the
        absorptive bottom to keep the type concrete.
    is_bottom:
        Explicit flag for ``⊥``. This flag is the single source of truth
        for invalid divisions.
    """

    value: Payload
    is_bottom: bool = False

    def __post_init__(self) -> None:
        if self.is_bottom:
            object.__setattr__(self, "value", None)
        elif self.value is None:
            raise ValueError("Non-bottom SCMValue must carry a numeric payload")

    @property
    def payload(self) -> Numeric:
        """Return the numeric payload for non-bottom values.

        `SCMValue.value` is typed as optional because bottom stores `None`.
        This helper narrows types for callers and raises if accessed on ⊥.
        """

        if self.is_bottom:
            raise ValueError("Bottom (⊥) has no numeric payload")
        return cast(Numeric, self.value)

    # ------------------------------------------------------------------
    # Representations
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover - trivial formatting
        if self.is_bottom:
            return "SCMValue(⊥)"
        return f"SCMValue({self.value!r})"

    # ------------------------------------------------------------------
    # Arithmetic operations
    # ------------------------------------------------------------------
    def _binary_op(
        self, other: SCMValue | Numeric, op: Callable[[Numeric, Numeric], Numeric]
    ) -> "SCMValue":
        rhs = _coerce(other)
        if self.is_bottom or rhs.is_bottom:
            return scm_bottom()
        return SCMValue(op(self.payload, rhs.payload))

    def __add__(self, other: SCMValue | Numeric) -> "SCMValue":
        return self._binary_op(other, lambda a, b: a + b)

    def __radd__(self, other: SCMValue | Numeric) -> "SCMValue":
        return self.__add__(other)

    def __sub__(self, other: SCMValue | Numeric) -> "SCMValue":
        return self._binary_op(other, lambda a, b: a - b)

    def __rsub__(self, other: SCMValue | Numeric) -> "SCMValue":
        rhs = _coerce(other)
        return rhs.__sub__(self)

    def __mul__(self, other: SCMValue | Numeric) -> "SCMValue":
        return self._binary_op(other, lambda a, b: a * b)

    def __rmul__(self, other: SCMValue | Numeric) -> "SCMValue":
        return self.__mul__(other)

    def __truediv__(self, other: SCMValue | Numeric) -> "SCMValue":
        rhs = _coerce(other)
        if self.is_bottom or rhs.is_bottom:
            return scm_bottom()
        if rhs.payload == 0:
            return scm_bottom()
        return SCMValue(self.payload / rhs.payload)

    def __rtruediv__(self, other: SCMValue | Numeric) -> "SCMValue":
        rhs = _coerce(other)
        return rhs.__truediv__(self)

    def __neg__(self) -> "SCMValue":
        if self.is_bottom:
            return scm_bottom()
        return SCMValue(-self.payload)


# ----------------------------------------------------------------------
# Factories
# ----------------------------------------------------------------------


def scm_real(x: float) -> SCMValue:
    """Create an ``SCMValue`` from a real number."""

    return SCMValue(float(x))


def scm_complex(z: complex) -> SCMValue:
    """Create an ``SCMValue`` from a complex number."""

    return SCMValue(complex(z))


def scm_bottom() -> SCMValue:
    """Return the absorptive bottom element ``⊥``."""

    return SCMValue(value=None, is_bottom=True)
