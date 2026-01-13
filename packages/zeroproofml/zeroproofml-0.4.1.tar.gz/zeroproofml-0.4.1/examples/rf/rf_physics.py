from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor


@dataclass(frozen=True)
class ResonatorParams:
    """
    2nd-order resonator transfer function:
      H(s) = w0^2 / (s^2 + (w0/Q)s + w0^2)
    """

    w0: float
    q: float


def resonator_coeffs(*, w0: Tensor, q: Tensor) -> tuple[Tensor, Tensor, Tensor]:
    """Return (b0, b1, b2) for denominator b2*s^2 + b1*s + b0 with b2=1."""

    # Den(s) = s^2 + (w0/Q)s + w0^2
    b2 = torch.ones_like(w0)
    b1 = w0 / q
    b0 = w0 * w0
    return b0, b1, b2


def eval_poly_jw(coeffs: Tensor, w: Tensor) -> Tensor:
    """
    Evaluate a real-coefficient polynomial in s at s = j*w.

    coeffs: (..., K) for ascending powers in s: sum_k coeffs[...,k] * s^k
    w: (...,) (broadcastable with coeffs leading dims)
    returns complex tensor (...,)
    """

    if coeffs.dim() < 1:
        raise ValueError("coeffs must have at least 1 dimension")
    if w.dim() < 1:
        raise ValueError("w must have at least 1 dimension")

    # Horner in complex domain.
    s = 1j * w.to(torch.complex64 if w.dtype == torch.float32 else torch.complex128)
    out = torch.zeros_like(s)
    for k in range(int(coeffs.shape[-1]) - 1, -1, -1):
        out = out * s + coeffs[..., k].to(out.dtype)
    return out


def resonator_response(w: Tensor, *, w0: Tensor, q: Tensor) -> Tensor:
    """Return complex H(j*w) for the resonator."""

    b0, b1, b2 = resonator_coeffs(w0=w0, q=q)
    # P(s) = w0^2
    num = (w0 * w0).to(torch.complex64 if w.dtype == torch.float32 else torch.complex128)
    den_coeffs = torch.stack([b0, b1, b2], dim=-1)
    den = eval_poly_jw(den_coeffs, w)
    return num / den


def safe_complex_div(num: Tensor, den: Tensor, *, eps: float = 1e-8) -> tuple[Tensor, Tensor]:
    """Return (num/den, bottom_mask) where bottom_mask flags small |den|."""

    if not torch.is_complex(num) or not torch.is_complex(den):
        raise ValueError("num and den must be complex tensors")
    den_abs2 = (den.real * den.real + den.imag * den.imag).to(torch.float64)
    bottom = den_abs2 < float(eps) ** 2
    out = torch.where(bottom, torch.zeros_like(num), num / den)
    return out, bottom


def logspace_w(*, w_min: float, w_max: float, n: int, device: str, dtype: torch.dtype) -> Tensor:
    if w_min <= 0 or w_max <= 0:
        raise ValueError("w_min and w_max must be positive for logspace")
    exps = torch.linspace(math.log10(float(w_min)), math.log10(float(w_max)), int(n), device=device, dtype=dtype)
    return (10.0 ** exps).to(dtype)

