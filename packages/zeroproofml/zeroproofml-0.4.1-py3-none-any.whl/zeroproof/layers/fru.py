# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Fused Rational Unit (FRU) utilities.

The FRU is the small symbolic island in the otherwise numerical
projective computation graph. It receives an already flattened tuple
``(P, Q)`` and optionally applies additional rational layers, while
tracking polynomial degree growth. The symbolic flattening algorithm
itself is intentionally lightweight here—the heavy algebraic machinery
belongs to :mod:`zeroproof.scm.fracterm`—but the FRU enforces the
engineering constraints from ``concept.tex``:

* Depth is capped at :pyattr:`max_depth` (default 5).
* Polynomial degrees follow the doubling table per layer.
* Callers can introspect the projected numerator/denominator degrees to
  decide whether an FRU configuration is safe to JIT/fuse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Tuple


def _degree_bounds(depth: int, d_p: int, d_q: int) -> Tuple[int, int]:
    """Return the theoretical max degrees after ``depth`` layers.

    The bounds follow the table in ``concept.tex`` where each additional
    layer doubles the maximum degree of the previous layer. The formula
    can be written as ``2 ** (depth - 1) * max(d_p, d_q)`` for both
    numerator and denominator.
    """

    base = max(d_p, d_q)
    factor = 2 ** (depth - 1)
    return factor * base, factor * base


@dataclass
class FractermRationalUnit:
    """Represents a bounded-depth fused rational unit.

    Parameters
    ----------
    numerator_degree, denominator_degree:
        Degrees of the incoming flattened rational function. These are
        used as the seed for the degree bounds table.
    depth:
        Number of rational layers being fused. The constructor validates
        the constraint ``depth <= max_depth``.
    max_depth:
        Maximum allowed fusion depth. Defaults to the project rule of 5.
    """

    numerator_degree: int
    denominator_degree: int
    depth: int = 1
    max_depth: int = 5
    _degree_history: list[tuple[int, int]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.depth <= 0:
            raise ValueError("FRU depth must be positive")
        if self.depth > self.max_depth:
            raise ValueError(f"FRU depth {self.depth} exceeds max_depth={self.max_depth}")
        self._recompute_bounds()

    @property
    def current_bounds(self) -> tuple[int, int]:
        """Return the final (P, Q) degree bounds for the configured depth."""

        return self._degree_history[-1]

    def _recompute_bounds(self) -> None:
        self._degree_history.clear()
        for level in range(1, self.depth + 1):
            self._degree_history.append(
                _degree_bounds(level, self.numerator_degree, self.denominator_degree)
            )

    def extend(self, extra_layers: int = 1) -> tuple[int, int]:
        """Increase the fused depth and return the new bounds.

        Raises
        ------
        ValueError
            If the requested depth would exceed :pyattr:`max_depth`.
        """

        new_depth = self.depth + extra_layers
        if new_depth > self.max_depth:
            raise ValueError(f"FRU depth {new_depth} exceeds max_depth={self.max_depth}")
        self.depth = new_depth
        self._recompute_bounds()
        return self.current_bounds

    def degree_profile(self) -> list[tuple[int, int]]:
        """Return the per-layer degree bounds up to ``depth``."""

        return list(self._degree_history)

    def flatten(
        self, numerators: Iterable[float], denominators: Iterable[float]
    ) -> tuple[list[float], list[float]]:
        """Return a naive flattened representation of the FRU polynomials.

        This helper does not attempt full symbolic algebra. Instead it
        concatenates the provided coefficients to signal that a fused
        polynomial has been produced. The output length is validated
        against the current degree bounds so callers can detect oversized
        coefficient sets early.
        """

        p_coeffs = list(numerators)
        q_coeffs = list(denominators)
        p_bound, q_bound = self.current_bounds
        if len(p_coeffs) - 1 > p_bound or len(q_coeffs) - 1 > q_bound:
            raise ValueError(
                f"Coefficient degrees exceed FRU bounds: P={len(p_coeffs) - 1} (max {p_bound}), "
                f"Q={len(q_coeffs) - 1} (max {q_bound})"
            )
        return p_coeffs, q_coeffs
