from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import torch
from torch import Tensor
from torch.utils.data import TensorDataset

from .rf_physics import resonator_response


@dataclass(frozen=True)
class RFResonatorDataConfig:
    n_filters_train: int = 2048
    n_filters_val: int = 512
    n_filters_test: int = 1024

    points_per_filter: int = 64

    # Frequency grid sampling.
    # - log_uniform: each point is sampled log-uniform in [w_min, w_max]
    # - mixture: 50/50 mix of global log-uniform + local Gaussian around resonance (w0)
    sampling_strategy: str = "log_uniform"  # "log_uniform" | "mixture"
    mixture_global_frac: float = 0.5
    mixture_local_sigma_scale: float = 1.0
    mixture_sort_within_filter: bool = True

    # Frequency range
    w_min: float = 0.1
    w_max: float = 10.0

    # Resonator parameter ranges (log-uniform)
    w0_min: float = 0.5
    w0_max: float = 5.0

    q_min: float = 2.0
    q_max_train: float = 30.0
    q_max_test: float = 200.0

    seed: int = 0
    dtype: str = "float32"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _dtype_from_name(name: str) -> torch.dtype:
    if str(name) == "float32":
        return torch.float32
    if str(name) == "float64":
        return torch.float64
    raise ValueError("dtype must be 'float32' or 'float64'")


def _log_uniform(n: int, lo: float, hi: float, *, g: torch.Generator, device: str, dtype: torch.dtype) -> Tensor:
    lo = float(lo)
    hi = float(hi)
    if lo <= 0 or hi <= 0:
        raise ValueError("log-uniform bounds must be positive")
    u = torch.rand((int(n),), generator=g, device=device, dtype=dtype)
    return torch.exp(torch.log(torch.tensor(lo, device=device, dtype=dtype)) + u * torch.log(torch.tensor(hi / lo, device=device, dtype=dtype)))


def _sample_frequencies(
    *,
    n_filters: int,
    points_per_filter: int,
    w0: Tensor,
    q: Tensor,
    cfg: RFResonatorDataConfig,
    g: torch.Generator,
    device: str,
    dtype: torch.dtype,
) -> Tensor:
    """
    Returns w with shape [n_filters * points_per_filter] in filter-major order.
    """
    n_filters = int(n_filters)
    points_per_filter = int(points_per_filter)
    if points_per_filter <= 0:
        raise ValueError("points_per_filter must be positive")

    strat = str(cfg.sampling_strategy)
    if strat == "log_uniform":
        return _log_uniform(n_filters * points_per_filter, cfg.w_min, cfg.w_max, g=g, device=device, dtype=dtype)

    if strat != "mixture":
        raise ValueError("sampling_strategy must be 'log_uniform' or 'mixture'")

    if points_per_filter == 1:
        return _log_uniform(n_filters, cfg.w_min, cfg.w_max, g=g, device=device, dtype=dtype)

    frac = float(cfg.mixture_global_frac)
    if not (0.0 <= frac <= 1.0):
        raise ValueError("mixture_global_frac must be in [0, 1]")

    n_global = int(points_per_filter * frac)
    n_global = max(0, min(points_per_filter, n_global))
    n_local = int(points_per_filter - n_global)

    parts: list[Tensor] = []
    if n_global:
        w_global = _log_uniform(n_filters * n_global, cfg.w_min, cfg.w_max, g=g, device=device, dtype=dtype).view(n_filters, n_global)
        parts.append(w_global)
    if n_local:
        sigma = (w0 / torch.clamp(q, min=0.5)) * float(cfg.mixture_local_sigma_scale)
        w_local = w0[:, None] + sigma[:, None] * torch.randn((n_filters, n_local), generator=g, device=device, dtype=dtype)
        w_local = torch.clamp(w_local, min=float(cfg.w_min), max=float(cfg.w_max))
        parts.append(w_local)

    w_mat = torch.cat(parts, dim=1) if len(parts) > 1 else parts[0]
    if bool(cfg.mixture_sort_within_filter):
        w_mat, _ = torch.sort(w_mat, dim=1)
    return w_mat.reshape(-1)


def _make_split(
    *,
    n_filters: int,
    points_per_filter: int,
    cfg: RFResonatorDataConfig,
    q_max: float,
    g: torch.Generator,
    device: str,
    dtype: torch.dtype,
) -> tuple[TensorDataset, Tensor]:
    # Sample filter parameters
    w0 = _log_uniform(int(n_filters), cfg.w0_min, cfg.w0_max, g=g, device=device, dtype=dtype)
    q = _log_uniform(int(n_filters), cfg.q_min, float(q_max), g=g, device=device, dtype=dtype)

    # Sample per-point frequencies
    w = _sample_frequencies(
        n_filters=int(n_filters),
        points_per_filter=int(points_per_filter),
        w0=w0,
        q=q,
        cfg=cfg,
        g=g,
        device=device,
        dtype=dtype,
    )
    filt_ids = torch.arange(int(n_filters), device=device, dtype=torch.int64).repeat_interleave(int(points_per_filter))
    w0_pts = w0[filt_ids]
    q_pts = q[filt_ids]

    # Inputs: [log10(w), log10(w0), log10(q)]
    x = torch.stack([torch.log10(w), torch.log10(w0_pts), torch.log10(q_pts)], dim=-1).to(dtype)

    h = resonator_response(w, w0=w0_pts, q=q_pts)
    y = torch.stack([h.real.to(dtype), h.imag.to(dtype)], dim=-1)

    ds = TensorDataset(x, y, filt_ids, w0_pts, q_pts, w)
    return ds, torch.stack([w0, q], dim=-1)


def make_rf_resonator_datasets(
    cfg: RFResonatorDataConfig, *, device: str = "cpu"
) -> Tuple[TensorDataset, TensorDataset, TensorDataset]:
    dtype = _dtype_from_name(cfg.dtype)
    g = torch.Generator(device=device)
    g.manual_seed(int(cfg.seed))

    train, _ = _make_split(
        n_filters=int(cfg.n_filters_train),
        points_per_filter=int(cfg.points_per_filter),
        cfg=cfg,
        q_max=float(cfg.q_max_train),
        g=g,
        device=device,
        dtype=dtype,
    )
    val, _ = _make_split(
        n_filters=int(cfg.n_filters_val),
        points_per_filter=int(cfg.points_per_filter),
        cfg=cfg,
        q_max=float(cfg.q_max_train),
        g=g,
        device=device,
        dtype=dtype,
    )
    test, _ = _make_split(
        n_filters=int(cfg.n_filters_test),
        points_per_filter=int(cfg.points_per_filter),
        cfg=cfg,
        q_max=float(cfg.q_max_test),
        g=g,
        device=device,
        dtype=dtype,
    )
    return train, val, test
