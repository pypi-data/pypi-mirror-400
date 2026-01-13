"""SCM-oriented optimization and monitoring patterns.

The original transreal profiling utilities have been removed in favour of
SCM-first primitives. This demo highlights the new building blocks:
- vectorised ⊥ propagation with NumPy and PyTorch
- gradient policies that gate learning near singularities
- projective tuple heads that surface ⊥ masks for coverage metrics
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch

# Ensure local repo imports work when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zeroproof.autodiff.policies import GradientPolicy
from zeroproof.layers import SCMRationalLayer
from zeroproof.scm.ops import scm_add_numpy, scm_div_torch
from zeroproof.scm.value import scm_bottom, scm_real



def demonstrate_vectorized_bottoms() -> None:
    """Run a small NumPy pipeline to show ⊥ masks flowing with data."""

    print("=== Vectorised ⊥ propagation ===")
    payload = np.array([1.0, 0.0, -2.0])
    mask = np.array([False, True, False])

    summed, sum_mask = scm_add_numpy(payload, mask, np.array([0.5, 0.5, 0.5]), mask)
    print("payload :", payload.tolist())
    print("mask    :", mask.tolist())
    print("sum     :", summed.tolist())
    print("sum mask:", sum_mask.tolist())
    print()


def demonstrate_gradient_policy() -> None:
    """Illustrate PROJECT vs PASSTHROUGH on torch tensors."""

    print("=== Gradient policy ===")
    x = torch.tensor([1.0, 0.0], requires_grad=True)
    denom_mask = torch.tensor([False, True])

    y, bottom = scm_div_torch(x, None, torch.tensor([1.0, 0.0]), denom_mask)
    loss = y.sum()

    # Backward twice with different policies
    loss.backward(retain_graph=True)
    passthrough_grad = x.grad.detach().clone()

    x.grad.zero_()
    loss.backward()
    projected_grad = torch.where(bottom, torch.zeros_like(x.grad), x.grad)

    print("values   :", y.tolist())
    print("⊥ mask    :", bottom.tolist())
    print("grad pass :", passthrough_grad.tolist())
    print("grad proj :", projected_grad.tolist())
    print()


def demonstrate_projective_head() -> None:
    """Use SCMRationalLayer to expose ⊥ coverage during training."""

    print("=== Projective tuple rational head ===")
    layer = SCMRationalLayer(1, 1, gradient_policy=GradientPolicy.PROJECT)
    with torch.no_grad():
        layer.numerator[:] = torch.tensor([0.0, 1.0])
        layer.denominator[:] = torch.tensor([1.0, 0.1])

    x = torch.linspace(-1.0, 1.0, steps=5)
    y, bottom = layer(x)

    decoded = torch.where(bottom, torch.full_like(y, float("nan")), y)
    coverage = float(bottom.float().mean())

    print("inputs     :", x.tolist())
    print("outputs    :", decoded.tolist())
    print("⊥ mask     :", bottom.tolist())
    print("coverage   :", f"{coverage:.2f}")
    print("bottom lit.:", scm_bottom())
    print("safe real  :", scm_real(2.0))
    print()


if __name__ == "__main__":
    print("ZeroProof: SCM Optimization Demo")
    print("=====================================\n")

    demonstrate_vectorized_bottoms()
    demonstrate_gradient_policy()
    demonstrate_projective_head()

    print("=====================================")
    print("Optimizations now centre on SCM masks, gradient policies, and projective tuples.")
