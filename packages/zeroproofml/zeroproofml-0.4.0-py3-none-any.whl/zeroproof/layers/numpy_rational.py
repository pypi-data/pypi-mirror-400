"""
NumPy TR-Rational (vectorized, reference backend).

Provides a CPU-only, vectorized rational evaluator using NumPy and TRArray
ops. Useful for reference runs and metric parity checks.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore
    NUMPY_AVAILABLE = False

from ..bridge.numpy_bridge import (
    TRArray,
    from_numpy,
    to_numpy_array,
    tr_add_np,
    tr_div_np,
    tr_mul_np,
)
from ..core import TRTag


def _monomial_basis(x: "np.ndarray", max_deg: int) -> "np.ndarray":
    """Compute monomial basis [1, x, x^2, ..., x^max_deg] for all x."""
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for _monomial_basis")
    x = np.asarray(x, dtype=float)
    psi = np.ones((x.shape[0], max_deg + 1), dtype=float)
    if max_deg >= 1:
        for k in range(1, max_deg + 1):
            psi[:, k] = psi[:, k - 1] * x
    return psi


class NPRational:
    """Vectorized rational function y = P(x)/Q(x) with monomial basis.

    P(x) = sum_{k=0..d_p} theta_k x^k
    Q(x) = 1 + sum_{k=1..d_q} phi_k x^k
    """

    def __init__(self, d_p: int, d_q: int):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for NPRational")
        if d_p < 0 or d_q < 1:
            raise ValueError("Degrees must satisfy d_p>=0 and d_q>=1")
        self.d_p = int(d_p)
        self.d_q = int(d_q)
        # Initialize small phi to start near Q≈1
        self.theta = np.zeros(self.d_p + 1, dtype=float)
        self.phi = np.zeros(self.d_q, dtype=float)
        if self.d_q > 0:
            scale = 0.01 / np.sqrt(self.d_q)
            for i in range(self.d_q):
                self.phi[i] = scale * (1.0 if (i % 2 == 0) else -1.0)

    def forward(self, x: "np.ndarray") -> TRArray:
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for NPRational.forward")
        x = np.asarray(x, dtype=float).reshape(-1)
        psi = _monomial_basis(x, max(self.d_p, self.d_q))
        # P
        P = np.dot(psi[:, : self.d_p + 1], self.theta)
        # Q = 1 + Σ phi_k x^k (k>=1)
        Q = 1.0 + np.dot(psi[:, 1 : self.d_q + 1], self.phi)
        # Use NumPy IEEE division; map to TR via from_numpy
        y = P / Q
        return from_numpy(y, return_array=True)  # type: ignore[return-value]

    def forward_values(self, x: "np.ndarray") -> "np.ndarray":
        return to_numpy_array(self.forward(x))

    def get_q_values(self, x: "np.ndarray") -> List[float]:
        x = np.asarray(x, dtype=float).reshape(-1)
        psi = _monomial_basis(x, max(self.d_p, self.d_q))
        Q = 1.0 + np.dot(psi[:, 1 : self.d_q + 1], self.phi)
        return [float(abs(q)) for q in Q]

    def estimate_local_scales(self, basis_bound: Optional[float] = None) -> Tuple[float, float]:
        B = float(basis_bound) if basis_bound is not None else 1.0
        phi_l1 = float(np.sum(np.abs(self.phi)))
        theta_l1 = float(np.sum(np.abs(self.theta)))
        return (1.0 + B * phi_l1, 1.0 + B * theta_l1)
