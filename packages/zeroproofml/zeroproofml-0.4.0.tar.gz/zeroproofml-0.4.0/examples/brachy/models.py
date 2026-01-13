from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class MLPConfig:
    input_dim: int = 2
    hidden_dims: Tuple[int, ...] = (64, 64)
    output_dim: int = 1


class MLP(nn.Module):
    def __init__(self, cfg: MLPConfig) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        layers.append(nn.Linear(prev, int(cfg.output_dim)))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class FourierFeatures(nn.Module):
    def __init__(self, *, input_dim: int, n_frequencies: int = 6, include_input: bool = True) -> None:
        super().__init__()
        self.input_dim = int(input_dim)
        self.n_frequencies = int(n_frequencies)
        self.include_input = bool(include_input)
        self.register_buffer("freqs", torch.tensor([2.0**k for k in range(int(n_frequencies))], dtype=torch.float32))

    def out_dim(self) -> int:
        base = self.input_dim if self.include_input else 0
        return base + (2 * self.input_dim * self.n_frequencies)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B,D)
        parts = []
        if self.include_input:
            parts.append(x)
        # broadcast freqs over batch and dims
        # (B,D,1) * (1,1,F) -> (B,D,F)
        ang = x.unsqueeze(-1) * self.freqs.view(1, 1, -1)
        parts.append(torch.sin(ang).reshape(x.shape[0], -1))
        parts.append(torch.cos(ang).reshape(x.shape[0], -1))
        return torch.cat(parts, dim=-1) if len(parts) > 1 else parts[0]


@dataclass(frozen=True)
class FourierMLPConfig:
    input_dim: int = 2
    n_frequencies: int = 6
    hidden_dims: Tuple[int, ...] = (64, 64)
    output_dim: int = 1


class FourierMLP(nn.Module):
    def __init__(self, cfg: FourierMLPConfig) -> None:
        super().__init__()
        self.ff = FourierFeatures(input_dim=int(cfg.input_dim), n_frequencies=int(cfg.n_frequencies), include_input=True)
        mlp_cfg = MLPConfig(input_dim=int(self.ff.out_dim()), hidden_dims=tuple(cfg.hidden_dims), output_dim=int(cfg.output_dim))
        self.mlp = MLP(mlp_cfg)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.mlp(self.ff(x))


class Sine(nn.Module):
    def __init__(self, w0: float = 30.0) -> None:
        super().__init__()
        self.w0 = float(w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sin(self.w0 * x)


@dataclass(frozen=True)
class SirenConfig:
    input_dim: int = 2
    hidden_dims: Tuple[int, ...] = (64, 64)
    w0: float = 30.0
    output_dim: int = 1


class Siren(nn.Module):
    def __init__(self, cfg: SirenConfig) -> None:
        super().__init__()
        self.w0 = float(cfg.w0)
        dims = [int(cfg.input_dim), *[int(h) for h in cfg.hidden_dims], int(cfg.output_dim)]
        layers: List[nn.Module] = []
        for i in range(len(dims) - 2):
            lin = nn.Linear(dims[i], dims[i + 1])
            self._init_siren(lin, first=(i == 0))
            layers.append(lin)
            layers.append(Sine(w0=float(cfg.w0)))
        last = nn.Linear(dims[-2], dims[-1])
        self._init_siren(last, first=False, last=True)
        layers.append(last)
        self.net = nn.Sequential(*layers)

    def _init_siren(self, layer: nn.Linear, *, first: bool, last: bool = False) -> None:
        with torch.no_grad():
            in_dim = layer.in_features
            if first:
                bound = 1.0 / max(1.0, float(in_dim))
            else:
                bound = math.sqrt(6.0 / float(in_dim)) / float(self.w0)
            layer.weight.uniform_(-bound, bound)
            layer.bias.uniform_(-bound, bound)
            if last:
                # Make output layer a bit smaller for stability.
                layer.weight.mul_(0.5)
                layer.bias.mul_(0.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass(frozen=True)
class ProjectivePQConfig:
    input_dim: int = 2
    hidden_dims: Tuple[int, ...] = (64, 64)
    q_anchor: str = "ones"  # "ones" | "none"


class ProjectivePQ(nn.Module):
    def __init__(self, cfg: ProjectivePQConfig) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.head_p = nn.Linear(prev, 1)
        self.head_q = nn.Linear(prev, 1)
        self.q_anchor = str(cfg.q_anchor)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        p = self.head_p(h)
        q = self.head_q(h)
        if self.q_anchor == "ones":
            q = q + torch.ones_like(q)
        return p, q


@dataclass(frozen=True)
class Rational2DPolyConfig:
    degree: int = 4
    r_scale_mm: float = 30.0
    q_min: float = 1e-6
    p_bias_init: float = 0.0
    q_bias_init: float = 1.0


class Rational2DPoly(nn.Module):
    """
    Multivariate rational polynomial in (r,theta):
      f(r,theta) = P(r_u, t_u) / Q(r_u, t_u)
    where r_u=r/r_scale_mm, t_u=theta/pi, both in [0,1] for the dataset.

    Q is constrained positive via softplus on its coefficients and bias.
    """

    def __init__(self, cfg: Rational2DPolyConfig) -> None:
        super().__init__()
        d = int(cfg.degree)
        if d < 0:
            raise ValueError("degree must be >= 0")
        self.degree = d
        self.r_scale_mm = float(cfg.r_scale_mm)
        self.q_min = float(cfg.q_min)

        self.P = nn.Parameter(torch.zeros(d + 1, d + 1))
        self.Q_raw = nn.Parameter(torch.zeros(d + 1, d + 1))
        self.p_bias = nn.Parameter(torch.tensor(float(cfg.p_bias_init)))
        self.q_bias_raw = nn.Parameter(torch.tensor(float(cfg.q_bias_init)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        r = x[:, 0:1]
        th = x[:, 1:2]
        r_u = torch.clamp_min(r, 0.0) / max(1e-12, float(self.r_scale_mm))
        t_u = torch.clamp(th, 0.0, math.pi) / math.pi
        r_u = torch.clamp(r_u, 0.0, 1.0)
        t_u = torch.clamp(t_u, 0.0, 1.0)

        r_u1 = r_u.squeeze(-1)
        t_u1 = t_u.squeeze(-1)
        r_pow = torch.stack([r_u1**i for i in range(self.degree + 1)], dim=-1)
        t_pow = torch.stack([t_u1**j for j in range(self.degree + 1)], dim=-1)

        num = torch.einsum("bi,bj,ij->b", r_pow, t_pow, self.P).unsqueeze(-1) + self.p_bias
        q_coeff = F.softplus(self.Q_raw)
        den = torch.einsum("bi,bj,ij->b", r_pow, t_pow, q_coeff).unsqueeze(-1)
        den = den + F.softplus(self.q_bias_raw) + float(self.q_min)
        return num / den
