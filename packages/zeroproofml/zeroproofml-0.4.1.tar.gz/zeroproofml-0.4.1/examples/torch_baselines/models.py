from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import torch
from torch import nn

from zeroproof.layers.projective_rational import ProjectiveRRModelConfig, RRProjectiveRationalModel


@dataclass(frozen=True)
class TorchMLPConfig:
    input_dim: int = 4
    output_dim: int = 2
    hidden_dims: Tuple[int, ...] = (64, 64)


class TorchMLP(nn.Module):
    def __init__(self, cfg: TorchMLPConfig) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.head = nn.Linear(prev, int(cfg.output_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.backbone(x))


class TorchMLPWithPoleHead(nn.Module):
    def __init__(self, cfg: TorchMLPConfig) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.reg_head = nn.Linear(prev, int(cfg.output_dim))
        self.pole_head = nn.Linear(prev, 1)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.reg_head(h), self.pole_head(h)


def build_projective_rr_model(
    *,
    hidden_dims: Iterable[int] = (64, 64),
    numerator_degree: int = 3,
    denominator_degree: int = 2,
    q_anchor: str = "ones",
    enable_pole_head: bool = False,
) -> RRProjectiveRationalModel:
    return RRProjectiveRationalModel(
        ProjectiveRRModelConfig(
            input_dim=4,
            output_dim=2,
            hidden_dims=tuple(int(x) for x in hidden_dims),
            numerator_degree=int(numerator_degree),
            denominator_degree=int(denominator_degree),
            q_anchor=str(q_anchor),
            enable_pole_head=bool(enable_pole_head),
        )
    )

