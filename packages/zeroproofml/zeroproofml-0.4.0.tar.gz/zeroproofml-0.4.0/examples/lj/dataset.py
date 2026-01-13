from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import torch
from torch import Tensor
from torch.utils.data import TensorDataset

from .lj_physics import lj_dv_dr, lj_energy


@dataclass(frozen=True)
class LJDimerDataConfig:
    epsilon: float = 1.0
    sigma: float = 1.0

    n_train: int = 50_000
    n_val: int = 10_000
    n_test: int = 20_000

    # Realistic regime: training data rarely includes overlaps (r < ~0.8σ).
    train_r_min: float = 0.8
    train_r_max: float = 3.0
    train_sampling: str = "uniform"  # "uniform" | "min_bias"
    train_sampling_power: float = 3.0

    # Test includes severe overlaps to probe singular extrapolation.
    test_r_min: float = 0.2
    test_r_max: float = 3.0

    # Make the test distribution stress the near-zero region.
    test_stress_fraction: float = 0.6
    test_stress_r_max: float = 0.8

    seed: int = 0
    dtype: str = "float64"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _dtype_from_name(name: str) -> torch.dtype:
    if str(name) == "float32":
        return torch.float32
    if str(name) == "float64":
        return torch.float64
    raise ValueError("dtype must be 'float32' or 'float64'")


def _sample_uniform(n: int, lo: float, hi: float, *, g: torch.Generator, device: str) -> Tensor:
    u = torch.rand((int(n),), generator=g, device=device)
    return float(lo) + (float(hi) - float(lo)) * u


def _sample_dimer_train(cfg: LJDimerDataConfig, *, n: int, g: torch.Generator, device: str) -> Tensor:
    s = float(cfg.sigma)
    lo = float(cfg.train_r_min) * s
    hi = float(cfg.train_r_max) * s
    mode = str(cfg.train_sampling)
    if mode == "uniform":
        return _sample_uniform(int(n), lo, hi, g=g, device=device)
    if mode == "min_bias":
        # Concentrate samples near the lower bound (the repulsive shoulder).
        p = float(cfg.train_sampling_power)
        if p <= 0:
            raise ValueError("train_sampling_power must be > 0")
        u = torch.rand((int(n),), generator=g, device=device)
        t = torch.pow(u, p)
        return lo + (hi - lo) * t
    raise ValueError("train_sampling must be 'uniform' or 'min_bias'")


def _sample_dimer_test(cfg: LJDimerDataConfig, *, n: int, g: torch.Generator, device: str) -> Tensor:
    s = float(cfg.sigma)
    n = int(n)
    n_stress = int(round(float(cfg.test_stress_fraction) * n))
    n_rest = n - n_stress

    # Stress region: sample log-uniform in [test_r_min, test_stress_r_max] * sigma
    lo = float(cfg.test_r_min) * s
    hi = float(cfg.test_stress_r_max) * s
    log_lo = torch.log(torch.tensor(lo, device=device))
    log_hi = torch.log(torch.tensor(hi, device=device))
    u = torch.rand((n_stress,), generator=g, device=device)
    stress = torch.exp(log_lo + (log_hi - log_lo) * u)

    rest = _sample_uniform(
        n_rest, float(cfg.test_stress_r_max) * s, float(cfg.test_r_max) * s, g=g, device=device
    )
    r = torch.cat([stress, rest], dim=0)
    r = r[torch.randperm(r.shape[0], generator=g, device=device)]
    return r


def make_lj_dimer_datasets(
    cfg: LJDimerDataConfig, *, device: str = "cpu"
) -> Tuple[TensorDataset, TensorDataset, TensorDataset]:
    g = torch.Generator(device=device)
    g.manual_seed(int(cfg.seed))
    dtype = _dtype_from_name(cfg.dtype)

    r_train = _sample_dimer_train(cfg, n=int(cfg.n_train), g=g, device=device).to(dtype)
    r_val = _sample_dimer_train(cfg, n=int(cfg.n_val), g=g, device=device).to(dtype)
    r_test = _sample_dimer_test(cfg, n=int(cfg.n_test), g=g, device=device).to(dtype)

    def _targets(r: Tensor) -> Tensor:
        v = lj_energy(r, epsilon=cfg.epsilon, sigma=cfg.sigma)
        dv = lj_dv_dr(r, epsilon=cfg.epsilon, sigma=cfg.sigma)
        return torch.stack([v, dv], dim=-1)

    y_train = _targets(r_train)
    y_val = _targets(r_val)
    y_test = _targets(r_test)

    x_train = r_train.unsqueeze(-1)
    x_val = r_val.unsqueeze(-1)
    x_test = r_test.unsqueeze(-1)

    return (
        TensorDataset(x_train, y_train),
        TensorDataset(x_val, y_val),
        TensorDataset(x_test, y_test),
    )
