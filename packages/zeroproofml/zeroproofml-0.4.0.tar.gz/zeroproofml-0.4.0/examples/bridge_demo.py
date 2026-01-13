"""SCM bridge demonstration for NumPy, PyTorch, and IEEE scalars."""
from __future__ import annotations

import os
import sys
from typing import Iterable

import numpy as np
import torch

# Ensure local repo imports work when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zeroproof.scm.ops import scm_add_numpy, scm_div_numpy, scm_mul_torch
from zeroproof.scm.value import scm_bottom, scm_real
from zeroproof.utils import batch_from_ieee, batch_to_ieee, from_ieee, to_ieee



def _fmt(values: Iterable) -> str:
    return ", ".join(str(v) for v in values)


def demonstrate_ieee_scalars() -> None:
    """Bridge IEEE-754 scalars into SCM and back."""

    print("=== Scalar bridge ===")
    scalars = [float("nan"), float("inf"), float("-inf"), -0.0, 1.25]
    scm_values = [from_ieee(x) for x in scalars]
    round_trip = [to_ieee(v) for v in scm_values]

    print("inputs     :", _fmt(scalars))
    print("SCM values :", _fmt(scm_values))
    print("round-trip :", _fmt(round_trip))
    print()


def demonstrate_numpy_bridge() -> None:
    """Show vectorised ⊥ propagation with NumPy arrays."""

    print("=== NumPy vector bridge ===")
    arr = np.array([1.0, np.inf, -np.inf, np.nan, 0.0])
    values = batch_from_ieee(arr)

    payload = np.array([v.value for v in values])
    mask = np.array([v.is_bottom for v in values])
    summed, bottom = scm_add_numpy(payload, mask, payload * 2, mask)
    quotient, q_bottom = scm_div_numpy(payload, mask, np.ones_like(payload), mask)

    print("payload     :", payload.tolist())
    print("⊥ mask      :", mask.tolist())
    print("sum (⊥→0)   :", summed.tolist())
    print("sum mask    :", bottom.tolist())
    print("quotient    :", quotient.tolist())
    print("quot mask   :", q_bottom.tolist())
    print("back to IEEE:", batch_to_ieee(values))
    print()


def demonstrate_torch_bridge() -> None:
    """Use the torch factories to keep tensors SCM-safe."""

    print("=== Torch vector bridge ===")
    t = torch.tensor([2.0, -1.0, 0.0])
    payload, mask = t, torch.tensor([False, False, True])

    prod, prod_mask = scm_mul_torch(payload, mask, torch.tensor([-1.0, 4.0, 5.0]), mask)

    print("tensor      :", t.tolist())
    print("mask        :", mask.tolist())
    print("product     :", prod.tolist())
    print("product mask:", prod_mask.tolist())
    print()


def demonstrate_bottom_literal() -> None:
    """Show that ⊥ is explicit and composable."""

    print("=== Explicit ⊥ literal ===")
    b = scm_bottom()
    print("bottom literal :", b)
    print("bottom + 3     :", scm_real(3.0) + b)
    print()


if __name__ == "__main__":
    print("ZeroProof: SCM Bridge Demo")
    print("=====================================\n")

    demonstrate_ieee_scalars()
    demonstrate_numpy_bridge()
    demonstrate_torch_bridge()
    demonstrate_bottom_literal()

    print("=====================================")
    print("Transports collapse IEEE NaN/Inf to ⊥ and keep vector masks aligned.")
