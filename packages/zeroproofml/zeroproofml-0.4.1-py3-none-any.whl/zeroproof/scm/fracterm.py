# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Fracterm representation and basic flattening utilities.

This module encodes the ``P/Q`` representation discussed in ``concept.tex``
for small rational subgraphs. The implementation is intentionally light
weight: polynomials are stored as dictionaries of monomials to
coefficients, with minimal simplification to avoid blow-ups while still
providing degree tracking and evaluation into :class:`SCMValue` objects.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping, Tuple

from .value import SCMValue, scm_bottom

Monomial = Tuple[Tuple[str, int], ...]


def _normalize_monomial(pairs: Iterable[Tuple[str, int]]) -> Monomial:
    accumulator: Dict[str, int] = {}
    for var, exp in pairs:
        if exp == 0:
            continue
        accumulator[var] = accumulator.get(var, 0) + exp
    return tuple(sorted(accumulator.items()))


def _monomial_gcd(monomials: Iterable[Monomial]) -> Monomial:
    iterator = iter(monomials)
    try:
        first = next(iterator)
    except StopIteration:
        return ()

    gcd_map: Dict[str, int] = dict(first)
    for mono in iterator:
        mono_map = dict(mono)
        for var in list(gcd_map.keys()):
            gcd_map[var] = min(gcd_map[var], mono_map.get(var, 0))
            if gcd_map[var] == 0:
                del gcd_map[var]

    return tuple(sorted(gcd_map.items()))


def _numeric_gcd(values: Iterable[complex]) -> float | None:
    """Return a shared integer factor when coefficients permit.

    The helper is intentionally conservative: it only returns a factor when
    all coefficients are (near) integers and share a non-trivial ``gcd``. This
    keeps simplification deterministic without introducing floating-point
    round-off artefacts during factor cancellation.
    """

    integers: list[int] = []
    for coeff in values:
        if coeff == 0:
            continue
        if isinstance(coeff, complex):
            if coeff.imag != 0:
                return None
            coeff = coeff.real
        rounded = round(coeff)
        if abs(coeff - rounded) > 1e-12:
            return None
        integers.append(int(rounded))

    if not integers:
        return None

    gcd_value = abs(integers[0])
    for val in integers[1:]:
        gcd_value = math.gcd(gcd_value, abs(val))
    if gcd_value <= 1:
        return None
    return float(gcd_value)


def _coerce_numeric(value: complex | SCMValue) -> SCMValue:
    if isinstance(value, SCMValue):
        return value
    if isinstance(value, bool):
        raise TypeError("Boolean values are not valid SCM operands")
    return SCMValue(value)


@dataclass(frozen=True)
class Polynomial:
    """Sparse multivariate polynomial used for fracterm construction."""

    terms: Dict[Monomial, complex]

    @staticmethod
    def constant(value: complex) -> "Polynomial":
        if value == 0:
            return Polynomial({})
        return Polynomial({(): value})

    @staticmethod
    def variable(name: str) -> "Polynomial":
        return Polynomial({((name, 1),): 1.0})

    @property
    def degree(self) -> int:
        if not self.terms:
            return 0
        return max(sum(exp for _, exp in mono) for mono in self.terms)

    def __add__(self, other: "Polynomial") -> "Polynomial":
        new_terms: Dict[Monomial, complex] = dict(self.terms)
        for mono, coeff in other.terms.items():
            new_terms[mono] = new_terms.get(mono, 0) + coeff
            if new_terms[mono] == 0:
                del new_terms[mono]
        return Polynomial(new_terms)

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        new_terms: Dict[Monomial, complex] = {}
        for mono_a, coeff_a in self.terms.items():
            for mono_b, coeff_b in other.terms.items():
                combined = _normalize_monomial(
                    [(var, exp) for var, exp in mono_a] + [(var, exp) for var, exp in mono_b]
                )
                new_terms[combined] = new_terms.get(combined, 0) + coeff_a * coeff_b
                if new_terms[combined] == 0:
                    del new_terms[combined]
        return Polynomial(new_terms)

    def simplify(self) -> "Polynomial":
        """Remove zero coefficients and normalise an empty polynomial."""

        cleaned = {mono: coeff for mono, coeff in self.terms.items() if coeff != 0}
        return Polynomial(cleaned)

    def divide_by_monomial(self, monomial: Monomial) -> "Polynomial":
        if not monomial:
            return self

        divisor = dict(monomial)
        new_terms: Dict[Monomial, complex] = {}
        for mono, coeff in self.terms.items():
            mono_map = dict(mono)
            adjusted: Dict[str, int] = {}
            for var, exp in mono_map.items():
                reduced = exp - divisor.get(var, 0)
                if reduced < 0:
                    raise ValueError("Divisor monomial does not divide polynomial term")
                if reduced:
                    adjusted[var] = reduced
            new_terms[tuple(sorted(adjusted.items()))] = coeff
        return Polynomial(new_terms)

    def monomial_gcd(self) -> Monomial:
        return _monomial_gcd(self.terms)

    def evaluate(self, values: Mapping[str, complex | SCMValue]) -> SCMValue:
        total = SCMValue(0.0)
        if not self.terms:
            return total

        for monomial, coeff in self.terms.items():
            term = _coerce_numeric(coeff)
            for var, exp in monomial:
                if var not in values:
                    raise KeyError(f"Missing assignment for variable '{var}'")
                base = _coerce_numeric(values[var])
                if base.is_bottom:
                    term = scm_bottom()
                    break
                powered = SCMValue(1.0)
                for _ in range(exp):
                    powered = powered * base
                    if powered.is_bottom:
                        break
                term = term * powered
                if term.is_bottom:
                    break
            total = total + term
        return total


SymbolicSimplifier = Callable[[Polynomial, Polynomial], Tuple[Polynomial, Polynomial]]


def _bergstra_tucker_simplifier(
    numerator: Polynomial, denominator: Polynomial
) -> Tuple[Polynomial, Polynomial]:
    """Symbolic simplifier inspired by Bergstra–Tucker fracterm calculus.

    This variant cancels shared monomial and numeric factors even when the
    fraction only contains a single monomial term. It is deliberately
    deterministic and conservative, sticking to the safe cancellations that
    appear in the Bergstra–Tucker rewrite systems while avoiding full
    polynomial expansion.
    """

    if not numerator.terms:
        return Polynomial.constant(0.0), Polynomial.constant(1.0)

    shared_monomial = _monomial_gcd([numerator.monomial_gcd(), denominator.monomial_gcd()])
    if shared_monomial:
        numerator = numerator.divide_by_monomial(shared_monomial).simplify()
        denominator = denominator.divide_by_monomial(shared_monomial).simplify()

    coeff_gcd = _numeric_gcd(list(numerator.terms.values()) + list(denominator.terms.values()))
    if coeff_gcd:
        numerator = Polynomial({m: c / coeff_gcd for m, c in numerator.terms.items()}).simplify()
        denominator = Polynomial(
            {m: c / coeff_gcd for m, c in denominator.terms.items()}
        ).simplify()

    return numerator, denominator


_SYMBOLIC_SIMPLIFIERS: Dict[str, SymbolicSimplifier] = {
    "bergstra_tucker": _bergstra_tucker_simplifier,
}


def _resolve_symbolic_simplifier(
    symbolic: str | SymbolicSimplifier | None,
) -> SymbolicSimplifier | None:
    if symbolic is None:
        return None
    if isinstance(symbolic, str):
        if symbolic not in _SYMBOLIC_SIMPLIFIERS:
            raise KeyError(f"Unknown symbolic simplifier '{symbolic}'")
        return _SYMBOLIC_SIMPLIFIERS[symbolic]
    if callable(symbolic):
        return symbolic
    raise TypeError("symbolic simplifier must be None, a registered name, or a callable")


@dataclass
class Fracterm:
    """Fractional term ``P/Q`` with degree tracking and evaluation.

    The ``depth`` attribute tracks how many rational layers were combined to
    build the term. Flattening enforces the engineering constraint ``L ≤ 5``
    from ``concept.tex`` by default.
    """

    numerator: Polynomial
    denominator: Polynomial
    depth: int = 1
    degree_trace: Tuple[Tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if self.depth <= 0:
            raise ValueError("Fracterm depth must be positive")
        if not self.degree_trace:
            object.__setattr__(self, "degree_trace", (self.degrees,))

    @staticmethod
    def from_constant(value: complex) -> "Fracterm":
        zero = Polynomial.constant(value)
        return Fracterm(zero, Polynomial.constant(1.0))

    @staticmethod
    def from_variable(name: str) -> "Fracterm":
        return Fracterm(Polynomial.variable(name), Polynomial.constant(1.0))

    @property
    def degrees(self) -> Tuple[int, int]:
        return self.numerator.degree, self.denominator.degree

    def _merge(
        self, other: "Fracterm", numerator: Polynomial, denominator: Polynomial
    ) -> "Fracterm":
        new_depth = max(self.depth, other.depth) + 1
        trace = self.degree_trace + other.degree_trace + ((numerator.degree, denominator.degree),)
        return Fracterm(numerator, denominator, depth=new_depth, degree_trace=trace).simplify()

    def _cancel_factors(
        self,
        numerator: Polynomial,
        denominator: Polynomial,
        *,
        aggressive: bool,
        symbolic: str | SymbolicSimplifier | None = None,
    ) -> Tuple[Polynomial, Polynomial]:
        if not numerator.terms:
            zero = Polynomial.constant(0.0)
            one = Polynomial.constant(1.0)
            return zero, one

        symbolic_fn = _resolve_symbolic_simplifier(symbolic)
        if symbolic_fn:
            numerator, denominator = symbolic_fn(numerator, denominator)

        num = numerator.simplify()
        den = denominator.simplify()

        shared_monomial = _monomial_gcd([num.monomial_gcd(), den.monomial_gcd()])
        should_cancel = shared_monomial and (aggressive or len(num.terms) > 1 or len(den.terms) > 1)
        if should_cancel:
            num = num.divide_by_monomial(shared_monomial).simplify()
            den = den.divide_by_monomial(shared_monomial).simplify()

        if aggressive:
            coeff_gcd = _numeric_gcd(list(num.terms.values()) + list(den.terms.values()))
            if coeff_gcd:
                num = Polynomial({m: c / coeff_gcd for m, c in num.terms.items()}).simplify()
                den = Polynomial({m: c / coeff_gcd for m, c in den.terms.items()}).simplify()

        return num, den

    def simplify(
        self,
        aggressive: bool = False,
        *,
        symbolic: str | SymbolicSimplifier | None = None,
    ) -> "Fracterm":
        num, den = self._cancel_factors(
            self.numerator, self.denominator, aggressive=aggressive, symbolic=symbolic
        )
        if num is self.numerator and den is self.denominator:
            return self
        return Fracterm(num, den, depth=self.depth, degree_trace=self.degree_trace)

    def __add__(self, other: "Fracterm") -> "Fracterm":
        num = self.numerator * other.denominator + other.numerator * self.denominator
        den = self.denominator * other.denominator
        return self._merge(other, num, den)

    def __mul__(self, other: "Fracterm") -> "Fracterm":
        num = self.numerator * other.numerator
        den = self.denominator * other.denominator
        return self._merge(other, num, den)

    def __truediv__(self, other: "Fracterm") -> "Fracterm":
        num = self.numerator * other.denominator
        den = self.denominator * other.numerator
        return self._merge(other, num, den)

    def flatten(
        self,
        max_depth: int | None = 5,
        max_degree: int | None = None,
        aggressive: bool = False,
        symbolic: str | SymbolicSimplifier | None = None,
    ) -> Tuple[Polynomial, Polynomial]:
        if max_depth is not None and self.depth > max_depth:
            raise ValueError(
                f"Fracterm depth {self.depth} exceeds limit L ≤ {max_depth}. "
                "Consider reducing fused rational layers."
            )
        numerator, denominator = self._cancel_factors(
            self.numerator,
            self.denominator,
            aggressive=aggressive,
            symbolic=symbolic,
        )
        if max_degree is not None:
            if numerator.degree > max_degree or denominator.degree > max_degree:
                raise ValueError(
                    f"Polynomial degree exceeds bound {max_degree}: "
                    f"P degree={numerator.degree}, Q degree={denominator.degree}"
                )
        return numerator, denominator

    def degree_profile(self) -> Tuple[Tuple[int, int], ...]:
        """Return the recorded degree growth across composed layers."""

        return self.degree_trace

    def evaluate(self, values: Mapping[str, complex | SCMValue]) -> SCMValue:
        num_val = self.numerator.evaluate(values)
        den_val = self.denominator.evaluate(values)
        if num_val.is_bottom or den_val.is_bottom:
            return scm_bottom()
        if den_val.payload == 0:
            return scm_bottom()
        return SCMValue(num_val.payload / den_val.payload)
