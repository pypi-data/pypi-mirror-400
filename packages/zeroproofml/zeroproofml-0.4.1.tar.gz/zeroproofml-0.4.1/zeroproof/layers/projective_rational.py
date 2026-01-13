# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Projective rational heads for SCM training.

These modules emit projective tuples ``(P, Q)`` directly (no division in the
forward pass). They are intended to be decoded via strict SCM inference.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from zeroproof.layers.scm_rational import BasisFunction, MonomialBasis

__all__ = ["ProjectiveRationalMultiHead", "ProjectiveRRModelConfig", "RRProjectiveRationalModel"]


@dataclass(frozen=True)
class ProjectiveRRModelConfig:
    input_dim: int = 4
    output_dim: int = 2
    hidden_dims: tuple[int, ...] = (64, 64)
    numerator_degree: int = 3
    denominator_degree: int = 2
    q_anchor: str = "ones"  # "ones" -> Q = 1 + δQ ; "none" -> Q = δQ
    q_param: str = "none"  # "none" | "softplus"
    q_min: float = 0.0
    basis: BasisFunction = MonomialBasis()
    enable_pole_head: bool = False


class ProjectiveRationalMultiHead(nn.Module):  # type: ignore[misc]
    """Multi-output rational head with a shared denominator feature.

    The head consumes:
      - `z_num`: shape `(B, O)` numerator features (one scalar feature per output)
      - `z_den`: shape `(B,)` or `(B, 1)` shared denominator feature

    And emits `(P, Q)` of shape `(B, O)` each, so downstream code can apply
    projective renormalization and strict SCM decoding.
    """

    def __init__(
        self,
        output_dim: int,
        numerator_degree: int,
        denominator_degree: int,
        *,
        basis: BasisFunction | None = None,
        q_anchor: str = "ones",
        q_param: str = "none",
        q_min: float = 0.0,
    ) -> None:
        super().__init__()
        if output_dim <= 0:
            raise ValueError("output_dim must be positive")
        if numerator_degree < 0 or denominator_degree < 0:
            raise ValueError("degrees must be non-negative")
        if q_anchor not in ("ones", "none"):
            raise ValueError("q_anchor must be 'ones' or 'none'")
        if q_param not in ("none", "softplus"):
            raise ValueError("q_param must be 'none' or 'softplus'")
        if float(q_min) < 0.0:
            raise ValueError("q_min must be non-negative")

        self.output_dim = int(output_dim)
        self.numerator_degree = int(numerator_degree)
        self.denominator_degree = int(denominator_degree)
        self.basis = basis or MonomialBasis()
        self.q_anchor = str(q_anchor)
        self.q_param = str(q_param)
        self.q_min = float(q_min)

        self.num_weights = nn.Parameter(torch.empty(self.output_dim, self.numerator_degree + 1))
        self.den_weights = nn.Parameter(torch.empty(self.denominator_degree + 1))

        with torch.no_grad():
            nn.init.normal_(self.num_weights, mean=0.0, std=1e-2)
            nn.init.normal_(self.den_weights, mean=0.0, std=1e-2)

    def forward(self, z_num: Tensor, z_den: Tensor) -> tuple[Tensor, Tensor]:
        if z_num.dim() != 2:
            raise ValueError("z_num must have shape (batch, output_dim)")
        if z_num.shape[-1] != self.output_dim:
            raise ValueError(f"z_num last dim must be output_dim={self.output_dim}")
        if z_den.dim() == 2 and z_den.shape[-1] == 1:
            z_den = z_den.squeeze(-1)
        if z_den.dim() != 1:
            raise ValueError("z_den must have shape (batch,) or (batch, 1)")
        if z_den.shape[0] != z_num.shape[0]:
            raise ValueError("z_den batch dimension must match z_num")

        # Polynomial features
        p_feats = self.basis(z_num, self.numerator_degree)  # (B, O, Kp)
        q_feats = self.basis(z_den, self.denominator_degree)  # (B, Kq)

        # Avoid `einsum` here: it requires identical dtypes across operands.
        # Elementwise ops naturally promote dtypes (e.g., float32 params with float64 inputs).
        P = torch.sum(p_feats * self.num_weights.unsqueeze(0), dim=-1)
        Q_delta = torch.sum(q_feats * self.den_weights, dim=-1).unsqueeze(-1).expand_as(P)
        if self.q_param == "softplus":
            Q_delta = F.softplus(Q_delta) + float(self.q_min)
        if self.q_anchor == "ones":
            Q = Q_delta + torch.ones_like(Q_delta)
        else:
            Q = Q_delta
        return P, Q


class RRProjectiveRationalModel(nn.Module):  # type: ignore[misc]
    """RR IK model: MLP frontend -> shared-denominator projective rational head."""

    def __init__(self, config: ProjectiveRRModelConfig) -> None:
        super().__init__()
        if not config.hidden_dims:
            raise ValueError("hidden_dims must be non-empty")

        layers: list[nn.Module] = []
        prev = int(config.input_dim)
        for h in config.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)

        # One shared denominator feature + one numerator feature per output.
        self.feature_head = nn.Linear(prev, 1 + int(config.output_dim))
        self.enable_pole_head = bool(config.enable_pole_head)
        if self.enable_pole_head:
            self.pole_head = nn.Linear(prev, 1)
        self.rational_head = ProjectiveRationalMultiHead(
            output_dim=int(config.output_dim),
            numerator_degree=int(config.numerator_degree),
            denominator_degree=int(config.denominator_degree),
            basis=config.basis,
            q_anchor=config.q_anchor,
            q_param=config.q_param,
            q_min=config.q_min,
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor] | tuple[Tensor, Tensor, Tensor]:
        h = self.backbone(x)
        feats = self.feature_head(h)
        z_den = feats[:, :1]
        z_num = feats[:, 1:]
        P, Q = self.rational_head(z_num, z_den)
        if self.enable_pole_head:
            pole_logit = self.pole_head(h)
            return P, Q, pole_logit
        return P, Q
