from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import torch
from torch import nn


@dataclass(frozen=True)
class PowerMLPConfig:
    input_dim: int
    output_dim: int = 1
    hidden_dims: Tuple[int, ...] = (64, 64)


class PowerMLP(nn.Module):
    def __init__(self, cfg: PowerMLPConfig) -> None:
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


class PowerMLPMultiTask(nn.Module):
    def __init__(self, cfg: PowerMLPConfig, *, n_classes: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.reg_head = nn.Linear(prev, int(cfg.output_dim))
        self.cls_head = nn.Linear(prev, int(n_classes))

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.reg_head(h), self.cls_head(h)


class PowerMLPWithPoleHead(nn.Module):
    def __init__(self, cfg: PowerMLPConfig) -> None:
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


class PowerMLPWithMultiPoleHead(nn.Module):
    def __init__(self, cfg: PowerMLPConfig, *, n_poles: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.reg_head = nn.Linear(prev, int(cfg.output_dim))
        self.pole_head = nn.Linear(prev, int(n_poles))

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.reg_head(h), self.pole_head(h)


@dataclass(frozen=True)
class PowerProjectivePQConfig:
    input_dim: int
    output_dim: int = 1
    hidden_dims: Tuple[int, ...] = (64, 64)
    q_anchor: str = "ones"  # "ones" | "none"


class PowerProjectivePQ(nn.Module):
    def __init__(self, cfg: PowerProjectivePQConfig) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.head_p = nn.Linear(prev, int(cfg.output_dim))
        self.head_q = nn.Linear(prev, int(cfg.output_dim))
        self.q_anchor = str(cfg.q_anchor)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        p = self.head_p(h)
        q = self.head_q(h)
        if self.q_anchor == "ones":
            q = q + torch.ones_like(q)
        return p, q


class PowerProjectivePQMultiTask(nn.Module):
    def __init__(self, cfg: PowerProjectivePQConfig, *, n_classes: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(nn.ReLU())
            prev = int(h)
        self.backbone = nn.Sequential(*layers)
        self.head_p = nn.Linear(prev, int(cfg.output_dim))
        self.head_q = nn.Linear(prev, int(cfg.output_dim))
        self.head_cls = nn.Linear(prev, int(n_classes))
        self.q_anchor = str(cfg.q_anchor)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        p = self.head_p(h)
        q = self.head_q(h)
        if self.q_anchor == "ones":
            q = q + torch.ones_like(q)
        logits = self.head_cls(h)
        return p, q, logits
