from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader


@dataclass(frozen=True)
class TrainConfig:
    epochs: int = 5
    lr: float = 1e-3
    batch_size: int = 256
    device: str = "cpu"


@dataclass(frozen=True)
class TrainLog:
    training_time_s: float
    avg_epoch_time_s: float
    losses: List[float]
    optimizer_steps: int


@dataclass(frozen=True)
class TrainLogWithSelection(TrainLog):
    val_mse_history: Optional[List[float]] = None
    best_epoch: Optional[int] = None
    best_val_mse: Optional[float] = None
    restored_best: bool = False


def train_loop(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: Callable[[Any], torch.Tensor],
    *,
    cfg: TrainConfig,
) -> TrainLog:
    model.to(cfg.device)
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=float(cfg.lr))
    losses: List[float] = []
    steps = 0
    t0 = time.perf_counter()
    for _epoch in range(int(cfg.epochs)):
        e0 = time.perf_counter()
        batch_losses: List[float] = []
        for batch in loader:
            steps += 1
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(batch)
            loss.backward()
            opt.step()
            batch_losses.append(float(loss.detach().cpu().item()))
        losses.append(sum(batch_losses) / max(1, len(batch_losses)))
        _ = time.perf_counter() - e0
    t1 = time.perf_counter()
    total = float(t1 - t0)
    return TrainLog(
        training_time_s=total,
        avg_epoch_time_s=(total / max(1, int(cfg.epochs))),
        losses=losses,
        optimizer_steps=steps,
    )


def train_loop_with_selection(
    model: nn.Module,
    train_loader: DataLoader,
    loss_fn: Callable[[Any], torch.Tensor],
    *,
    cfg: TrainConfig,
    val_loader: Optional[DataLoader] = None,
    val_mse_fn: Optional[Callable[[], float]] = None,
    scheduler: str = "cosine",
    eta_min: Optional[float] = None,
    restore_best: bool = True,
) -> TrainLogWithSelection:
    model.to(cfg.device)
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=float(cfg.lr))

    sched = None
    if str(scheduler) == "cosine":
        eta = float(eta_min) if eta_min is not None else min(1e-7, float(cfg.lr) * 0.01)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=int(cfg.epochs), eta_min=float(eta))

    losses: List[float] = []
    val_hist: Optional[List[float]] = [] if (val_loader is not None and val_mse_fn is not None) else None
    steps = 0
    best_val = float("inf")
    best_epoch: Optional[int] = None
    best_state: Optional[Dict[str, torch.Tensor]] = None

    t0 = time.perf_counter()
    for epoch in range(int(cfg.epochs)):
        batch_losses: List[float] = []
        for batch in train_loader:
            steps += 1
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(batch)
            loss.backward()
            opt.step()
            batch_losses.append(float(loss.detach().cpu().item()))
        losses.append(sum(batch_losses) / max(1, len(batch_losses)))

        if val_hist is not None:
            model.eval()
            v = float(val_mse_fn())
            val_hist.append(v)
            model.train()
            if restore_best and v < best_val:
                best_val = v
                best_epoch = int(epoch)
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        if sched is not None:
            sched.step()

    total = float(time.perf_counter() - t0)

    restored = False
    if restore_best and best_state is not None:
        model.load_state_dict(best_state)
        restored = True

    return TrainLogWithSelection(
        training_time_s=total,
        avg_epoch_time_s=(total / max(1, int(cfg.epochs))),
        losses=losses,
        optimizer_steps=steps,
        val_mse_history=val_hist,
        best_epoch=best_epoch,
        best_val_mse=(best_val if best_epoch is not None else None),
        restored_best=restored,
    )


@torch.no_grad()
def evaluate_regression(
    model: nn.Module,
    loader: DataLoader,
    *,
    device: str,
    predict_fn: Callable[[Any], torch.Tensor],
) -> Dict[str, Any]:
    model.eval()
    model.to(device)
    preds: List[List[float]] = []
    targets: List[List[float]] = []
    valid_mask: List[bool] = []
    t0 = time.perf_counter()
    n = 0
    for batch in loader:
        y_pred = predict_fn(batch)
        y_true = batch[1].to(device)
        y_pred_cpu = y_pred.to("cpu")
        y_true_cpu = y_true.to("cpu")
        preds.extend(y_pred_cpu.tolist())
        targets.extend(y_true_cpu.tolist())
        if y_pred_cpu.ndim == 1:
            finite = torch.isfinite(y_pred_cpu)
        else:
            finite = torch.isfinite(y_pred_cpu).all(dim=-1)
        valid_mask.extend([bool(x) for x in finite.tolist()])
        n += int(y_true_cpu.shape[0])
    elapsed = float(time.perf_counter() - t0)
    per_sample_mse: List[float] = []
    per_sample_mae: List[float] = []
    n_valid = 0
    for is_valid, p, t in zip(valid_mask, preds, targets):
        if not bool(is_valid):
            per_sample_mse.append(float("nan"))
            per_sample_mae.append(float("nan"))
            continue
        n_valid += 1
        mse_i = sum((float(pi) - float(ti)) ** 2 for pi, ti in zip(p, t)) / max(1, len(t))
        mae_i = sum(abs(float(pi) - float(ti)) for pi, ti in zip(p, t)) / max(1, len(t))
        per_sample_mse.append(float(mse_i))
        per_sample_mae.append(float(mae_i))
    mse_vals = [v for v in per_sample_mse if math.isfinite(float(v))]
    mae_vals = [v for v in per_sample_mae if math.isfinite(float(v))]
    mse = float(sum(mse_vals) / max(1, len(mse_vals))) if mse_vals else float("inf")
    mae = float(sum(mae_vals) / max(1, len(mae_vals))) if mae_vals else float("inf")
    return {
        "mse": mse,
        "mae": mae,
        "n_samples": int(n),
        "n_valid": int(n_valid),
        "success_rate": (float(n_valid) / float(n)) if n else 0.0,
        "predictions": preds,
        "per_sample_mse": per_sample_mse,
        "inference_time_total_s": elapsed,
        "inference_us_per_sample": (1e6 * elapsed / max(1, n)) if n else None,
    }


@torch.no_grad()
def evaluate_regression_mse(
    model: nn.Module,
    loader: DataLoader,
    *,
    device: str,
    predict_fn: Callable[[Any], torch.Tensor],
) -> float:
    model.eval()
    model.to(device)
    sum_sq = 0.0
    n_valid = 0
    for batch in loader:
        y_pred = predict_fn(batch)
        y_true = batch[1].to(device)
        if y_pred.ndim == 1:
            finite = torch.isfinite(y_pred)
            err = y_pred - y_true.squeeze(-1)
            err = err[finite]
        else:
            finite = torch.isfinite(y_pred).all(dim=-1)
            err = y_pred - y_true
            err = err[finite]
        if err.numel() == 0:
            continue
        sum_sq += float(torch.sum(err * err).detach().cpu().item())
        n_valid += int(err.numel())
    return float(sum_sq / max(1, n_valid)) if n_valid else float("inf")
