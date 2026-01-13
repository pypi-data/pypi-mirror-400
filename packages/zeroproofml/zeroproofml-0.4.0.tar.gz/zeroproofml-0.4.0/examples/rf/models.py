from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
from torch import Tensor

from zeroproof.layers.scm_rational import ChebyshevBasis, SCMRationalLayer
from zeroproof.scm.ops import scm_div_torch

from .rf_physics import eval_poly_jw, resonator_response, safe_complex_div


@dataclass(frozen=True)
class TorchMLPConfig:
    input_dim: int = 3  # [log10(w), log10(w0), log10(Q)]
    hidden_dims: tuple[int, ...] = (256, 256)
    activation: str = "silu"  # "relu" | "tanh" | "silu"
    output_dim: int = 2  # Re, Im


class TorchMLP(nn.Module):
    """Smooth baseline that outputs Re/Im directly."""

    def __init__(self, cfg: TorchMLPConfig) -> None:
        super().__init__()
        if not cfg.hidden_dims:
            raise ValueError("hidden_dims must be non-empty")
        if cfg.activation == "relu":
            act: nn.Module = nn.ReLU()
        elif cfg.activation == "tanh":
            act = nn.Tanh()
        elif cfg.activation == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be one of: relu, tanh, silu")

        layers: list[nn.Module] = []
        prev = int(cfg.input_dim)
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)
        layers.append(nn.Linear(prev, int(cfg.output_dim)))
        self.net = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self.net(x)


@dataclass(frozen=True)
class RationalTransferConfig:
    """
    Pole-native model:
      - Small MLP predicts *real* polynomial coefficients for P(s), Q(s)
      - Evaluate H(jw) = P(jw) / Q(jw) and output Re/Im

    Degrees default to quadratic to match the resonator family, but the head is learnable.
    """

    input_dim: int = 3
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "relu"
    degree_p: int = 2
    degree_q: int = 2
    q_anchor: str = "monic"  # "monic" -> enforce leading coeff = 1
    denom_eps: float = 1e-8


class RationalTransfer(nn.Module):
    def __init__(self, cfg: RationalTransferConfig) -> None:
        super().__init__()
        if cfg.activation == "relu":
            act: nn.Module = nn.ReLU()
        elif cfg.activation == "tanh":
            act = nn.Tanh()
        elif cfg.activation == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be one of: relu, tanh, silu")
        if cfg.degree_p < 0 or cfg.degree_q < 0:
            raise ValueError("degrees must be non-negative")
        if cfg.q_anchor not in ("monic", "none"):
            raise ValueError("q_anchor must be 'monic' or 'none'")

        self.cfg = cfg
        prev = int(cfg.input_dim)
        layers: list[nn.Module] = []
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)
        self.backbone = nn.Sequential(*layers)

        # Emit raw coefficients in ascending order:
        # P: (degree_p+1), Q: (degree_q+1) but optionally anchor Q leading term.
        out_dim = (cfg.degree_p + 1) + (cfg.degree_q + 1)
        if cfg.q_anchor == "monic":
            out_dim -= 1  # we don't emit leading coefficient
        self.head = nn.Linear(prev, int(out_dim))

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """
        Returns (y_pred, bottom_mask), where y_pred has shape (B,2) and bottom_mask is (B,).
        """

        if x.dim() != 2 or x.shape[-1] != int(self.cfg.input_dim):
            raise ValueError(f"x must have shape (B,{self.cfg.input_dim})")
        h = self.backbone(x)
        raw = self.head(h)

        dp = int(self.cfg.degree_p)
        dq = int(self.cfg.degree_q)
        p_raw = raw[:, : (dp + 1)]
        q_raw = raw[:, (dp + 1) :]

        if self.cfg.q_anchor == "monic":
            # Q(s) has leading coefficient fixed to 1.0 (monic), remaining are learnable.
            if q_raw.shape[-1] != dq:
                raise RuntimeError("internal shape mismatch for monic denominator")
            q_coeffs = torch.cat([q_raw, torch.ones((q_raw.shape[0], 1), device=q_raw.device, dtype=q_raw.dtype)], dim=-1)
        else:
            if q_raw.shape[-1] != (dq + 1):
                raise RuntimeError("internal shape mismatch for denominator")
            q_coeffs = q_raw

        # Evaluate at jw. We store log10(w) as the first feature.
        w = (10.0 ** x[:, 0]).to(x.dtype)
        num = eval_poly_jw(p_raw, w)
        den = eval_poly_jw(q_coeffs, w)
        h_c, bottom = safe_complex_div(num, den, eps=float(self.cfg.denom_eps))
        y = torch.stack([h_c.real.to(x.dtype), h_c.imag.to(x.dtype)], dim=-1)
        return y, bottom


@dataclass(frozen=True)
class ProjectiveSCMConfig:
    """
    ZeroProofML-SCM baseline for RF:
      x -> (small MLP) -> scalar latent z
      z -> SCMRationalLayer -> Re(H), Im(H)

    This gives the model an explicit rational/pole-capable head while keeping the input features identical
    to the smooth MLP baselines (no hidden feature engineering).
    """

    input_dim: int = 3
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "relu"  # "relu" | "tanh" | "silu"
    numerator_degree: int = 6
    denominator_degree: int = 6
    singular_epsilon: float = 1e-12


class ProjectiveSCMComplex(nn.Module):
    """Projective SCM-rational head producing complex response (Re/Im) with a shared scalar latent."""

    def __init__(self, cfg: ProjectiveSCMConfig) -> None:
        super().__init__()
        if not cfg.hidden_dims:
            raise ValueError("hidden_dims must be non-empty")
        if cfg.activation == "relu":
            act: nn.Module = nn.ReLU()
        elif cfg.activation == "tanh":
            act = nn.Tanh()
        elif cfg.activation == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be one of: relu, tanh, silu")

        prev = int(cfg.input_dim)
        layers: list[nn.Module] = []
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)
        layers.append(nn.Linear(prev, 1))
        self.backbone = nn.Sequential(*layers)

        basis = ChebyshevBasis()
        self.re_head = SCMRationalLayer(
            numerator_degree=int(cfg.numerator_degree),
            denominator_degree=int(cfg.denominator_degree),
            basis=basis,
            singular_epsilon=float(cfg.singular_epsilon),
        )
        self.im_head = SCMRationalLayer(
            numerator_degree=int(cfg.numerator_degree),
            denominator_degree=int(cfg.denominator_degree),
            basis=basis,
            singular_epsilon=float(cfg.singular_epsilon),
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        if x.dim() != 2 or x.shape[-1] != 3:
            raise ValueError("x must have shape (B,3)")
        z = self.backbone(x).squeeze(-1)
        re, b1 = self.re_head(z)
        im, b2 = self.im_head(z)
        bottom = torch.logical_or(b1, b2)
        y = torch.stack([re.to(x.dtype), im.to(x.dtype)], dim=-1)
        return y, bottom


@dataclass(frozen=True)
class SCMTransferHyperConfig:
    """
    ZeroProofML-SCM-Transfer:
      conditioning = [log10(w0), log10(Q)] -> (hypernetwork) -> real coefficients of P(s), Q(s)
      evaluate H(jw)=P(jw)/Q(jw) with a shared complex denominator.

    The backbone intentionally does NOT consume frequency w; it predicts the LTI system itself.
    """

    cond_dim: int = 2
    hidden_dims: tuple[int, ...] = (128, 128)
    activation: str = "silu"  # "relu" | "tanh" | "silu"
    degree_p: int = 2
    degree_q: int = 2
    q_anchor: str = "monic"  # enforce leading coefficient = 1 (recommended)
    q_coeff_param: str = "softplus"  # "softplus" | "none"
    q_coeff_min: float = 0.0
    denom_eps: float = 1e-8  # bottom threshold in |Q| (not squared)
    cond_mode: str = "logw0_logq"  # "logw0_logq" | "logw0_invq" | "w0_invq" | "logw0_damping" | "w0_damping"
    cond_scale_w0: float = 1.0
    cond_scale_invq: float = 1.0
    cond_scale_damping: float = 1.0


class SCMTransferHyper(nn.Module):
    """
    Physics-native transfer head with shared denominator and SCM-safe division.

    Input x is the standard feature vector:
      x[:,0]=log10(w), x[:,1]=log10(w0), x[:,2]=log10(Q)
    """

    def __init__(self, cfg: SCMTransferHyperConfig) -> None:
        super().__init__()
        if cfg.degree_p < 0 or cfg.degree_q < 0:
            raise ValueError("degrees must be non-negative")
        if cfg.q_anchor not in ("monic", "none"):
            raise ValueError("q_anchor must be 'monic' or 'none'")
        if cfg.q_coeff_param not in ("softplus", "none"):
            raise ValueError("q_coeff_param must be 'softplus' or 'none'")
        if cfg.cond_mode not in ("logw0_logq", "logw0_invq", "w0_invq", "logw0_damping", "w0_damping"):
            raise ValueError("cond_mode must be one of: logw0_logq, logw0_invq, w0_invq")
        if float(cfg.cond_scale_w0) <= 0:
            raise ValueError("cond_scale_w0 must be positive")
        if float(cfg.cond_scale_invq) <= 0:
            raise ValueError("cond_scale_invq must be positive")
        if float(cfg.cond_scale_damping) <= 0:
            raise ValueError("cond_scale_damping must be positive")

        self.cfg = cfg

        if cfg.activation == "relu":
            act: nn.Module = nn.ReLU()
        elif cfg.activation == "tanh":
            act = nn.Tanh()
        elif cfg.activation == "silu":
            act = nn.SiLU()
        else:
            raise ValueError("activation must be one of: relu, tanh, silu")

        prev = int(cfg.cond_dim)
        layers: list[nn.Module] = []
        for h in cfg.hidden_dims:
            layers.append(nn.Linear(prev, int(h)))
            layers.append(act)
            prev = int(h)

        out_dim = (cfg.degree_p + 1) + (cfg.degree_q + 1)
        if cfg.q_anchor == "monic":
            out_dim -= 1  # do not emit leading denom coefficient
        layers.append(nn.Linear(prev, int(out_dim)))
        self.net = nn.Sequential(*layers)

        # Bias init: prefer non-degenerate denominators at step 0.
        # Layout: [P0..Pdp, Q0..Q_{dq}] (or Q0..Q_{dq-1} if monic).
        with torch.no_grad():
            last = self.net[-1]
            if isinstance(last, nn.Linear):
                last.weight.mul_(0.01)
                # Nudge Q0 away from 0.
                q0_idx = int(cfg.degree_p + 1)
                if q0_idx < int(last.bias.numel()):
                    last.bias[q0_idx] = 1.0

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        if x.dim() != 2 or x.shape[-1] != 3:
            raise ValueError("x must have shape (B,3)")

        # Conditioning (design context). We intentionally do NOT feed frequency w.
        # For high-Q extrapolation, using inverse-Q (damping proxy) often linearizes
        # the mapping from conditioning -> pole real part.
        if self.cfg.cond_mode == "logw0_logq":
            cond = x[:, 1:3]
        elif self.cfg.cond_mode == "logw0_invq":
            logw0 = x[:, 1:2]
            logq = x[:, 2:3]
            invq = (10.0 ** (-logq)).to(x.dtype) / float(self.cfg.cond_scale_invq)
            cond = torch.cat([logw0, invq], dim=-1)
        elif self.cfg.cond_mode == "w0_invq":
            logw0 = x[:, 1:2]
            logq = x[:, 2:3]
            w0 = (10.0 ** logw0).to(x.dtype) / float(self.cfg.cond_scale_w0)
            invq = (10.0 ** (-logq)).to(x.dtype) / float(self.cfg.cond_scale_invq)
            cond = torch.cat([w0, invq], dim=-1)
        elif self.cfg.cond_mode == "logw0_damping":
            logw0 = x[:, 1:2]
            logq = x[:, 2:3]
            w0 = (10.0 ** logw0).to(x.dtype)
            invq = (10.0 ** (-logq)).to(x.dtype)
            damping = (w0 * invq).to(x.dtype) / float(self.cfg.cond_scale_damping)  # proportional to pole real part
            cond = torch.cat([logw0, damping], dim=-1)
        elif self.cfg.cond_mode == "w0_damping":
            logw0 = x[:, 1:2]
            logq = x[:, 2:3]
            w0 = (10.0 ** logw0).to(x.dtype) / float(self.cfg.cond_scale_w0)
            invq = (10.0 ** (-logq)).to(x.dtype)
            damping = (w0 * invq).to(x.dtype) / float(self.cfg.cond_scale_damping)
            cond = torch.cat([w0, damping], dim=-1)
        else:
            raise RuntimeError("unreachable cond_mode")
        raw = self.net(cond)

        dp = int(self.cfg.degree_p)
        dq = int(self.cfg.degree_q)
        p_coeffs = raw[:, : (dp + 1)]
        q_raw = raw[:, (dp + 1) :]

        if self.cfg.q_anchor == "monic":
            if q_raw.shape[-1] != dq:
                raise RuntimeError("internal shape mismatch for monic denominator")
            q_coeffs = torch.cat(
                [q_raw, torch.ones((q_raw.shape[0], 1), device=q_raw.device, dtype=q_raw.dtype)], dim=-1
            )
        else:
            if q_raw.shape[-1] != (dq + 1):
                raise RuntimeError("internal shape mismatch for denominator")
            q_coeffs = q_raw

        if self.cfg.q_coeff_param == "softplus":
            q_coeffs = torch.nn.functional.softplus(q_coeffs) + float(self.cfg.q_coeff_min)

        # Evaluate at jw.
        w = (10.0 ** x[:, 0]).to(x.dtype)
        p_jw = eval_poly_jw(p_coeffs, w)
        q_jw = eval_poly_jw(q_coeffs, w)

        # Shared-denominator SCM-safe division:
        # H = (P*conj(Q)) / |Q|^2, with ⊥ when |Q| is tiny.
        q_abs2 = (q_jw.real * q_jw.real + q_jw.imag * q_jw.imag).to(x.dtype)
        bottom = q_abs2 < float(self.cfg.denom_eps) ** 2
        num = p_jw * torch.conj(q_jw)
        re, b_re = scm_div_torch(num.real.to(x.dtype), q_abs2, mask_y=bottom)
        im, b_im = scm_div_torch(num.imag.to(x.dtype), q_abs2, mask_y=bottom)
        b = torch.logical_or(b_re, b_im)
        y = torch.stack([re.to(x.dtype), im.to(x.dtype)], dim=-1)
        return y, b


def predict_re_im(model: nn.Module, x: Tensor) -> tuple[Tensor, Tensor]:
    out = model(x)
    if isinstance(out, tuple) and len(out) == 2:
        y, bottom = out
        return y, bottom
    if isinstance(out, Tensor):
        bottom = torch.zeros((out.shape[0],), device=out.device, dtype=torch.bool)
        return out, bottom
    raise TypeError("Model must return Tensor or (Tensor, bottom_mask)")


class AnalyticResonator(nn.Module):
    """
    Analytic reference for the synthetic benchmark.

    Interprets input features as:
      x[:,0] = log10(w)
      x[:,1] = log10(w0)
      x[:,2] = log10(Q)
    and returns the exact H(jw) for the resonator family.
    """

    def forward(self, x: Tensor) -> Tensor:
        if x.dim() != 2 or x.shape[-1] != 3:
            raise ValueError("x must have shape (B,3)")
        w = 10.0 ** x[:, 0]
        w0 = 10.0 ** x[:, 1]
        q = 10.0 ** x[:, 2]
        h = resonator_response(w, w0=w0, q=q)
        return torch.stack([h.real.to(x.dtype), h.imag.to(x.dtype)], dim=-1)
