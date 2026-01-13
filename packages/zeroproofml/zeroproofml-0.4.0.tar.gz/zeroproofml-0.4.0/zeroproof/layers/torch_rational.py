"""
PyTorch TR-Rational layer.

Implements y(x) = P(x) / Q(x) with:
  - P(x) = sum_{k=0..d_p} theta_k x^k
  - Q(x) = 1 + sum_{k=1..d_q} phi_k x^k

Evaluation uses TRTensor operations (add/mul/div) so forward tags follow
transreal rules, and gradients follow Mask‑REAL/HYBRID/SAT policies defined
in the Torch bridge autograd functions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

try:  # Optional dependency
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    torch = None  # type: ignore
    nn = object  # type: ignore
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    from ..bridge.torch_bridge import (
        TAG_CODES,
        TRTensor,
        from_torch,
        to_torch,
        tr_add_tensor,
        tr_div_tensor,
        tr_mul_tensor,
    )


def _real_scalar_trtensor(val: "torch.Tensor", like: "torch.Tensor") -> "TRTensor":
    """Create a TRTensor filled with a scalar REAL value, broadcast to like.shape.

    Maintains autograd connectivity to val (scalar nn.Parameter).
    """
    assert TORCH_AVAILABLE
    if val.dim() != 0:
        val = val.view(())
    vals = val.to(device=like.device, dtype=like.dtype).expand_as(like)
    tags = torch.full_like(like, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
    return TRTensor(vals, tags, requires_grad=True)


def _constant_trtensor(c: float, like: "torch.Tensor") -> "TRTensor":
    """Create a constant REAL TRTensor with value c, broadcast to like.shape."""
    assert TORCH_AVAILABLE
    vals = torch.full_like(like, fill_value=float(c))
    tags = torch.full_like(like, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
    return TRTensor(vals, tags, requires_grad=False)


if TORCH_AVAILABLE:

    class TorchTRRational(nn.Module):
        """
        Torch nn.Module for transreal rational function y = P(x)/Q(x).

        Args:
            d_p: Degree of numerator polynomial P (>= 0)
            d_q: Degree of denominator polynomial Q (>= 1)
            dtype: Torch dtype for parameters (default: float64)
        """

        def __init__(self, d_p: int, d_q: int, dtype: Optional["torch.dtype"] = None):
            super().__init__()
            if d_p < 0:
                raise ValueError("d_p must be >= 0")
            if d_q < 1:
                raise ValueError("d_q must be >= 1")
            self.d_p = int(d_p)
            self.d_q = int(d_q)
            self.dtype = dtype or torch.float64

            # Parameters: theta_0..theta_d_p ; phi_1..phi_d_q
            theta = torch.zeros(self.d_p + 1, dtype=self.dtype)
            # Small initialization for phi to start near Q ≈ 1
            # Spread slightly by degree index for diversity
            phi = torch.zeros(self.d_q, dtype=self.dtype)
            if self.d_q > 0:
                scale = 0.01 / (self.d_q**0.5)
                for i in range(self.d_q):
                    phi[i] = scale * (1.0 if (i % 2 == 0) else -1.0)

            self.theta = nn.Parameter(theta)
            self.phi = nn.Parameter(phi)

            # Diagnostics
            self._last_q_min: Optional[float] = None

        def _horner_P(self, X: "TRTensor") -> "TRTensor":
            """Evaluate P(x) via Horner's method using TR ops."""
            # P = theta_d
            P = _real_scalar_trtensor(self.theta[-1], X.values)
            for k in range(self.d_p - 1, -1, -1):
                P = tr_mul_tensor(X, P)
                P = tr_add_tensor(P, _real_scalar_trtensor(self.theta[k], X.values))
            return P

        def _horner_Q(self, X: "TRTensor") -> "TRTensor":
            """Evaluate Q(x) = 1 + Σ_{k=1..d_q} phi_k x^k via Horner + TR ops."""
            # Q_tail = phi_d
            Q = _real_scalar_trtensor(self.phi[-1], X.values)
            # Accumulate down to phi_1
            for idx in range(self.d_q - 2, -1, -1):  # idx = d_q-2 .. 0 maps to phi_{idx+1}
                Q = tr_mul_tensor(X, Q)
                Q = tr_add_tensor(Q, _real_scalar_trtensor(self.phi[idx], X.values))
            # Final add constant 1: Q = 1 + x * Q when d_q>=1
            Q = tr_mul_tensor(X, Q)
            Q = tr_add_tensor(Q, _constant_trtensor(1.0, X.values))
            return Q

        def forward(self, x: "torch.Tensor") -> "TRTensor":  # type: ignore[override]
            """Compute TRTensor output, keeping tag information available."""
            X = from_torch(x, requires_grad=x.requires_grad)
            P = self._horner_P(X)
            Q = self._horner_Q(X)
            Y = tr_div_tensor(P, Q)
            # Track q_min (REAL Q only) for diagnostics
            try:
                q_vals = torch.abs(to_torch(Q))
                # nan_to_num to handle NaN from PHI and inf from infinities
                q_vals = torch.nan_to_num(q_vals, nan=float("inf"))
                self._last_q_min = float(torch.min(q_vals).item()) if q_vals.numel() > 0 else None
            except Exception:
                self._last_q_min = None
            return Y

        def forward_values(self, x: "torch.Tensor") -> "torch.Tensor":
            """Convenience: return only IEEE values of y(x) for standard losses."""
            return to_torch(self.forward(x))

        def regularization_loss(self, alpha_phi: float = 1e-3) -> "torch.Tensor":
            """L2 regularization on phi: (alpha/2) * ||phi||^2."""
            return 0.5 * float(alpha_phi) * torch.sum(self.phi * self.phi)

        def get_q_min(self) -> Optional[float]:
            return self._last_q_min

        def estimate_local_scales(self, basis_bound: Optional[float] = None) -> Tuple[float, float]:
            """
            Estimate local scales (1 + B·||φ||₁, 1 + B·||θ||₁) used by TR policy.
            """
            B = float(basis_bound) if basis_bound is not None else 1.0
            phi_l1 = float(torch.sum(torch.abs(self.phi)).item())
            theta_l1 = float(torch.sum(torch.abs(self.theta)).item())
            return (1.0 + B * phi_l1, 1.0 + B * theta_l1)

    class TorchTRRationalMulti(nn.Module):
        """
        Multi-head Torch TR-Rational with shared Q.

        y_h(x) = P_h(x) / Q(x) for h=1..H
        - Shared Q coefficients φ (degree d_q)
        - Separate numerator coefficients θ_h (degree d_p) per head
        Returns TRTensor with last dimension = H (heads).
        """

        def __init__(self, d_p: int, d_q: int, n_heads: int, dtype: Optional["torch.dtype"] = None):
            super().__init__()
            if d_p < 0:
                raise ValueError("d_p must be >= 0")
            if d_q < 1:
                raise ValueError("d_q must be >= 1")
            if n_heads < 1:
                raise ValueError("n_heads must be >= 1")
            self.d_p = int(d_p)
            self.d_q = int(d_q)
            self.n_heads = int(n_heads)
            self.dtype = dtype or torch.float64

            theta = torch.zeros(self.n_heads, self.d_p + 1, dtype=self.dtype)
            phi = torch.zeros(self.d_q, dtype=self.dtype)
            if self.d_q > 0:
                scale = 0.01 / (self.d_q**0.5)
                for i in range(self.d_q):
                    phi[i] = scale * (1.0 if (i % 2 == 0) else -1.0)
            self.theta = nn.Parameter(theta)
            self.phi = nn.Parameter(phi)

            self._last_q_min: Optional[float] = None

        @staticmethod
        def _expand_last_dim(T: "TRTensor", size: int) -> "TRTensor":
            """Expand a TRTensor by adding a last dimension of given size."""
            v = T.values.unsqueeze(-1).expand(*T.values.shape, size)
            t = T.tags.unsqueeze(-1).expand(*T.tags.shape, size)
            return TRTensor(v, t, requires_grad=T.values.requires_grad)

        @staticmethod
        def _vec_param_as_trtensor(vec: "torch.Tensor", like: "torch.Tensor") -> "TRTensor":
            """Broadcast a parameter vector over spatial dims as last dimension."""
            if vec.dim() != 1:
                vec = vec.view(-1)
            # Reshape to [..., H] with broadcasting over like.shape
            shape = (*([1] * like.dim()), vec.shape[0])
            vals = (
                vec.view(shape)
                .to(device=like.device, dtype=like.dtype)
                .expand(*like.shape, vec.shape[0])
            )
            tags = torch.full_like(vals, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            return TRTensor(vals, tags, requires_grad=True)

        def _horner_P_multi(self, XH: "TRTensor") -> "TRTensor":
            """Evaluate all heads' P via Horner with last dim as head index."""
            # Start with theta[:, -1]
            P = self._vec_param_as_trtensor(self.theta[:, -1], XH.values)
            for k in range(self.d_p - 1, -1, -1):
                P = tr_mul_tensor(XH, P)
                P = tr_add_tensor(P, self._vec_param_as_trtensor(self.theta[:, k], XH.values))
            return P

        def _horner_Q(self, X: "TRTensor") -> "TRTensor":
            Q = _real_scalar_trtensor(self.phi[-1], X.values)
            for idx in range(self.d_q - 2, -1, -1):
                Q = tr_mul_tensor(X, Q)
                Q = tr_add_tensor(Q, _real_scalar_trtensor(self.phi[idx], X.values))
            Q = tr_mul_tensor(X, Q)
            Q = tr_add_tensor(Q, _constant_trtensor(1.0, X.values))
            return Q

        def forward(self, x: "torch.Tensor") -> "TRTensor":  # type: ignore[override]
            X = from_torch(x, requires_grad=x.requires_grad)
            # Expand X to last dim = n_heads
            XH = self._expand_last_dim(X, self.n_heads)
            P = self._horner_P_multi(XH)
            Q = self._horner_Q(X)
            QH = self._expand_last_dim(Q, self.n_heads)
            Y = tr_div_tensor(P, QH)
            try:
                q_vals = torch.abs(to_torch(Q))
                q_vals = torch.nan_to_num(q_vals, nan=float("inf"))
                self._last_q_min = float(torch.min(q_vals).item()) if q_vals.numel() > 0 else None
            except Exception:
                self._last_q_min = None
            return Y

        def forward_values(self, x: "torch.Tensor") -> "torch.Tensor":
            return to_torch(self.forward(x))

        def regularization_loss(self, alpha_phi: float = 1e-3) -> "torch.Tensor":
            return 0.5 * float(alpha_phi) * torch.sum(self.phi * self.phi)

        def get_q_min(self) -> Optional[float]:
            return self._last_q_min

        def estimate_local_scales(self, basis_bound: Optional[float] = None) -> Tuple[float, float]:
            B = float(basis_bound) if basis_bound is not None else 1.0
            phi_l1 = float(torch.sum(torch.abs(self.phi)).item())
            theta_l1 = float(torch.sum(torch.abs(self.theta)).item())
            return (1.0 + B * phi_l1, 1.0 + B * theta_l1)
