"""Basic SCM usage examples.

This example walks through Signed Common Meadow (SCM) semantics:
- absorptive bottom element ``⊥``
- weak sign projection with hysteresis
- projective tuples produced by ``SCMRationalLayer``
- IEEE bridge utilities that collapse NaN/Inf to ``⊥``
"""
from __future__ import annotations

import os
import sys
from typing import Iterable

import torch

# Ensure local repo imports work when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zeroproof.scm.ops import scm_add, scm_div, scm_log, scm_mul, scm_pow, scm_sqrt
from zeroproof.scm.sign import WeakSignState, weak_sign
from zeroproof.scm.value import SCMValue, scm_bottom, scm_real
from zeroproof.layers import SCMRationalLayer
from zeroproof.utils import batch_from_ieee, batch_to_ieee, from_ieee, to_ieee


def _format(values: Iterable[SCMValue]) -> str:
    return ", ".join(repr(v) for v in values)


def demonstrate_scm_arithmetic() -> None:
    """Show absorptive arithmetic with the single bottom element."""

    print("=== Basic SCM Arithmetic ===\n")
    x = scm_real(3.0)
    y = scm_real(0.0)
    z = scm_real(-2.0)

    print(f"3 / 0 -> {scm_div(x, y)} (division collapses to ⊥)")
    print(f"-2 / 0 -> {scm_div(z, y)} (sign does not create ±∞)")
    print(f"0 / 0 -> {scm_div(y, y)} (indeterminate forms also map to ⊥)")

    bottom = scm_bottom()
    print(f"⊥ is absorptive: 5 * ⊥ = {scm_mul(scm_real(5.0), bottom)}")
    print(f"⊥ + (-2) = {scm_add(bottom, z)}")

    print("\nDomain-aware transcendentals")
    print(f"log(1)   = {scm_log(scm_real(1.0))}")
    print(f"log(-1)  = {scm_log(z)} (invalid → ⊥)")
    print(f"sqrt(4)  = {scm_sqrt(scm_real(4.0))}")
    print(f"sqrt(-1) = {scm_sqrt(z)} (real-domain violation → ⊥)")
    print(f"0 ** -1  = {scm_pow(y, -1)} (singular exponent → ⊥)")


def demonstrate_weak_sign() -> None:
    """Illustrate weak sign hysteresis near the singular band."""

    print("\n=== Weak Sign Projection ===\n")
    state = WeakSignState(epsilon=1e-3, hysteresis=0.5)
    samples = [scm_real(1.0), scm_real(1e-4), scm_real(0.0), scm_real(-1e-4), scm_real(-1.0)]

    print("Inputs:", _format(samples))
    print("Weak signs with history lock:")
    for v in samples:
        sign = weak_sign(v, state)
        print(f"  sign({v}) = {sign}")


def demonstrate_projective_tuple() -> None:
    """Show projective tuple output from ``SCMRationalLayer``."""

    print("\n=== Projective Tuple Rational ===\n")
    x = torch.tensor([-2.0, -0.25, 0.0, 0.25, 2.0])
    layer = SCMRationalLayer(1, 1)
    with torch.no_grad():
        layer.numerator[:] = torch.tensor([0.5, 1.0])
        layer.denominator[:] = torch.tensor([1.0, 0.25])

    y, bottom_mask = layer(x)
    print("inputs       :", x.tolist())
    print("numerator    :", layer.numerator.tolist())
    print("denominator  :", layer.denominator.tolist())
    print("projective y :", torch.nan_to_num(y, nan=float("nan")).tolist())
    print("⊥ mask       :", bottom_mask.tolist())
    print("decode(y)    :", torch.where(bottom_mask, torch.nan, y).tolist())


def demonstrate_ieee_bridge() -> None:
    """Map IEEE-754 special values to SCM and back."""

    print("\n=== IEEE ↔ SCM Bridge ===\n")
    specials = [float("nan"), float("inf"), float("-inf"), 0.0, -2.5]

    bridged = batch_from_ieee(specials)
    print("from_ieee →", _format(bridged))
    print("round-trip →", batch_to_ieee(bridged))

    single = from_ieee(float("nan"))
    print(f"Explicit ⊥ from NaN: {single}")
    print(f"Back to IEEE: {to_ieee(single)}")


if __name__ == "__main__":
    print("ZeroProof: SCM Basics Demo")
    print("=====================================\n")

    demonstrate_scm_arithmetic()
    demonstrate_weak_sign()
    demonstrate_projective_tuple()
    demonstrate_ieee_bridge()

    print("\n=====================================")
    print("SCM makes singularities first-class: one ⊥, weak signs, projective tuples.")
