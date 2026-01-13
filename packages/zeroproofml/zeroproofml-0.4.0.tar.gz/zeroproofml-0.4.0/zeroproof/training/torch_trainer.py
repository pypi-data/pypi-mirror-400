"""
Minimal PyTorch trainer for TorchTRRational layers.

Trains a TorchTRRational or TorchTRRationalMulti on (x, y) tensors using
standard MSE while leveraging TR autograd ops (Mask‑REAL/SAT/HYBRID).

Logs basic metrics (loss, coverage, non_real_frac, q_min_epoch) and optional
TensorBoard scalars/histograms (|Q|, tags, grad_abs) via ZPTBWriter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

try:  # Optional torch
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    torch = None  # type: ignore
    nn = object  # type: ignore
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    from ..layers.torch_rational import TorchTRRational, TorchTRRationalMulti
    from ..bridge.torch_bridge import from_torch, to_torch
    from ..loggers import ZPTBWriter  # type: ignore

from ..autodiff.grad_mode import GradientMode, GradientModeConfig
from ..utils.seeding import set_global_seed
from .policy_utils import enable_policy_from_model


@dataclass
class TorchTrainingConfig:
    learning_rate: float = 1e-3
    max_epochs: int = 100
    seed: Optional[int] = None
    enable_tensorboard: bool = False
    tb_log_dir: Optional[str] = None
    deterministic: bool = True
    # Optional output JSON dump of final metrics
    output_json: Optional[str] = None
    # Optional dataset checksum for metadata
    dataset_checksum: Optional[str] = None
    # Optional TR policy (guard bands, deterministic reductions)
    enable_tr_policy: bool = False
    policy_ulp_scale: float = 4.0
    policy_deterministic_reduction: bool = True
    # Gradient mode control for torch TR ops
    gradient_mode: str = "mask_real"  # one of: mask_real | saturating | hybrid
    delta: float = 0.0  # local threshold for hybrid (|Q| or |x|)
    gmax: float = 1.0  # saturation bound for SAT/HYBRID


def _tag_stats_from_tr(tr_out) -> Dict[str, float]:
    tags = tr_out.tags
    total = float(tags.numel())
    if total == 0:
        return {"REAL_ratio": 0.0, "PINF_ratio": 0.0, "NINF_ratio": 0.0, "PHI_ratio": 0.0}
    REAL = (tags == 0).sum().item() if hasattr(tags, "sum") else 0
    PINF = (tags == 1).sum().item() if hasattr(tags, "sum") else 0
    NINF = (tags == 2).sum().item() if hasattr(tags, "sum") else 0
    PHI = (tags == 3).sum().item() if hasattr(tags, "sum") else 0
    return {
        "REAL_ratio": float(REAL / total),
        "PINF_ratio": float(PINF / total),
        "NINF_ratio": float(NINF / total),
        "PHI_ratio": float(PHI / total),
        "non_real_frac": float((PINF + NINF + PHI) / total),
    }


def train_torch_rational(
    model: "torch.nn.Module",
    x: "torch.Tensor",
    y: "torch.Tensor",
    config: Optional[TorchTrainingConfig] = None,
) -> Dict[str, float]:
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for train_torch_rational")
    cfg = config or TorchTrainingConfig()

    # Seed and determinism
    if cfg.seed is not None:
        set_global_seed(cfg.seed)
    if cfg.deterministic:
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass

    device = x.device
    model = model.to(device)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.learning_rate)
    writer = (
        ZPTBWriter(cfg.tb_log_dir or "runs/torch_tr", flush_secs=10)
        if cfg.enable_tensorboard and ZPTBWriter is not None
        else None
    )

    # Optional policy setup (guard bands + deterministic reductions)
    try:
        if cfg.enable_tr_policy:
            enable_policy_from_model(
                model,
                ulp_scale=cfg.policy_ulp_scale,
                deterministic_reduction=cfg.policy_deterministic_reduction,
            )
    except Exception:
        pass

    # TB hparams
    if writer is not None:
        try:
            writer.log_hparams(
                {
                    "lr": cfg.learning_rate,
                    "epochs": cfg.max_epochs,
                    "seed": cfg.seed if cfg.seed is not None else -1,
                    "deterministic": int(bool(cfg.deterministic)),
                    "gradient_mode": cfg.gradient_mode,
                    "delta": cfg.delta,
                    "gmax": cfg.gmax,
                }
            )
            # Run metadata (seed, dataset checksum)
            try:
                from ..loggers.tensorboard import RunMeta  # type: ignore

                writer.log_run_metadata(
                    RunMeta(
                        run_dir=(cfg.tb_log_dir or "runs/torch_tr"),
                        seed=cfg.seed,
                        dataset_checksum=cfg.dataset_checksum,
                        policy_flags=None,
                    )
                )
            except Exception:
                pass
        except Exception:
            pass

    for epoch in range(cfg.max_epochs):
        opt.zero_grad()

        # Configure gradient mode for TR ops
        try:
            if cfg.gradient_mode == "saturating":
                GradientModeConfig.set_mode(GradientMode.SATURATING)
                GradientModeConfig.set_saturation_bound(cfg.gmax)
                GradientModeConfig.set_local_threshold(None)
            elif cfg.gradient_mode == "hybrid":
                GradientModeConfig.set_mode(GradientMode.HYBRID)
                GradientModeConfig.set_saturation_bound(cfg.gmax)
                GradientModeConfig.set_local_threshold(cfg.delta if cfg.delta > 0 else None)
            else:
                GradientModeConfig.set_mode(GradientMode.MASK_REAL)
                GradientModeConfig.set_local_threshold(None)
        except Exception:
            pass

        # Forward both TRTensor (for tags/Q) and IEEE values (for loss)
        tr_out = model(x)  # TRTensor
        y_pred = model.forward_values(x)  # torch.Tensor
        loss = torch.nanmean((y_pred - y) ** 2)
        loss.backward()

        # Metrics
        stats = _tag_stats_from_tr(tr_out)
        qmin = None
        try:
            qmin = getattr(model, "get_q_min", lambda: None)()
        except Exception:
            qmin = None

        # Step
        opt.step()

        # Log TB scalars/hists
        if writer is not None:
            scalars = {
                "loss": float(loss.detach().cpu().item()),
                "coverage": float(1.0 - stats.get("non_real_frac", 0.0)),
                "non_real_frac": float(stats.get("non_real_frac", 0.0)),
            }
            if qmin is not None:
                scalars["q_min_epoch"] = float(qmin)
            writer.log_scalars(scalars, step=epoch, prefix="torch")

            # Histograms for tags and |Q| + bucketed MSE
            try:
                # Compute Q via internal helper if available
                if hasattr(model, "_horner_Q"):
                    Q = model._horner_Q(from_torch(x))  # type: ignore[attr-defined]
                    q_torch = torch.abs(to_torch(Q)).detach()
                    writer.log_histogram(
                        "torch/Q_abs", q_torch.flatten().cpu().tolist(), step=epoch
                    )
                    # Bucketed MSE (single or multi-head)
                    edges = [0.0, 1e-5, 1e-4, 1e-3, 1e-2, float("inf")]
                    is_multi = y_pred.dim() >= 2 and y_pred.shape[-1] > 1
                    if is_multi:
                        H = y_pred.shape[-1]
                        for h in range(H):
                            try:
                                tags_h = tr_out.tags[..., h].detach()
                                yph = y_pred.detach()[..., h]
                                yh = (
                                    y.detach()[..., h]
                                    if y.dim() == y_pred.dim()
                                    else y.detach().view(-1)
                                )
                                qh = q_torch
                                if qh.dim() == 2 and qh.shape[-1] == H:
                                    qh = qh[..., h]
                                qh = qh.view(-1)
                                tags_flat = tags_h.view(-1)
                                yph = yph.view(-1)
                                yh = yh.view(-1)
                                real_mask = tags_flat == 0
                                head_scalars = {}
                                for j in range(len(edges) - 1):
                                    lo, hi = edges[j], edges[j + 1]
                                    bin_mask = (qh >= lo) & (qh <= hi) & real_mask
                                    if torch.any(bin_mask):
                                        e = (yph[bin_mask] - yh[bin_mask]) ** 2
                                        mse = torch.mean(e).item()
                                    else:
                                        mse = float("nan")
                                    head_scalars[f"head{h}/B{j}_mse"] = mse
                                head_scalars[f"head{h}/coverage"] = float(
                                    real_mask.float().mean().item()
                                )
                                writer.log_scalars(head_scalars, step=epoch, prefix="torch")
                            except Exception:
                                continue
                    else:
                        try:
                            tags_flat = tr_out.tags.detach().view(-1)
                            ypf = y_pred.detach().view(-1)
                            yf = y.detach().view(-1)
                            qf = q_torch.view(-1)
                            real_mask = tags_flat == 0
                            b_scalars = {}
                            for j in range(len(edges) - 1):
                                lo, hi = edges[j], edges[j + 1]
                                bin_mask = (qf >= lo) & (qf <= hi) & real_mask
                                if torch.any(bin_mask):
                                    e = (ypf[bin_mask] - yf[bin_mask]) ** 2
                                    mse = torch.mean(e).item()
                                else:
                                    mse = float("nan")
                                b_scalars[f"B{j}_mse"] = mse
                            writer.log_scalars(b_scalars, step=epoch, prefix="torch")
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                writer.log_histogram(
                    "torch/tags", tr_out.tags.detach().flatten().cpu().tolist(), step=epoch, bins=4
                )
            except Exception:
                pass

    # Final metrics
    final = {
        "loss": float(loss.detach().cpu().item()),
        "coverage": float(1.0 - stats.get("non_real_frac", 0.0)),
        "non_real_frac": float(stats.get("non_real_frac", 0.0)),
    }
    if qmin is not None:
        final["q_min_epoch"] = float(qmin)
    # Per-bucket MSE summary for single-head or averaged across heads
    try:
        if hasattr(model, "_horner_Q"):
            edges = [0.0, 1e-5, 1e-4, 1e-3, 1e-2, float("inf")]
            Q = model._horner_Q(from_torch(x))  # type: ignore[attr-defined]
            q = torch.abs(to_torch(Q)).detach()
            y_pred_final = model.forward_values(x).detach()
            y_true = y.detach()
            # Flatten shapes; support optional head dim
            if y_pred_final.dim() >= 2 and y_pred_final.shape[-1] > 1:
                # Average per-bucket across heads
                H = y_pred_final.shape[-1]
                mse_buckets = {f"B{j}_mse": 0.0 for j in range(len(edges) - 1)}
                cnt_buckets = {f"B{j}_count": 0.0 for j in range(len(edges) - 1)}
                for h in range(H):
                    qh = q
                    if qh.dim() == 2 and qh.shape[-1] == H:
                        qh = qh[..., h]
                    qf = qh.view(-1)
                    ypf = y_pred_final[..., h].view(-1)
                    yf = (
                        y_true[..., h] if y_true.dim() == y_pred_final.dim() else y_true.view(-1)
                    ).view(-1)
                    # Use tags if available
                    real_mask = (
                        (tr_out.tags[..., h].detach().view(-1) == 0)
                        if hasattr(tr_out, "tags")
                        else torch.isfinite(ypf)
                    )
                    for j in range(len(edges) - 1):
                        lo, hi = edges[j], edges[j + 1]
                        mask = (qf >= lo) & (qf <= hi) & real_mask
                        key_m = f"B{j}_mse"
                        key_c = f"B{j}_count"
                        if torch.any(mask):
                            e = (ypf[mask] - yf[mask]) ** 2
                            mse = torch.mean(e).item()
                            cnt = float(mask.sum().item())
                            # Running average weighted by counts
                            prev_cnt = cnt_buckets[key_c]
                            prev_mse = mse_buckets[key_m]
                            total = prev_cnt + cnt
                            mse_buckets[key_m] = (prev_mse * prev_cnt + mse * cnt) / max(
                                total, 1e-12
                            )
                            cnt_buckets[key_c] = total
                final.update(mse_buckets)
                final.update(cnt_buckets)
            else:
                qf = q.view(-1)
                ypf = y_pred_final.view(-1)
                yf = y_true.view(-1)
                real_mask = (
                    (tr_out.tags.detach().view(-1) == 0)
                    if hasattr(tr_out, "tags")
                    else torch.isfinite(ypf)
                )
                for j in range(len(edges) - 1):
                    lo, hi = edges[j], edges[j + 1]
                    mask = (qf >= lo) & (qf <= hi) & real_mask
                    if torch.any(mask):
                        e = (ypf[mask] - yf[mask]) ** 2
                        final[f"B{j}_mse"] = float(torch.mean(e).item())
                        final[f"B{j}_count"] = float(mask.sum().item())
                    else:
                        final[f"B{j}_mse"] = float("nan")
                        final[f"B{j}_count"] = 0.0
    except Exception:
        pass
    if writer is not None:
        try:
            writer.flush()
            writer.close()
        except Exception:
            pass
    # Optional JSON export
    try:
        if cfg.output_json:
            import json

            with open(cfg.output_json, "w", encoding="utf-8") as f:
                json.dump(final, f, indent=2)
    except Exception:
        pass
    return final
