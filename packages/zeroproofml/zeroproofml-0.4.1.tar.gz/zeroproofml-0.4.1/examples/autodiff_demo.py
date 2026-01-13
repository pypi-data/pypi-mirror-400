"""Autodiff demonstration for Signed Common Meadows.

The lightweight graph in :mod:`zeroproof.autodiff.graph` mirrors the
policies described in ``concept.tex``: gradients on ⊥ paths can be
projected, clamped, or rejected while keeping regular paths untouched.
"""
from __future__ import annotations

import os
import sys

# Ensure local repo imports work when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zeroproof.autodiff.graph import SCMNode, add, div, mul, sub
from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.scm.sign import WeakSignState, weak_sign
from zeroproof.scm.value import scm_real



def demonstrate_basic_autodiff() -> None:
    """Differentiate a polynomial using the SCM graph primitives."""

    print("=== Basic SCM autodiff ===\n")
    x = SCMNode.constant(scm_real(3.0))
    y = add(mul(x, x), add(mul(2.0, x), 1.0))  # y = x^2 + 2x + 1

    y.backward(policy=GradientPolicy.PASSTHROUGH)
    print("y = x^2 + 2x + 1")
    print("x value     :", x.value)
    print("y value     :", y.value)
    print("dy/dx       :", x.grad)



def demonstrate_bottom_projection() -> None:
    """Show how ⊥ paths zero gradients under PROJECT policy."""

    print("\n=== Gradient policy on ⊥ ===\n")
    numerator = SCMNode.constant(scm_real(1.0))
    denominator = SCMNode.constant(scm_real(0.0))
    ratio = div(numerator, denominator)

    ratio.backward(policy=GradientPolicy.PROJECT)
    print("ratio       :", ratio.value)
    print("is ⊥?       :", ratio.value.is_bottom)
    print("∂ratio/∂num :", numerator.grad, "(projected)")
    print("∂ratio/∂den :", denominator.grad, "(projected)")



def demonstrate_weak_sign_gradients() -> None:
    """Combine weak sign with autodiff nodes for orientation tracking."""

    print("\n=== Weak sign during backprop ===\n")
    state = WeakSignState(epsilon=1e-3, hysteresis=0.25)

    x = SCMNode.constant(scm_real(0.0005))
    y = mul(weak_sign(x.value, state), 2.0)
    y.backward(policy=GradientPolicy.CLAMP)

    print("x in band   :", x.value)
    print("weak sign   :", weak_sign(x.value, state))
    print("gradient    :", x.grad, "(clamped after ⊥/band check)")


if __name__ == "__main__":
    print("ZeroProof: SCM Autodiff Demo")
    print("=====================================\n")

    demonstrate_basic_autodiff()
    demonstrate_bottom_projection()
    demonstrate_weak_sign_gradients()

    print("=====================================")
    print("Gradients respect the single ⊥ and weak sign hysteresis.")
