"""
NumPy finite-difference gradient checks for rational functions.

Verifies REAL-path gradients for y(x) = P(x)/Q(x) against the analytic rule
  dy/dx = (P'(x)Q(x) - P(x)Q'(x)) / Q(x)^2
on samples where Q and x are finite and Q(x) != 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore
    NUMPY_AVAILABLE = False


def _polyval(coeffs: "np.ndarray", x: "np.ndarray") -> "np.ndarray":
    """Evaluate polynomial sum_{k=0..d} c_k x^k via Horner."""
    y = np.zeros_like(x, dtype=float)
    for c in coeffs[::-1]:
        y = y * x + float(c)
    return y


def _polyder(coeffs: "np.ndarray") -> "np.ndarray":
    """Derivative coefficients for coeffs[0] + coeffs[1] x + ... + coeffs[d] x^d."""
    if coeffs.size <= 1:
        return np.array([0.0])
    k = np.arange(1, coeffs.size, dtype=float)
    return coeffs[1:] * k


@dataclass
class GradCheckResult:
    max_abs_err: float
    mean_abs_err: float
    n_points: int
    n_masked: int
    eps: float


def check_rational_gradients(
    theta: "np.ndarray",
    phi: "np.ndarray",
    xs: "np.ndarray",
    eps: float = 1e-6,
) -> GradCheckResult:
    """
    Check REAL-path gradients for y = P/Q on sample points.

    Args:
      theta: coefficients [theta_0..theta_d]
      phi: denominator coefficients [phi_1..phi_dq]
      xs: sample points (1D array)
      eps: finite difference epsilon

    Returns:
      GradCheckResult with max/mean abs error on valid REAL points.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for check_rational_gradients")

    xs = np.asarray(xs, dtype=float)
    theta = np.asarray(theta, dtype=float)
    phi = np.asarray(phi, dtype=float)

    # P, Q, and derivatives
    P = _polyval(theta, xs)
    Q = 1.0 + _polyval(
        np.concatenate([[0.0], phi]), xs
    )  # align powers: phi_k is x^k coefficient for k>=1
    dP = _polyval(_polyder(theta), xs)
    phi_full = np.concatenate([[0.0], phi])
    dQ = _polyval(_polyder(phi_full), xs)

    # Analytic derivative on REAL path where Q != 0
    mask_real = np.isfinite(xs) & np.isfinite(P) & np.isfinite(Q) & (Q != 0.0)
    dy_analytic = np.zeros_like(xs)
    dy_analytic[mask_real] = (dP[mask_real] * Q[mask_real] - P[mask_real] * dQ[mask_real]) / (
        Q[mask_real] ** 2
    )

    # Finite-difference derivative (central) where possible
    xh1 = xs + eps
    xh2 = xs - eps
    Ph1 = _polyval(theta, xh1)
    Qh1 = 1.0 + _polyval(np.concatenate([[0.0], phi]), xh1)
    yh1 = Ph1 / Qh1
    Ph2 = _polyval(theta, xh2)
    Qh2 = 1.0 + _polyval(np.concatenate([[0.0], phi]), xh2)
    yh2 = Ph2 / Qh2
    dy_fd = (yh1 - yh2) / (2.0 * eps)

    # Compare only on REAL path mask
    err = np.abs(dy_fd[mask_real] - dy_analytic[mask_real])
    if err.size == 0:
        return GradCheckResult(
            max_abs_err=float("nan"),
            mean_abs_err=float("nan"),
            n_points=0,
            n_masked=xs.size,
            eps=eps,
        )
    return GradCheckResult(
        max_abs_err=float(np.max(err)),
        mean_abs_err=float(np.mean(err)),
        n_points=int(err.size),
        n_masked=int(xs.size - err.size),
        eps=float(eps),
    )
