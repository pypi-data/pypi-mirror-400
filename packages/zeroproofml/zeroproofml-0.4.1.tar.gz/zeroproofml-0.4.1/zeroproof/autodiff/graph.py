# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Minimal autodiff graph for documentation and testing (Phase 9).

This module mirrors the behaviour of the production computation graph in a
pure-Python form so that the documentation examples in Phase 9 remain
faithful to the signed common meadow semantics. The focus is on clarity and
policy-aware gradient flow rather than performance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Sequence

from zeroproof.autodiff.policies import GradientPolicy, apply_policy
from zeroproof.scm.value import SCMValue

Numeric = float | complex


def _to_node(value: SCMValue | float | int | "SCMNode") -> "SCMNode":
    """Promote raw values to :class:`SCMNode` instances.

    The lightweight graph API accepts Python scalars for ergonomic test
    construction; they are wrapped as constant nodes carrying
    :class:`~zeroproof.scm.value.SCMValue` payloads so that downstream
    arithmetic continues to respect absorptive ``⊥`` semantics.
    """
    if isinstance(value, SCMNode):
        return value
    if isinstance(value, SCMValue):
        return SCMNode.constant(value)
    return SCMNode.constant(SCMValue(float(value)))


BackwardFn = Callable[[Numeric], Sequence[Numeric]]


@dataclass
class SCMNode:
    """Computation graph node with basic autodiff support.

    Each node stores its forward :class:`~zeroproof.scm.value.SCMValue`
    and a small amount of metadata required for reverse-mode AD. The
    ``is_bottom`` flag is duplicated from the payload to make gradient
    policy checks cheap during the backward sweep.
    """

    value: SCMValue
    parents: List["SCMNode"] = field(default_factory=list)
    backward_fn: BackwardFn | None = None
    op_name: str = "const"
    is_stop: bool = False

    grad: Numeric = 0.0
    is_bottom: bool = False

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @classmethod
    def constant(cls, value: SCMValue) -> "SCMNode":
        """Instantiate a leaf node carrying a fixed :class:`SCMValue`.

        The resulting node has no parents and is treated as a source during
        the backward sweep.
        """
        return cls(value=value, is_bottom=value.is_bottom)

    @classmethod
    def stop_gradient(cls, node: "SCMNode") -> "SCMNode":
        """Create a detached copy that halts gradient propagation."""
        return cls(
            value=node.value,
            parents=[node],
            backward_fn=None,
            op_name="sg",
            is_stop=True,
            is_bottom=node.value.is_bottom,
        )

    # ------------------------------------------------------------------
    # Primitive operations
    # ------------------------------------------------------------------
    def _binary(
        self,
        other: SCMValue | float | int | "SCMNode",
        op: Callable[[SCMValue, SCMValue], SCMValue],
        derivs: Callable[[SCMValue, SCMValue], tuple[Numeric, Numeric]],
        op_name: str,
    ) -> "SCMNode":
        rhs = _to_node(other)
        lhs_val, rhs_val = self.value, rhs.value
        out_value = op(lhs_val, rhs_val)

        def backward(upstream: Numeric) -> tuple[Numeric, Numeric]:
            dl, dr = derivs(lhs_val, rhs_val)
            return upstream * dl, upstream * dr

        return SCMNode(
            value=out_value,
            parents=[self, rhs],
            backward_fn=backward,
            op_name=op_name,
            is_bottom=out_value.is_bottom,
        )

    def add(self, other: SCMValue | float | int | "SCMNode") -> "SCMNode":
        """Elementwise addition that propagates the absorptive bottom."""
        return self._binary(other, lambda a, b: a + b, lambda _a, _b: (1.0, 1.0), "add")

    def sub(self, other: SCMValue | float | int | "SCMNode") -> "SCMNode":
        """Elementwise subtraction with standard SCM semantics."""
        return self._binary(other, lambda a, b: a - b, lambda _a, _b: (1.0, -1.0), "sub")

    def mul(self, other: SCMValue | float | int | "SCMNode") -> "SCMNode":
        """Multiplication that absorbs to ``⊥`` if either operand is bottom."""
        return self._binary(
            other,
            lambda a, b: a * b,
            lambda a, b: (
                0.0 if a.is_bottom or b.is_bottom else b.payload,
                0.0 if a.is_bottom or b.is_bottom else a.payload,
            ),
            "mul",
        )

    def div(self, other: SCMValue | float | int | "SCMNode") -> "SCMNode":
        """Total division consistent with common meadow axioms.

        Division by zero or by a bottom operand yields a bottom output;
        the derivative is masked in these regions so gradient policies
        can decide how to treat the singular path.
        """

        def forward(a: SCMValue, b: SCMValue) -> SCMValue:
            return a / b

        def derivs(a: SCMValue, b: SCMValue) -> tuple[Numeric, Numeric]:
            if a.is_bottom or b.is_bottom or b.payload == 0:
                return 0.0, 0.0
            return 1.0 / b.payload, -a.payload / (b.payload**2)

        return self._binary(other, forward, derivs, "div")

    # ------------------------------------------------------------------
    # Backward pass
    # ------------------------------------------------------------------
    def backward(self, upstream: Numeric = 1.0, *, policy: GradientPolicy | None = None) -> None:
        """Accumulate gradients using the provided policy.

        Gradients are routed through :func:`apply_policy`, allowing
        callers to select clamping, projection, rejection, or pass-through
        handling of paths that encountered ``⊥`` during the forward pass.
        """

        self.grad += apply_policy(upstream, is_bottom=self.is_bottom, policy=policy)

        if self.backward_fn is None or self.is_stop:
            return

        downstream_grads = self.backward_fn(upstream)
        for parent, g in zip(self.parents, downstream_grads):
            parent.backward(g, policy=policy)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def trace(self, depth: int = 0) -> List[str]:
        """Return a simple textual representation of the graph.

        Useful for debugging Phase 9 documentation examples without
        needing a full visualization stack.
        """

        prefix = "  " * depth
        lines = [f"{prefix}{self.op_name}: value={self.value}, grad={self.grad}"]
        for parent in self.parents:
            lines.extend(parent.trace(depth + 1))
        return lines


# Convenience aliases for functional style --------------------------------------------------


def add(lhs: SCMNode | float | int, rhs: SCMNode | float | int) -> SCMNode:
    """Functional alias for :meth:`SCMNode.add`."""
    return _to_node(lhs).add(rhs)


def sub(lhs: SCMNode | float | int, rhs: SCMNode | float | int) -> SCMNode:
    """Functional alias for :meth:`SCMNode.sub`."""
    return _to_node(lhs).sub(rhs)


def mul(lhs: SCMNode | float | int, rhs: SCMNode | float | int) -> SCMNode:
    """Functional alias for :meth:`SCMNode.mul`."""
    return _to_node(lhs).mul(rhs)


def div(lhs: SCMNode | float | int, rhs: SCMNode | float | int) -> SCMNode:
    """Functional alias for :meth:`SCMNode.div`."""
    return _to_node(lhs).div(rhs)


def stop_gradient(node: SCMNode | float | int) -> SCMNode:
    """Create a detached copy of a node for stop-gradient semantics."""
    return SCMNode.stop_gradient(_to_node(node))
