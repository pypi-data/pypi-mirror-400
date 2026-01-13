from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor


@dataclass(frozen=True)
class LJParams:
    epsilon: float = 1.0
    sigma: float = 1.0


def lj_minimum_distance(*, sigma: float = 1.0) -> float:
    """Return r* = 2^(1/6) * sigma (minimum of Lennard-Jones potential)."""

    return float((2.0 ** (1.0 / 6.0)) * float(sigma))


def lj_energy(r: Tensor, *, epsilon: float = 1.0, sigma: float = 1.0) -> Tensor:
    """Lennard-Jones energy: V(r) = 4ε[(σ/r)^12 - (σ/r)^6]."""

    if not isinstance(r, Tensor):
        raise TypeError("r must be a torch.Tensor")
    inv = (float(sigma) / r).clamp(min=torch.finfo(r.dtype).tiny)
    inv6 = inv.pow(6)
    inv12 = inv6 * inv6
    return (4.0 * float(epsilon)) * (inv12 - inv6)


def lj_dv_dr(r: Tensor, *, epsilon: float = 1.0, sigma: float = 1.0) -> Tensor:
    """Analytic derivative dV/dr for Lennard-Jones potential."""

    if not isinstance(r, Tensor):
        raise TypeError("r must be a torch.Tensor")
    sig = float(sigma)
    eps = float(epsilon)
    r_safe = r.clamp(min=torch.finfo(r.dtype).tiny)
    inv_r = 1.0 / r_safe
    sr = sig * inv_r
    sr6 = sr.pow(6)
    sr12 = sr6 * sr6
    # d/dr [4ε( (σ/r)^12 - (σ/r)^6 )]
    # = 4ε( -12 σ^12 r^-13 + 6 σ^6 r^-7 )
    term12 = -12.0 * (sig**12) * inv_r.pow(13)
    term6 = 6.0 * (sig**6) * inv_r.pow(7)
    # Alternatively: sr12 and sr6 forms are equivalent but this is explicit.
    _ = sr6, sr12  # keep for debugging/consistency if needed
    return (4.0 * eps) * (term12 + term6)


def lj_force_magnitude(r: Tensor, *, epsilon: float = 1.0, sigma: float = 1.0) -> Tensor:
    """Return scalar force magnitude for a dimer: F(r) = -dV/dr."""

    return -lj_dv_dr(r, epsilon=epsilon, sigma=sigma)


def min_pair_distance(positions: Tensor) -> Tensor:
    """Return per-sample minimum pairwise distance for positions (B,N,3)."""

    if positions.dim() != 3 or positions.size(-1) != 3:
        raise ValueError("positions must have shape (B, N, 3)")
    b, n, _ = positions.shape
    diffs = positions.unsqueeze(2) - positions.unsqueeze(1)  # (B,N,N,3)
    dists = torch.linalg.norm(diffs, dim=-1)  # (B,N,N)
    eye = torch.eye(n, device=positions.device, dtype=torch.bool).unsqueeze(0).expand(b, -1, -1)
    dists = dists.masked_fill(eye, float("inf"))
    return dists.amin(dim=(1, 2))


def sum_pairwise_lj_energy(
    positions: Tensor, *, epsilon: float = 1.0, sigma: float = 1.0
) -> Tensor:
    """Sum Lennard-Jones energy across all pairs for positions (B,N,3)."""

    if positions.dim() != 3 or positions.size(-1) != 3:
        raise ValueError("positions must have shape (B, N, 3)")
    diffs = positions.unsqueeze(2) - positions.unsqueeze(1)  # (B,N,N,3)
    dists = torch.linalg.norm(diffs, dim=-1)  # (B,N,N)
    b, n, _ = dists.shape
    eye = torch.eye(n, device=positions.device, dtype=torch.bool).unsqueeze(0).expand(b, -1, -1)
    dists = dists.masked_fill(eye, 1.0)  # avoid divide by zero; masked out below anyway
    e = lj_energy(dists, epsilon=epsilon, sigma=sigma)
    e = e.masked_fill(eye, 0.0)
    return 0.5 * e.sum(dim=(1, 2))


def lj_energy_buckets(*, sigma: float = 1.0) -> list[tuple[str, float, float]]:
    """Bucket edges for reporting, expressed in multiples of sigma."""

    s = float(sigma)
    return [
        ("r<0.5σ", 0.0, 0.5 * s),
        ("0.5σ–0.8σ", 0.5 * s, 0.8 * s),
        ("0.8σ–1.2σ", 0.8 * s, 1.2 * s),
        ("1.2σ–2.0σ", 1.2 * s, 2.0 * s),
        ("r≥2.0σ", 2.0 * s, float("inf")),
    ]


def bucket_mask(r: Tensor, lo: float, hi: float) -> Tensor:
    if not isinstance(r, Tensor):
        raise TypeError("r must be a torch.Tensor")
    if math.isinf(float(hi)):
        return r >= float(lo)
    return (r >= float(lo)) & (r < float(hi))

