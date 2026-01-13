from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch import Tensor

from zeroproof.layers.scm_rational import SCMRationalLayer
from zeroproof.scm.ops import scm_div_torch, scm_pow_torch

from .lj_physics import lj_energy


def rbf_features(r: Tensor, *, n: int, r_min: float, r_max: float) -> Tensor:
    """Gaussian RBF expansion over r (shape (...,1) or (...,))."""

    if r.dim() == 2 and r.shape[-1] == 1:
        r = r.squeeze(-1)
    if r.dim() != 1:
        raise ValueError("r must have shape (B,) or (B,1)")
    centers = torch.linspace(float(r_min), float(r_max), int(n), device=r.device, dtype=r.dtype)
    widths = (centers[1] - centers[0]).clamp(min=torch.finfo(r.dtype).eps)
    gamma = 1.0 / (2.0 * widths * widths)
    diffs = r.unsqueeze(-1) - centers.unsqueeze(0)
    return torch.exp(-gamma * diffs * diffs)


@dataclass(frozen=True)
class SmoothMLPConfig:
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "silu"  # "relu" | "silu" | "tanh"


class SmoothMLP(nn.Module):
    """Smooth baseline: MLP(r) -> energy."""

    def __init__(self, cfg: SmoothMLPConfig, *, in_dim: int = 1) -> None:
        super().__init__()
        act: nn.Module
        if cfg.activation == "relu":
            act = nn.ReLU()
        elif cfg.activation == "tanh":
            act = nn.Tanh()
        elif cfg.activation == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be one of: relu, silu, tanh")

        layers: list[nn.Module] = []
        prev = int(in_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self.net(x).squeeze(-1)


@dataclass(frozen=True)
class RBFMLPConfig:
    n_rbf: int = 64
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "silu"


class RBFMLP(nn.Module):
    """Baseline: RBF(r) -> MLP -> energy."""

    def __init__(self, cfg: RBFMLPConfig, *, r_min: float, r_max: float) -> None:
        super().__init__()
        self.r_min = float(r_min)
        self.r_max = float(r_max)
        self.n_rbf = int(cfg.n_rbf)
        self.backbone = SmoothMLP(
            SmoothMLPConfig(hidden_dims=cfg.hidden_dims, activation=cfg.activation),
            in_dim=int(cfg.n_rbf),
        )

    def forward(self, x: Tensor) -> Tensor:
        if x.dim() != 2 or x.shape[-1] != 1:
            raise ValueError("x must have shape (B,1) with r distances")
        feats = rbf_features(x, n=self.n_rbf, r_min=self.r_min, r_max=self.r_max)
        return self.backbone(feats)


@dataclass(frozen=True)
class RBFNetConfig:
    n_rbf: int = 50
    hidden_dims: tuple[int, ...] = (128, 128, 128)
    activation: str = "silu"


class RBFNet(nn.Module):
    """RBF baseline for arbitrary 1D input (e.g., u=1/r)."""

    def __init__(self, cfg: RBFNetConfig, *, x_min: float, x_max: float) -> None:
        super().__init__()
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.n_rbf = int(cfg.n_rbf)
        self.backbone = SmoothMLP(
            SmoothMLPConfig(hidden_dims=cfg.hidden_dims, activation=cfg.activation),
            in_dim=int(cfg.n_rbf),
        )

    def forward(self, x: Tensor) -> Tensor:
        if x.dim() != 2 or x.shape[-1] != 1:
            raise ValueError("x must have shape (B,1)")
        feats = rbf_features(x, n=self.n_rbf, r_min=self.x_min, r_max=self.x_max)
        return self.backbone(feats)


@dataclass(frozen=True)
class SirenConfig:
    hidden_dims: tuple[int, ...] = (128, 128, 128)
    w0: float = 30.0


class _Sine(nn.Module):
    def __init__(self, w0: float) -> None:
        super().__init__()
        self.w0 = float(w0)

    def forward(self, x: Tensor) -> Tensor:
        return torch.sin(self.w0 * x)


class SirenNet(nn.Module):
    """SIREN-style coordinate MLP for 1D input."""

    def __init__(self, cfg: SirenConfig, *, in_dim: int = 1) -> None:
        super().__init__()
        if not cfg.hidden_dims:
            raise ValueError("hidden_dims must be non-empty")
        layers: list[nn.Module] = []
        prev = int(in_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(_Sine(cfg.w0))
            prev = int(h)
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        if x.dim() != 2:
            raise ValueError("x must have shape (B,1)")
        return self.net(x).squeeze(-1)


@dataclass(frozen=True)
class SCMRationalConfig:
    numerator_degree: int = 8
    denominator_degree: int = 4


class SCMRationalEnergy(nn.Module):
    """SCM rational energy model for 1D input, returning (energy, bottom_mask)."""

    def __init__(self, cfg: SCMRationalConfig) -> None:
        super().__init__()
        self.layer = SCMRationalLayer(
            numerator_degree=int(cfg.numerator_degree),
            denominator_degree=int(cfg.denominator_degree),
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        if x.dim() == 2 and x.shape[-1] == 1:
            x = x.squeeze(-1)
        if x.dim() != 1:
            raise ValueError("x must have shape (B,) or (B,1)")
        return self.layer(x)


@dataclass(frozen=True)
class LJOracleConfig:
    epsilon: float = 1.0
    sigma: float = 1.0
    feature_scale: float = 1.0


class LJOracleFromReciprocal(nn.Module):
    """Analytic LJ energy expressed in u=1/r features (for 'oracle' tether scores)."""

    def __init__(self, cfg: LJOracleConfig) -> None:
        super().__init__()
        self.cfg = cfg

    def forward(self, x: Tensor) -> Tensor:
        if x.dim() != 2 or x.shape[-1] != 1:
            raise ValueError("x must have shape (B,1) containing scaled u=1/r")
        # Compute in float64 for near-exact agreement with float64 ground truth labels.
        u = x.squeeze(-1).to(torch.float64) * float(self.cfg.feature_scale)
        # r = 1/u; compute in a numerically safe way.
        r = 1.0 / u.clamp(min=torch.finfo(u.dtype).tiny)
        return lj_energy(r, epsilon=float(self.cfg.epsilon), sigma=float(self.cfg.sigma))


@dataclass(frozen=True)
class ImproperRationalHeadConfig:
    degree_p: int = 4
    degree_q: int = 2
    q_param: str = "softplus"  # "softplus" | "none"
    q_min: float = 1e-4
    lead_positive: bool = False
    lead_min: float = 0.1


class ImproperRationalHead(nn.Module):
    """Improper rational P(z)/Q(z) with degree_p > degree_q and positive denominator option."""

    def __init__(self, cfg: ImproperRationalHeadConfig) -> None:
        super().__init__()
        if int(cfg.degree_p) < 0 or int(cfg.degree_q) < 0:
            raise ValueError("degrees must be non-negative")
        if int(cfg.degree_p) <= int(cfg.degree_q):
            raise ValueError("ImproperRationalHead requires degree_p > degree_q")
        if str(cfg.q_param) not in ("softplus", "none"):
            raise ValueError("q_param must be 'softplus' or 'none'")
        self.cfg = cfg
        self.num = nn.Parameter(torch.empty(int(cfg.degree_p) + 1))
        self.den = nn.Parameter(torch.empty(int(cfg.degree_q) + 1))
        with torch.no_grad():
            nn.init.normal_(self.num, mean=0.0, std=1e-2)
            nn.init.normal_(self.den, mean=0.0, std=1e-2)
            # anchor denominator to be near 1 initially (helps stability).
            self.den[0].fill_(1.0)

    def forward(self, z: Tensor) -> Tensor:
        if z.dim() != 1:
            raise ValueError("z must have shape (B,)")
        deg_p = int(self.cfg.degree_p)
        deg_q = int(self.cfg.degree_q)
        max_deg = max(deg_p, deg_q)
        exps = torch.arange(max_deg + 1, device=z.device, dtype=z.dtype)
        feats = torch.pow(z.unsqueeze(-1), exps)  # (B, K)
        if bool(self.cfg.lead_positive):
            # Guarantee P(z) has a positive leading coefficient, preventing E -> -inf "black holes"
            # as z -> +inf (the main structural variance source for singularity fitting).
            lead = torch.nn.functional.softplus(self.num[-1].to(z.dtype)) + float(self.cfg.lead_min)
            p = torch.sum(feats[:, :deg_p] * self.num[:-1].to(z.dtype), dim=-1) + lead * feats[:, deg_p]
        else:
            p = torch.sum(feats[:, : deg_p + 1] * self.num.to(z.dtype), dim=-1)
        q_raw = torch.sum(feats[:, : deg_q + 1] * self.den.to(z.dtype), dim=-1)
        if str(self.cfg.q_param) == "softplus":
            q = torch.nn.functional.softplus(q_raw) + float(self.cfg.q_min)
        else:
            q = q_raw
        return p / q


@dataclass(frozen=True)
class DeepImproperZPMLConfig:
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "relu"  # "relu" | "silu"
    head: ImproperRationalHeadConfig = ImproperRationalHeadConfig()
    use_skip: bool = False
    latent_transform: str = "none"  # "none" | "softplus" | "abs" | "u_plus_softplus"


class DeepImproperZPML(nn.Module):
    """Backbone MLP (u->z) + improper rational head (z->E). Returns (E, bottom_mask)."""

    def __init__(self, cfg: DeepImproperZPMLConfig) -> None:
        super().__init__()
        self.cfg = cfg
        if str(cfg.activation) == "relu":
            act: nn.Module = nn.ReLU()
        elif str(cfg.activation) == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be 'relu' or 'silu'")
        if str(cfg.latent_transform) not in ("none", "softplus", "abs", "u_plus_softplus"):
            raise ValueError("latent_transform must be one of: none, softplus, abs, u_plus_softplus")
        layers: list[nn.Module] = []
        prev = 1
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)
        layers.append(nn.Linear(prev, 1))
        self.backbone = nn.Sequential(*layers)
        self.head = ImproperRationalHead(cfg.head)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        if x.dim() != 2 or x.shape[-1] != 1:
            raise ValueError("x must have shape (B,1)")
        lt = str(self.cfg.latent_transform)
        if lt == "u_plus_softplus":
            # Guarantees z >= u and z grows at least linearly with u (stability for asymptotic fits).
            z = x.squeeze(-1) + torch.nn.functional.softplus(self.backbone(x).squeeze(-1))
        else:
            z = self.backbone(x).squeeze(-1)
            if bool(self.cfg.use_skip):
                z = z + x.squeeze(-1)
            if lt == "softplus":
                z = torch.nn.functional.softplus(z)
            elif lt == "abs":
                z = z.abs()
            elif lt != "none":
                raise ValueError("latent_transform must be one of: none, softplus, abs, u_plus_softplus")
        e = self.head(z)
        bottom = torch.zeros((e.shape[0],), device=e.device, dtype=torch.bool)
        return e, bottom


def hard_wall_repulsion(
    r: Tensor, *, epsilon: float = 1.0, sigma: float = 1.0, power: int = 12
) -> tuple[Tensor, Tensor]:
    """Compute 4ε(σ/r)^power with SCM-safe division; returns (value, bottom_mask)."""

    if r.dim() != 1:
        raise ValueError("r must have shape (B,)")
    sigma_t = torch.full_like(r, float(sigma))
    ratio, bottom = scm_div_torch(sigma_t, r)
    ratio_pow, bottom2 = scm_pow_torch(ratio, float(power), bottom)
    bottom = torch.logical_or(bottom, bottom2)
    return (4.0 * float(epsilon)) * ratio_pow, bottom


@dataclass(frozen=True)
class HardWallResidualConfig:
    epsilon: float = 1.0
    sigma: float = 1.0
    repulsion_power: int = 12
    residual_type: str = "scm_rational"  # "mlp" | "scm_rational"
    residual_hidden_dims: tuple[int, ...] = (128, 128)
    residual_activation: str = "silu"
    numerator_degree: int = 6
    denominator_degree: int = 4


class HardWallResidual(nn.Module):
    """Pole-native model: analytic 1/r^p repulsion + learnable residual."""

    def __init__(self, cfg: HardWallResidualConfig) -> None:
        super().__init__()
        self.cfg = cfg
        if cfg.residual_type == "mlp":
            self.residual = SmoothMLP(
                SmoothMLPConfig(hidden_dims=cfg.residual_hidden_dims, activation=cfg.residual_activation)
            )
        elif cfg.residual_type == "scm_rational":
            self.residual = SCMRationalLayer(
                numerator_degree=int(cfg.numerator_degree),
                denominator_degree=int(cfg.denominator_degree),
            )
        else:
            raise ValueError("residual_type must be 'mlp' or 'scm_rational'")

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        if x.dim() != 2 or x.shape[-1] != 1:
            raise ValueError("x must have shape (B,1) with r distances")
        r = x.squeeze(-1)
        rep, bottom = hard_wall_repulsion(
            r, epsilon=self.cfg.epsilon, sigma=self.cfg.sigma, power=self.cfg.repulsion_power
        )
        if isinstance(self.residual, SCMRationalLayer):
            res, res_bottom = self.residual(r)
            bottom = torch.logical_or(bottom, res_bottom)
        else:
            res = self.residual(x)
        return rep + res, bottom


def predict_energy(model: nn.Module, x: Tensor) -> tuple[Tensor, Tensor]:
    """Unified prediction API returning (energy, bottom_mask)."""

    out = model(x)
    if isinstance(out, tuple) and len(out) == 2:
        energy, bottom = out
        return energy, bottom
    if isinstance(out, Tensor):
        return out, torch.zeros((out.shape[0],), device=out.device, dtype=torch.bool)
    raise TypeError("Model must return Tensor or (Tensor, bottom_mask)")
