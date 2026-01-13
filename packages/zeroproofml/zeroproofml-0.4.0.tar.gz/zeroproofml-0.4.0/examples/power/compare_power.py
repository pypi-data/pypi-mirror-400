from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.sampler import WeightedRandomSampler

from examples.power.models import (
    PowerMLP,
    PowerMLPConfig,
    PowerMLPMultiTask,
    PowerMLPWithPoleHead,
    PowerMLPWithMultiPoleHead,
    PowerProjectivePQ,
    PowerProjectivePQConfig,
    PowerProjectivePQMultiTask,
)
from examples.power.power_dataset import dataset_info_dict, flatten_xy, load_power_dataset
from examples.torch_baselines.trainer import TrainConfig, evaluate_regression, train_loop
from zeroproofml.experiment_protocol import protocol_v1
from zeroproofml.benchmark import TorchMicrobenchConfig, torch_microbench
from zeroproofml.binary_metrics import binary_summary
from zeroproofml.resources import collect_system_info, peak_rss_mb, torch_cuda_peak_mb


def _set_seed(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(int(seed))
    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))


def _bucket_key(edges: List[float], i: int) -> str:
    lo = edges[i]
    hi = edges[i + 1]
    lo_s = f"{lo:.0e}" if math.isfinite(lo) else "inf"
    hi_s = f"{hi:.0e}" if math.isfinite(hi) else "inf"
    return f"({lo_s},{hi_s}]"


def _bucketize_delta(delta: float, edges: List[float]) -> int:
    for b in range(len(edges) - 1):
        lo, hi = float(edges[b]), float(edges[b + 1])
        if (delta >= lo if b == 0 else delta > lo) and delta <= hi:
            return b
    return len(edges) - 2


def _bucket_mse(per_sample_mse: List[float], delta_lambdas: List[float], edges: List[float]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    per_bucket: Dict[str, List[float]] = {_bucket_key(edges, i): [] for i in range(len(edges) - 1)}
    counts: Dict[str, int] = {_bucket_key(edges, i): 0 for i in range(len(edges) - 1)}
    for mse, d in zip(per_sample_mse, delta_lambdas):
        b = _bucketize_delta(float(d), edges)
        k = _bucket_key(edges, b)
        counts[k] += 1
        if isinstance(mse, (int, float)) and math.isfinite(float(mse)):
            per_bucket[k].append(float(mse))
    bucket_mse: Dict[str, Any] = {}
    for k, vals in per_bucket.items():
        bucket_mse[k] = (sum(vals) / len(vals)) if vals else None
    return bucket_mse, counts


def _to_builtin(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _to_builtin(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_to_builtin(v) for v in x]
    if isinstance(x, tuple):
        return [_to_builtin(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    try:
        return float(x)
    except Exception:
        return str(x)


def _infer_device(req: str) -> str:
    if req == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if req == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return req


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Torch-first power suite comparator (Phase 13 scaffold)")
    ap.add_argument("--dataset", required=True, help="Path to power dataset JSON")
    ap.add_argument("--output_dir", required=True, help="Output directory")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument(
        "--task",
        choices=["regression", "near_collapse_cls"],
        default="near_collapse_cls",
        help="Training mode. near_collapse_cls trains explicit classifier heads (optionally with regression auxiliary).",
    )
    ap.add_argument(
        "--target",
        choices=["vmin", "delta_lambda", "dvmin_dlambda"],
        default="delta_lambda",
        help="Regression target to learn from the dataset.",
    )
    ap.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Subset: mlp mlp_pole rational_eps smooth learnable_eps eps_ens",
    )
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch_size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--hidden_dims", nargs="*", type=int, default=[64, 64])
    ap.add_argument("--eps", type=float, default=1e-2, help="Fixed epsilon for Rational+ε")
    ap.add_argument("--alpha", type=float, default=1e-1, help="Fixed alpha for Smooth")
    ap.add_argument("--ens_eps", nargs="*", type=float, default=[1e-4, 1e-3, 1e-2], help="EpsEnsemble eps list")
    ap.add_argument(
        "--delta_reweight_alpha",
        type=float,
        default=0.0,
        help="If >0, upweight small-Δλ samples in regression loss via w=1+alpha*exp(-Δλ/tau).",
    )
    ap.add_argument(
        "--delta_reweight_tau",
        type=float,
        default=None,
        help="Δλ scale for reweighting (default: pole_delta_threshold).",
    )
    ap.add_argument(
        "--lambda_mono",
        type=float,
        default=0.0,
        help="Monotonicity regularizer weight (penalize increases vs λ within scenarios; targets vmin/delta_lambda only).",
    )
    ap.add_argument("--lambda_pole", type=float, default=0.1, help="Pole head loss weight (Power MLP+PoleHead)")
    ap.add_argument(
        "--pole_delta_threshold",
        type=float,
        default=0.01,
        help="Near-collapse threshold for pole head label (delta_lambda <= threshold).",
    )
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    ap.add_argument("--no-microbench", action="store_true", help="Skip microbenchmark timing tiers")
    ap.add_argument("--microbench-iters", type=int, default=120)
    ap.add_argument("--microbench-warmup", type=int, default=30)
    ap.add_argument(
        "--collapse_deltas",
        nargs="*",
        type=float,
        default=[1e-2, 5e-2, 2e-1],
        help="Δλ thresholds for near-collapse classification heads/metrics (positive if Δλ <= threshold).",
    )
    ap.add_argument(
        "--cls_fpr_budget",
        type=float,
        default=0.05,
        help="FPR budget for reporting FNR@FPR on near-collapse classification.",
    )
    ap.add_argument(
        "--cls_invalid_policy",
        choices=["positive", "negative", "ignore"],
        default="positive",
        help="How to treat non-finite Δλ predictions when computing classification scores (default: safety-conservative).",
    )
    ap.add_argument(
        "--lambda_cls",
        type=float,
        default=1.0,
        help="Classifier loss weight for near-collapse heads (only used for --task near_collapse_cls).",
    )
    ap.add_argument(
        "--lambda_reg_aux",
        type=float,
        default=1.0,
        help="Auxiliary regression MSE weight when training classification (only used for --task near_collapse_cls).",
    )
    ap.add_argument("--cls_loss", choices=["bce", "focal"], default="bce", help="Loss for near-collapse heads.")
    ap.add_argument("--cls_focal_gamma", type=float, default=2.0, help="Focal loss gamma (when --cls_loss=focal).")
    ap.add_argument(
        "--cls_pos_weight",
        nargs="*",
        type=float,
        default=None,
        help="Optional per-threshold positive class weights for BCEWithLogits (len=K or len=1 to broadcast).",
    )
    ap.add_argument(
        "--cls_pos_weight_auto",
        action="store_true",
        help="Auto-compute per-threshold pos_weight from the TRAIN split (neg/pos), clamped by --cls_pos_weight_max.",
    )
    ap.add_argument("--cls_pos_weight_max", type=float, default=100.0)
    ap.add_argument(
        "--cls_thr_weights",
        nargs="*",
        type=float,
        default=None,
        help="Optional per-threshold loss weights (len=K or len=1 to broadcast).",
    )
    ap.add_argument(
        "--cls_oversample",
        action="store_true",
        help="Oversample near-collapse positives (for the smallest Δλ threshold) via WeightedRandomSampler.",
    )
    ap.add_argument(
        "--cls_oversample_pos_mult",
        type=float,
        default=5.0,
        help="Positive sample weight multiplier for --cls_oversample.",
    )
    ap.add_argument(
        "--cls_oversample_threshold",
        type=float,
        default=None,
        help="Override the Δλ threshold used for oversampling positives (default: min(--collapse_deltas)).",
    )
    args = ap.parse_args(argv)

    os.makedirs(args.output_dir, exist_ok=True)
    device = _infer_device(str(args.device))
    _set_seed(args.seed)

    enabled = set(args.models or ["mlp", "mlp_pole", "rational_eps", "smooth", "learnable_eps", "eps_ens"])

    data = load_power_dataset(args.dataset)
    info, x, y, delta, _bucket, train_idx, test_idx, holdout_idx, scenario_ids, lambda_vals = flatten_xy(
        data, dataset_path=str(args.dataset), target=str(args.target)
    )
    edges = info.delta_lambda_bucket_edges or [0.0, 0.01, 0.05, 0.2, float("inf")]
    input_dim = int(info.input_dim)
    x_t = torch.tensor(x, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
    delta_t = torch.tensor([float(v) for v in delta], dtype=torch.float32).unsqueeze(-1)
    scenario_t = torch.tensor([int(v) for v in scenario_ids], dtype=torch.int64).unsqueeze(-1)
    lambda_t = torch.tensor([float(v) for v in lambda_vals], dtype=torch.float32).unsqueeze(-1)

    x_train = x_t[train_idx]
    y_train = y_t[train_idx]
    d_train_t = delta_t[train_idx]
    s_train_t = scenario_t[train_idx]
    l_train_t = lambda_t[train_idx]
    x_test = x_t[test_idx]
    y_test = y_t[test_idx]
    d_test_t = delta_t[test_idx]
    s_test_t = scenario_t[test_idx]
    l_test_t = lambda_t[test_idx]
    x_holdout = x_t[holdout_idx] if holdout_idx else None
    y_holdout = y_t[holdout_idx] if holdout_idx else None
    d_holdout_t = delta_t[holdout_idx] if holdout_idx else None
    s_holdout_t = scenario_t[holdout_idx] if holdout_idx else None
    l_holdout_t = lambda_t[holdout_idx] if holdout_idx else None
    delta_test = [float(delta[i]) for i in test_idx]
    delta_train = [float(delta[i]) for i in train_idx]
    delta_holdout = [float(delta[i]) for i in holdout_idx] if holdout_idx else []
    scenario_test = [int(scenario_ids[i]) for i in test_idx]
    lambda_test = [float(lambda_vals[i]) for i in test_idx]

    train_ds = TensorDataset(x_train, y_train, d_train_t, s_train_t, l_train_t)
    cls_thresholds_for_sampling = [float(x) for x in args.collapse_deltas]
    sampler = None
    shuffle = True
    if bool(args.cls_oversample) and bool(str(args.task) == "near_collapse_cls") and cls_thresholds_for_sampling:
        thr = (
            float(args.cls_oversample_threshold)
            if args.cls_oversample_threshold is not None
            else float(min(cls_thresholds_for_sampling))
        )
        pos = (d_train_t.squeeze(-1) <= thr).to(torch.bool)
        weights = torch.ones(int(pos.shape[0]), dtype=torch.double)
        weights[pos.cpu()] = float(args.cls_oversample_pos_mult)
        sampler = WeightedRandomSampler(weights=weights, num_samples=int(weights.shape[0]), replacement=True)
        shuffle = False

    train_loader = DataLoader(
        train_ds,
        batch_size=int(args.batch_size),
        shuffle=shuffle,
        sampler=sampler,
    )
    train_eval_loader = DataLoader(
        train_ds,
        batch_size=int(args.batch_size),
        shuffle=False,
    )
    test_loader = DataLoader(
        TensorDataset(x_test, y_test, d_test_t, s_test_t, l_test_t),
        batch_size=int(args.batch_size),
        shuffle=False,
    )
    holdout_loader = None
    if x_holdout is not None and y_holdout is not None and int(info.n_holdout) > 0:
        holdout_loader = DataLoader(
            TensorDataset(
                x_holdout,
                y_holdout,
                d_holdout_t,
                s_holdout_t,
                l_holdout_t,
            ),
            batch_size=int(args.batch_size),
            shuffle=False,
        )

    comp: Dict[str, Any] = {
        "protocol": protocol_v1(domain="power_ieee14", suite_name="paper_suite_power"),
        "resources": {"system": collect_system_info()},
        "dataset_info": {
            **dataset_info_dict(info),
            "train_indices": train_idx,
            "test_indices": test_idx,
            "holdout_indices": holdout_idx,
        },
        "individual_results": {},
        "comparison_table": [],
        "summary": {},
    }

    individual: Dict[str, Any] = comp["individual_results"]
    table: List[Dict[str, Any]] = comp["comparison_table"]

    x_bench = x_test.to(device)

    def maybe_microbench(*, predict_fn, label: str) -> Optional[Dict[str, Any]]:
        if bool(args.no_microbench):
            return None
        try:
            return torch_microbench(
                predict_fn=predict_fn,
                example_batch=x_bench,
                cfg=TorchMicrobenchConfig(
                    batch_sizes=(1, int(args.batch_size)),
                    warmup_iters=int(args.microbench_warmup),
                    iters=int(args.microbench_iters),
                    device=str(device),
                    label=str(label),
                ),
            )
        except Exception:
            return None

    def micro_us_per_sample(bench: Optional[Dict[str, Any]], bs: int) -> Any:
        if not isinstance(bench, dict):
            return None
        batches = bench.get("batches")
        if not isinstance(batches, dict):
            return None
        b = batches.get(str(int(bs)))
        if not isinstance(b, dict):
            return None
        return b.get("mean_us_per_sample")

    delta_reweight_tau = float(args.delta_reweight_tau) if args.delta_reweight_tau is not None else float(args.pole_delta_threshold)

    def sample_weights(delta_batch: torch.Tensor) -> torch.Tensor:
        if float(args.delta_reweight_alpha) <= 0.0:
            return torch.ones_like(delta_batch)
        tau = max(1e-12, float(delta_reweight_tau))
        return 1.0 + float(args.delta_reweight_alpha) * torch.exp(-delta_batch / tau)

    def weighted_mse(pred: torch.Tensor, yb: torch.Tensor, db: torch.Tensor) -> torch.Tensor:
        w = sample_weights(db)
        return torch.mean(w * (pred - yb) ** 2)

    def mono_penalty(pred: torch.Tensor, scen: torch.Tensor, lam: torch.Tensor) -> torch.Tensor:
        if float(args.lambda_mono) <= 0.0 or str(args.target) not in ("vmin", "delta_lambda"):
            return torch.zeros((), device=pred.device, dtype=pred.dtype)
        sid = scen.squeeze(-1)
        lam1 = lam.squeeze(-1)
        p = pred.squeeze(-1)
        uniq = torch.unique(sid)
        penalties: List[torch.Tensor] = []
        for u in uniq:
            mask = sid == u
            if int(mask.sum().item()) < 2:
                continue
            lams = lam1[mask]
            ps = p[mask]
            order = torch.argsort(lams)
            diffs = ps[order][1:] - ps[order][:-1]
            penalties.append(torch.relu(diffs))
        if not penalties:
            return torch.zeros((), device=pred.device, dtype=pred.dtype)
        return torch.mean(torch.cat(penalties, dim=0))

    cls_enabled = str(args.task) == "near_collapse_cls"
    cls_thresholds = [float(x) for x in args.collapse_deltas]

    def _broadcast_list(xs: Optional[List[float]], *, k: int, name: str) -> Optional[List[float]]:
        if xs is None:
            return None
        vals = [float(x) for x in xs]
        if not vals:
            return None
        if len(vals) == 1 and k > 1:
            return [float(vals[0])] * int(k)
        if len(vals) != int(k):
            raise ValueError(f"{name} must have len=1 or len={k}; got {len(vals)}")
        return vals

    k_cls = int(len(cls_thresholds))
    cls_thr_weights = _broadcast_list(args.cls_thr_weights, k=k_cls, name="--cls_thr_weights") or [1.0] * k_cls
    cls_pos_weight_vals = _broadcast_list(args.cls_pos_weight, k=k_cls, name="--cls_pos_weight")
    if cls_pos_weight_vals is None and bool(args.cls_pos_weight_auto) and k_cls:
        with torch.no_grad():
            thr_t = torch.tensor(cls_thresholds, dtype=torch.float32).view(1, -1)
            t = (d_train_t.squeeze(-1).unsqueeze(-1) <= thr_t).to(torch.float32)
            pos = t.sum(dim=0)
            neg = float(t.shape[0]) - pos
            out: List[float] = []
            for p, n in zip(pos.tolist(), neg.tolist()):
                if float(p) <= 0.0:
                    out.append(1.0)
                else:
                    out.append(float(min(float(args.cls_pos_weight_max), max(1.0, float(n) / float(p)))))
            cls_pos_weight_vals = out

    cls_thr_weights_t = (
        torch.tensor(cls_thr_weights, dtype=torch.float32, device=device).view(1, -1) if k_cls else None
    )
    cls_pos_weight_t = torch.tensor(cls_pos_weight_vals, dtype=torch.float32, device=device) if cls_pos_weight_vals else None

    def cls_targets(delta_batch: torch.Tensor) -> torch.Tensor:
        db = delta_batch.squeeze(-1)
        cols = [(db <= float(thr)).float() for thr in cls_thresholds]
        if not cols:
            return torch.zeros((db.shape[0], 0), device=db.device, dtype=db.dtype)
        return torch.stack(cols, dim=-1)

    def cls_loss(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        if logits.numel() == 0:
            return torch.zeros((), device=logits.device, dtype=logits.dtype)
        per = F.binary_cross_entropy_with_logits(
            logits,
            targets,
            pos_weight=(cls_pos_weight_t.to(logits.device) if cls_pos_weight_t is not None else None),
            reduction="none",
        )
        if str(args.cls_loss) == "focal":
            gamma = float(args.cls_focal_gamma)
            p = torch.sigmoid(logits)
            p_t = p * targets + (1.0 - p) * (1.0 - targets)
            per = per * (torch.clamp_min(1.0 - p_t, 0.0) ** gamma)
        if cls_thr_weights_t is not None:
            per = per * cls_thr_weights_t.to(logits.device)
        return torch.mean(per)

    cls_oversample_threshold_effective = (
        float(args.cls_oversample_threshold)
        if args.cls_oversample_threshold is not None
        else (float(min(cls_thresholds)) if cls_thresholds else None)
    )
    cls_config_record: Dict[str, Any] = {
        "cls_loss": str(args.cls_loss),
        "cls_focal_gamma": float(args.cls_focal_gamma),
        "cls_pos_weight": (None if cls_pos_weight_vals is None else [float(x) for x in cls_pos_weight_vals]),
        "cls_pos_weight_auto": bool(args.cls_pos_weight_auto),
        "cls_pos_weight_max": float(args.cls_pos_weight_max),
        "cls_thr_weights": [float(x) for x in cls_thr_weights],
        "cls_oversample": bool(args.cls_oversample),
        "cls_oversample_pos_mult": float(args.cls_oversample_pos_mult),
        "cls_oversample_threshold": cls_oversample_threshold_effective,
    }

    def add_row(
        *,
        method: str,
        params: int,
        epochs: int,
        train_mse: float,
        test_mse: float,
        training_time: float,
        avg_epoch_time: float,
        success_rate: float,
        inference_us_per_sample: Any,
        notes: str,
        bucket_counts: Dict[str, int],
        micro_us_per_sample_b1: Any = None,
        micro_us_per_sample_bN: Any = None,
    ) -> None:
        # Keep the column names aligned with the robotics suite CSV.
        table.append(
            {
                "Method": method,
                "Parameters": int(params),
                "Epochs": int(epochs),
                "Train_MSE": float(train_mse),
                "Test_MSE": float(test_mse),
                "Training_Time": float(training_time),
                "Avg_Epoch_Time": float(avg_epoch_time),
                "Success_Rate": float(success_rate),
                "Inference_us_per_sample": inference_us_per_sample,
                "Micro_us_per_sample_b1": micro_us_per_sample_b1,
                f"Micro_us_per_sample_b{int(args.batch_size)}": micro_us_per_sample_bN,
                "Notes": str(notes),
                "BucketCounts": bucket_counts,
            }
        )

    def near_collapse_band(per_sample_mse: List[float], delta_vals: List[float], *, thr: float) -> Dict[str, Any]:
        sel = [float(m) for m, d in zip(per_sample_mse, delta_vals) if float(d) <= float(thr) and math.isfinite(float(m))]
        if not sel:
            return {"threshold": float(thr), "mse": None, "n": 0}
        return {"threshold": float(thr), "mse": float(sum(sel) / len(sel)), "n": int(len(sel))}

    def monotonicity_violation_rate(
        preds: List[float], scen: List[int], lambdas: List[float]
    ) -> Dict[str, Any]:
        by: Dict[int, List[Tuple[float, float]]] = {}
        for p, sid, lam in zip(preds, scen, lambdas):
            if not (isinstance(p, (int, float)) and math.isfinite(float(p))):
                continue
            by.setdefault(int(sid), []).append((float(lam), float(p)))
        total_pairs = 0
        violations = 0
        for _sid, pts in by.items():
            pts.sort(key=lambda t: t[0])
            for i in range(1, len(pts)):
                total_pairs += 1
                # Expect target to be non-increasing as lambda increases (vmin, delta_lambda).
                if pts[i][1] > pts[i - 1][1] + 1e-6:
                    violations += 1
        return {
            "n_scenarios": int(len(by)),
            "n_pairs": int(total_pairs),
            "violation_rate": (float(violations) / float(total_pairs)) if total_pairs else None,
        }

    def lambda_star_metrics_from_delta(
        pred_delta: List[float],
        *,
        lambda_vals: List[float],
        delta_true: List[float],
        scenario_ids: List[int],
    ) -> Dict[str, Any]:
        lam_star_true: List[float] = []
        lam_star_pred: List[float] = []
        for pd, lam, dt in zip(pred_delta, lambda_vals, delta_true):
            if not (
                isinstance(pd, (int, float))
                and math.isfinite(float(pd))
                and isinstance(lam, (int, float))
                and math.isfinite(float(lam))
                and isinstance(dt, (int, float))
                and math.isfinite(float(dt))
            ):
                continue
            lam_star_true.append(float(lam) + float(dt))
            lam_star_pred.append(float(lam) + float(pd))

        per_err2 = [(p - t) ** 2 for p, t in zip(lam_star_pred, lam_star_true)]
        mse = (sum(per_err2) / len(per_err2)) if per_err2 else None
        rmse = (math.sqrt(float(mse)) if isinstance(mse, (int, float)) and math.isfinite(float(mse)) else None)

        by: Dict[int, List[Tuple[float, float]]] = {}
        for pd, lam, dt, sid in zip(pred_delta, lambda_vals, delta_true, scenario_ids):
            if not (
                isinstance(pd, (int, float))
                and math.isfinite(float(pd))
                and isinstance(lam, (int, float))
                and math.isfinite(float(lam))
                and isinstance(dt, (int, float))
                and math.isfinite(float(dt))
            ):
                continue
            by.setdefault(int(sid), []).append((float(lam) + float(pd), float(lam) + float(dt)))

        scenario_err2: List[float] = []
        scenario_abs: List[float] = []
        for _sid, pts in by.items():
            if not pts:
                continue
            pred_mean = sum(p for p, _t in pts) / len(pts)
            true_mean = sum(t for _p, t in pts) / len(pts)
            err = pred_mean - true_mean
            scenario_err2.append(err * err)
            scenario_abs.append(abs(err))

        scen_rmse = (math.sqrt(sum(scenario_err2) / len(scenario_err2)) if scenario_err2 else None)
        scen_mae = (sum(scenario_abs) / len(scenario_abs)) if scenario_abs else None

        return {
            "n_samples_valid": int(len(per_err2)),
            "lambda_star_mse": (float(mse) if mse is not None else None),
            "lambda_star_rmse": (float(rmse) if rmse is not None else None),
            "n_scenarios_valid": int(len(by)),
            "lambda_star_scenario_rmse": (float(scen_rmse) if scen_rmse is not None else None),
            "lambda_star_scenario_mae": (float(scen_mae) if scen_mae is not None else None),
        }

    def near_collapse_classification_from_logits(
        logits: List[List[float]],
        *,
        delta_true: List[float],
        thresholds: List[float],
        fpr_budget: float,
        invalid_policy: str,
    ) -> Dict[str, Any]:
        per_delta: Dict[str, Any] = {}
        invalid_total = 0
        for k, thr in enumerate(thresholds):
            scores: List[float] = []
            invalid = 0
            for row in logits:
                v = None
                if isinstance(row, list) and k < len(row) and isinstance(row[k], (int, float)) and math.isfinite(float(row[k])):
                    v = float(row[k])
                if v is None:
                    invalid += 1
                    if invalid_policy == "positive":
                        scores.append(float("inf"))
                    elif invalid_policy == "negative":
                        scores.append(float("-inf"))
                    else:
                        scores.append(float("nan"))
                else:
                    scores.append(float(v))
            invalid_total += invalid
            y_true = [1 if float(d) <= float(thr) else 0 for d in delta_true]
            per_delta[f"{float(thr):.0e}"] = binary_summary(y_true, scores, fpr_budget=float(fpr_budget))
        return {
            "thresholds": [float(t) for t in thresholds],
            "fpr_budget": float(fpr_budget),
            "invalid_policy": str(invalid_policy),
            "n_invalid_logit_total": int(invalid_total),
            "per_delta": per_delta,
        }

    def evaluate_classification(
        model,
        loader: DataLoader,
        *,
        predict_logits_fn,
    ) -> Dict[str, Any]:
        model.eval()
        logits_out: List[List[float]] = []
        t0 = time.perf_counter()
        with torch.no_grad():
            for batch in loader:
                logits = predict_logits_fn(batch)
                logits = logits.detach().cpu()
                for i in range(int(logits.shape[0])):
                    logits_out.append([float(v) for v in logits[i].view(-1).tolist()])
        t1 = time.perf_counter()
        n = len(logits_out)
        elapsed = float(t1 - t0)
        return {
            "cls_n_samples": int(n),
            "cls_inference_time_total_s": elapsed,
            "cls_inference_us_per_sample": (1e6 * elapsed / max(1, n)) if n else None,
            "cls_logits": logits_out,
            "cls_thresholds": [float(x) for x in args.collapse_deltas],
        }

    def eval_holdout_if_present(
        model,
        *,
        predict,
    ) -> Optional[Dict[str, Any]]:
        if holdout_loader is None:
            return None
        tm = evaluate_regression(model, holdout_loader, device=device, predict_fn=predict)
        return {
            "mse": tm.get("mse"),
            "n_samples": tm.get("n_samples"),
            "inference_us_per_sample": tm.get("inference_us_per_sample"),
        }

    # 1) MLP baseline
    if "mlp" in enabled:
        model = PowerMLPMultiTask(
            PowerMLPConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims)),
            n_classes=len(cls_thresholds),
        )
        train_cfg = TrainConfig(
            epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device
        )

        def loss_fn(batch):
            xb, yb, db, sb, lb = (
                batch[0].to(device),
                batch[1].to(device),
                batch[2].to(device),
                batch[3].to(device),
                batch[4].to(device),
            )
            pred, logits = model(xb)
            mse = weighted_mse(pred, yb, db)
            mono = mono_penalty(pred, sb, lb)
            loss = (float(args.lambda_reg_aux) * mse if cls_enabled else mse) + float(args.lambda_mono) * mono
            if cls_enabled:
                loss = loss + float(args.lambda_cls) * cls_loss(logits, cls_targets(db))
            return loss

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: model(xb)[0], label="power_mlp_forward")

        def pred_reg(batch):
            return model(batch[0].to(device))[0]

        def pred_logits(batch):
            return model(batch[0].to(device))[1]

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_reg)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_reg)
        holdout_metrics = eval_holdout_if_present(model, predict=pred_reg)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], delta_test, edges)
        band = near_collapse_band(test_metrics["per_sample_mse"], delta_test, thr=float(args.pole_delta_threshold))
        shape = (
            monotonicity_violation_rate([float(p[0]) for p in test_metrics["predictions"]], scenario_test, lambda_test)
            if str(args.target) in ("vmin", "delta_lambda")
            else None
        )
        lambda_star_metrics = (
            lambda_star_metrics_from_delta(
                [float(p[0]) for p in test_metrics["predictions"]],
                lambda_vals=lambda_test,
                delta_true=delta_test,
                scenario_ids=scenario_test,
            )
            if str(args.target) == "delta_lambda"
            else None
        )
        cls_tm = evaluate_classification(model, test_loader, predict_logits_fn=pred_logits) if cls_enabled else None
        if isinstance(cls_tm, dict):
            test_metrics = {**test_metrics, **cls_tm}
        near_collapse_cls = (
            near_collapse_classification_from_logits(
                (cls_tm or {}).get("cls_logits", []),
                delta_true=delta_test,
                thresholds=cls_thresholds,
                fpr_budget=float(args.cls_fpr_budget),
                invalid_policy=str(args.cls_invalid_policy),
            )
            if cls_enabled and isinstance(cls_tm, dict)
            else None
        )
        res = {
            "model_type": "PowerMLP",
            "config": {
                "task": str(args.task),
                "target": str(args.target),
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "delta_reweight_alpha": float(args.delta_reweight_alpha),
                "delta_reweight_tau": float(delta_reweight_tau),
                "lambda_mono": float(args.lambda_mono),
                "collapse_deltas": cls_thresholds,
                "cls_fpr_budget": float(args.cls_fpr_budget),
                "cls_invalid_policy": str(args.cls_invalid_policy),
                "lambda_cls": float(args.lambda_cls),
                "lambda_reg_aux": float(args.lambda_reg_aux),
                **cls_config_record,
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "near_collapse_band": band,
            "shape_metrics": shape,
            "lambda_star_metrics": lambda_star_metrics,
            "near_collapse_classification": near_collapse_cls,
            "holdout_metrics": holdout_metrics,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["MLP"] = _to_builtin(res)
        add_row(
            method="MLP",
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(log.training_time_s),
            avg_epoch_time=float(log.avg_epoch_time_s),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"hidden={list(args.hidden_dims)} target={str(args.target)}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # 1b) MLP+PoleHead baseline (safety-aware ablation for near-collapse)
    if "mlp_pole" in enabled:
        model = PowerMLPWithMultiPoleHead(
            PowerMLPConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims)),
            n_poles=len(cls_thresholds),
        )
        train_cfg = TrainConfig(
            epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device
        )

        def loss_fn(batch):
            xb, yb, db, sb, lb = (
                batch[0].to(device),
                batch[1].to(device),
                batch[2].to(device),
                batch[3].to(device),
                batch[4].to(device),
            )
            pred, pole_logit = model(xb)
            mse = weighted_mse(pred, yb, db)
            mono = mono_penalty(pred, sb, lb)
            pole = cls_loss(pole_logit, cls_targets(db))
            loss = (float(args.lambda_reg_aux) * mse if cls_enabled else mse) + float(args.lambda_mono) * mono
            loss = loss + float(args.lambda_pole) * pole
            return loss

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: model(xb)[0], label="power_mlp_pole_forward")

        def pred_reg(batch):
            return model(batch[0].to(device))[0]

        def pred_logits(batch):
            return model(batch[0].to(device))[1]

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_reg)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_reg)
        holdout_metrics = eval_holdout_if_present(model, predict=pred_reg)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], delta_test, edges)
        band = near_collapse_band(test_metrics["per_sample_mse"], delta_test, thr=float(args.pole_delta_threshold))
        shape = (
            monotonicity_violation_rate([float(p[0]) for p in test_metrics["predictions"]], scenario_test, lambda_test)
            if str(args.target) in ("vmin", "delta_lambda")
            else None
        )
        lambda_star_metrics = (
            lambda_star_metrics_from_delta(
                [float(p[0]) for p in test_metrics["predictions"]],
                lambda_vals=lambda_test,
                delta_true=delta_test,
                scenario_ids=scenario_test,
            )
            if str(args.target) == "delta_lambda"
            else None
        )
        cls_tm = evaluate_classification(model, test_loader, predict_logits_fn=pred_logits) if cls_enabled else None
        if isinstance(cls_tm, dict):
            test_metrics = {**test_metrics, **cls_tm}
        near_collapse_cls = (
            near_collapse_classification_from_logits(
                (cls_tm or {}).get("cls_logits", []),
                delta_true=delta_test,
                thresholds=cls_thresholds,
                fpr_budget=float(args.cls_fpr_budget),
                invalid_policy=str(args.cls_invalid_policy),
            )
            if cls_enabled and isinstance(cls_tm, dict)
            else None
        )
        res = {
            "model_type": "PowerMLP+PoleHead",
            "config": {
                "task": str(args.task),
                "target": str(args.target),
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "pole_delta_threshold": float(args.pole_delta_threshold),
                "lambda_pole": float(args.lambda_pole),
                "delta_reweight_alpha": float(args.delta_reweight_alpha),
                "delta_reweight_tau": float(delta_reweight_tau),
                "lambda_mono": float(args.lambda_mono),
                "collapse_deltas": cls_thresholds,
                "cls_fpr_budget": float(args.cls_fpr_budget),
                "cls_invalid_policy": str(args.cls_invalid_policy),
                "lambda_cls": float(args.lambda_cls),
                "lambda_reg_aux": float(args.lambda_reg_aux),
                **cls_config_record,
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "near_collapse_band": band,
            "shape_metrics": shape,
            "lambda_star_metrics": lambda_star_metrics,
            "near_collapse_classification": near_collapse_cls,
            "holdout_metrics": holdout_metrics,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["MLP+PoleHead"] = _to_builtin(res)
        add_row(
            method="MLP+PoleHead",
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(log.training_time_s),
            avg_epoch_time=float(log.avg_epoch_time_s),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"hidden={list(args.hidden_dims)} target={str(args.target)} pole_head=on thr={float(args.pole_delta_threshold):.2e}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    def train_projective_decoded(
        *,
        method: str,
        decode_fn,
        extra_notes: str,
    ) -> Tuple[Any, Dict[str, Any], Dict[str, int]]:
        model = PowerProjectivePQMultiTask(
            PowerProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones"),
            n_classes=len(cls_thresholds),
        )
        train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb, yb, db, sb, lb = (
                batch[0].to(device),
                batch[1].to(device),
                batch[2].to(device),
                batch[3].to(device),
                batch[4].to(device),
            )
            P, Q, logits = model(xb)
            pred = decode_fn(P, Q)
            mse = weighted_mse(pred, yb, db)
            mono = mono_penalty(pred, sb, lb)
            loss = (float(args.lambda_reg_aux) * mse if cls_enabled else mse) + float(args.lambda_mono) * mono
            if cls_enabled:
                loss = loss + float(args.lambda_cls) * cls_loss(logits, cls_targets(db))
            return loss

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: decode_fn(*model(xb)[:2]), label=f"power_{method}_forward")

        def predict_fn(batch):
            xb = batch[0].to(device)
            P, Q, _logits = model(xb)
            return decode_fn(P, Q)

        def predict_logits(batch):
            xb = batch[0].to(device)
            _P, _Q, logits = model(xb)
            return logits

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=predict_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=predict_fn)
        holdout_metrics = eval_holdout_if_present(model, predict=predict_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], delta_test, edges)
        band = near_collapse_band(test_metrics["per_sample_mse"], delta_test, thr=float(args.pole_delta_threshold))
        shape = (
            monotonicity_violation_rate([float(p[0]) for p in test_metrics["predictions"]], scenario_test, lambda_test)
            if str(args.target) in ("vmin", "delta_lambda")
            else None
        )
        lambda_star_metrics = (
            lambda_star_metrics_from_delta(
                [float(p[0]) for p in test_metrics["predictions"]],
                lambda_vals=lambda_test,
                delta_true=delta_test,
                scenario_ids=scenario_test,
            )
            if str(args.target) == "delta_lambda"
            else None
        )
        cls_tm = evaluate_classification(model, test_loader, predict_logits_fn=predict_logits) if cls_enabled else None
        if isinstance(cls_tm, dict):
            test_metrics = {**test_metrics, **cls_tm}
        near_collapse_cls = (
            near_collapse_classification_from_logits(
                (cls_tm or {}).get("cls_logits", []),
                delta_true=delta_test,
                thresholds=cls_thresholds,
                fpr_budget=float(args.cls_fpr_budget),
                invalid_policy=str(args.cls_invalid_policy),
            )
            if cls_enabled and isinstance(cls_tm, dict)
            else None
        )
        res = {
            "model_type": "PowerProjectivePQ",
            "config": {
                "task": str(args.task),
                "target": str(args.target),
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "delta_reweight_alpha": float(args.delta_reweight_alpha),
                "delta_reweight_tau": float(delta_reweight_tau),
                "lambda_mono": float(args.lambda_mono),
                "collapse_deltas": cls_thresholds,
                "cls_fpr_budget": float(args.cls_fpr_budget),
                "cls_invalid_policy": str(args.cls_invalid_policy),
                "lambda_cls": float(args.lambda_cls),
                "lambda_reg_aux": float(args.lambda_reg_aux),
                **cls_config_record,
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "near_collapse_band": band,
            "shape_metrics": shape,
            "lambda_star_metrics": lambda_star_metrics,
            "near_collapse_classification": near_collapse_cls,
            "holdout_metrics": holdout_metrics,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual[method] = _to_builtin(res)
        add_row(
            method=method,
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(log.training_time_s),
            avg_epoch_time=float(log.avg_epoch_time_s),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"{extra_notes} target={str(args.target)}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )
        return model, test_metrics, b_counts

    if "rational_eps" in enabled:
        eps = float(args.eps)
        train_projective_decoded(method="Rational+ε", decode_fn=lambda P, Q: P / (Q + eps), extra_notes=f"eps={eps}")

    if "smooth" in enabled:
        alpha = float(args.alpha)
        train_projective_decoded(
            method="Smooth",
            decode_fn=lambda P, Q: P / torch.sqrt(Q * Q + (alpha * alpha)),
            extra_notes=f"alpha={alpha}",
        )

    if "learnable_eps" in enabled:
        model = PowerProjectivePQMultiTask(
            PowerProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones"),
            n_classes=len(cls_thresholds),
        ).to(device)
        log_eps = torch.nn.Parameter(torch.tensor(-6.0, device=device))
        opt = torch.optim.Adam(list(model.parameters()) + [log_eps], lr=float(args.lr))
        losses: List[float] = []
        steps = 0
        t0 = time.perf_counter()

        def decode(P, Q):
            eps_t = torch.nn.functional.softplus(log_eps)
            return P / (Q + eps_t)

        model.train()
        for _epoch in range(int(args.epochs)):
            batch_losses: List[float] = []
            for batch in train_loader:
                steps += 1
                opt.zero_grad(set_to_none=True)
                xb, yb, db, sb, lb = (
                    batch[0].to(device),
                    batch[1].to(device),
                    batch[2].to(device),
                    batch[3].to(device),
                    batch[4].to(device),
                )
                P, Q, logits = model(xb)
                pred = decode(P, Q)
                mse = weighted_mse(pred, yb, db)
                mono = mono_penalty(pred, sb, lb)
                loss = (float(args.lambda_reg_aux) * mse if cls_enabled else mse) + float(args.lambda_mono) * mono
                if cls_enabled:
                    loss = loss + float(args.lambda_cls) * cls_loss(logits, cls_targets(db))
                loss.backward()
                opt.step()
                batch_losses.append(float(loss.detach().cpu().item()))
            losses.append(sum(batch_losses) / max(1, len(batch_losses)))
        total = float(time.perf_counter() - t0)

        def predict_fn(batch):
            xb = batch[0].to(device)
            P, Q, _logits = model(xb)
            return decode(P, Q)

        def predict_logits(batch):
            xb = batch[0].to(device)
            _P, _Q, logits = model(xb)
            return logits

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=predict_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=predict_fn)
        bench = maybe_microbench(predict_fn=lambda xb: decode(*model(xb)[:2]), label="power_learnable_eps_forward")
        holdout_metrics = eval_holdout_if_present(model, predict=predict_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], delta_test, edges)
        band = near_collapse_band(test_metrics["per_sample_mse"], delta_test, thr=float(args.pole_delta_threshold))
        shape = (
            monotonicity_violation_rate([float(p[0]) for p in test_metrics["predictions"]], scenario_test, lambda_test)
            if str(args.target) in ("vmin", "delta_lambda")
            else None
        )
        lambda_star_metrics = (
            lambda_star_metrics_from_delta(
                [float(p[0]) for p in test_metrics["predictions"]],
                lambda_vals=lambda_test,
                delta_true=delta_test,
                scenario_ids=scenario_test,
            )
            if str(args.target) == "delta_lambda"
            else None
        )
        cls_tm = evaluate_classification(model, test_loader, predict_logits_fn=predict_logits) if cls_enabled else None
        if isinstance(cls_tm, dict):
            test_metrics = {**test_metrics, **cls_tm}
        near_collapse_cls = (
            near_collapse_classification_from_logits(
                (cls_tm or {}).get("cls_logits", []),
                delta_true=delta_test,
                thresholds=cls_thresholds,
                fpr_budget=float(args.cls_fpr_budget),
                invalid_policy=str(args.cls_invalid_policy),
            )
            if cls_enabled and isinstance(cls_tm, dict)
            else None
        )
        eps_final = float(torch.nn.functional.softplus(log_eps).detach().cpu().item())
        res = {
            "model_type": "PowerLearnableEps",
            "config": {
                "task": str(args.task),
                "target": str(args.target),
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "delta_reweight_alpha": float(args.delta_reweight_alpha),
                "delta_reweight_tau": float(delta_reweight_tau),
                "lambda_mono": float(args.lambda_mono),
                "collapse_deltas": cls_thresholds,
                "cls_fpr_budget": float(args.cls_fpr_budget),
                "cls_invalid_policy": str(args.cls_invalid_policy),
                "lambda_cls": float(args.lambda_cls),
                "lambda_reg_aux": float(args.lambda_reg_aux),
                **cls_config_record,
            },
            "training_results": {
                "training_time": total,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": losses,
                "optimizer_steps": steps,
            },
            "test_metrics": {**test_metrics, "eps_final": eps_final},
            "near_collapse_band": band,
            "shape_metrics": shape,
            "lambda_star_metrics": lambda_star_metrics,
            "near_collapse_classification": near_collapse_cls,
            "holdout_metrics": holdout_metrics,
            "n_parameters": int(sum(p.numel() for p in model.parameters())) + 1,
            "training_time": total,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["LearnableEps"] = _to_builtin(res)
        add_row(
            method="LearnableEps",
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(total),
            avg_epoch_time=float(total / max(1, int(args.epochs))),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"eps_final≈{eps_final:.2e} target={str(args.target)}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if "eps_ens" in enabled:
        eps_list = [float(x) for x in args.ens_eps]
        members: List[Tuple[float, PowerProjectivePQMultiTask, float, int]] = []
        preds: List[torch.Tensor] = []
        total_params = 0
        total_train_time = 0.0
        total_steps = 0

        for eps in eps_list:
            model = PowerProjectivePQMultiTask(
                PowerProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones"),
                n_classes=len(cls_thresholds),
            )
            train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

            def loss_fn(batch, *, _eps: float = eps, _m=model):
                xb, yb, db, sb, lb = (
                    batch[0].to(device),
                    batch[1].to(device),
                    batch[2].to(device),
                    batch[3].to(device),
                    batch[4].to(device),
                )
                P, Q, logits = _m(xb)
                pred = P / (Q + float(_eps))
                mse = weighted_mse(pred, yb, db)
                mono = mono_penalty(pred, sb, lb)
                loss = (float(args.lambda_reg_aux) * mse if cls_enabled else mse) + float(args.lambda_mono) * mono
                if cls_enabled:
                    loss = loss + float(args.lambda_cls) * cls_loss(logits, cls_targets(db))
                return loss

            log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
            total_train_time += float(log.training_time_s)
            total_steps += int(log.optimizer_steps)
            params = int(sum(p.numel() for p in model.parameters()))
            total_params += params
            members.append((float(eps), model, float(log.training_time_s), int(log.optimizer_steps)))

        @torch.no_grad()
        def predict_fn(batch):
            xb = batch[0].to(device)
            outs = []
            for eps, m, _t, _s in members:
                P, Q, _logits = m(xb)
                outs.append(P / (Q + float(eps)))
            return torch.mean(torch.stack(outs, dim=0), dim=0)

        @torch.no_grad()
        def bench_predict(xb: torch.Tensor) -> torch.Tensor:
            outs = []
            for eps, m, _t, _s in members:
                P, Q, _logits = m(xb)
                outs.append(P / (Q + float(eps)))
            return torch.mean(torch.stack(outs, dim=0), dim=0)

        @torch.no_grad()
        def predict_logits(batch):
            xb = batch[0].to(device)
            outs = []
            for _eps, m, _t, _s in members:
                _P, _Q, logits = m(xb)
                outs.append(logits)
            return torch.mean(torch.stack(outs, dim=0), dim=0)

        train_metrics = evaluate_regression(members[0][1], train_eval_loader, device=device, predict_fn=predict_fn)
        test_metrics = evaluate_regression(members[0][1], test_loader, device=device, predict_fn=predict_fn)
        bench = maybe_microbench(predict_fn=bench_predict, label="power_eps_ens_forward")
        holdout_metrics = eval_holdout_if_present(members[0][1], predict=predict_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], delta_test, edges)
        band = near_collapse_band(test_metrics["per_sample_mse"], delta_test, thr=float(args.pole_delta_threshold))
        shape = (
            monotonicity_violation_rate([float(p[0]) for p in test_metrics["predictions"]], scenario_test, lambda_test)
            if str(args.target) in ("vmin", "delta_lambda")
            else None
        )
        lambda_star_metrics = (
            lambda_star_metrics_from_delta(
                [float(p[0]) for p in test_metrics["predictions"]],
                lambda_vals=lambda_test,
                delta_true=delta_test,
                scenario_ids=scenario_test,
            )
            if str(args.target) == "delta_lambda"
            else None
        )
        cls_tm = evaluate_classification(members[0][1], test_loader, predict_logits_fn=predict_logits) if cls_enabled else None
        if isinstance(cls_tm, dict):
            test_metrics = {**test_metrics, **cls_tm}
        near_collapse_cls = (
            near_collapse_classification_from_logits(
                (cls_tm or {}).get("cls_logits", []),
                delta_true=delta_test,
                thresholds=cls_thresholds,
                fpr_budget=float(args.cls_fpr_budget),
                invalid_policy=str(args.cls_invalid_policy),
            )
            if cls_enabled and isinstance(cls_tm, dict)
            else None
        )

        res = {
            "model_type": "PowerEpsEnsemble",
            "config": {
                "task": str(args.task),
                "target": str(args.target),
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "ens_eps": eps_list,
                "delta_reweight_alpha": float(args.delta_reweight_alpha),
                "delta_reweight_tau": float(delta_reweight_tau),
                "lambda_mono": float(args.lambda_mono),
                "collapse_deltas": cls_thresholds,
                "cls_fpr_budget": float(args.cls_fpr_budget),
                "cls_invalid_policy": str(args.cls_invalid_policy),
                "lambda_cls": float(args.lambda_cls),
                "lambda_reg_aux": float(args.lambda_reg_aux),
                **cls_config_record,
            },
            "training_results": {
                "training_time": total_train_time,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "optimizer_steps": total_steps,
                "members": [{"eps": e, "training_time": t, "optimizer_steps": s} for e, _m, t, s in members],
            },
            "test_metrics": test_metrics,
            "near_collapse_band": band,
            "shape_metrics": shape,
            "lambda_star_metrics": lambda_star_metrics,
            "near_collapse_classification": near_collapse_cls,
            "holdout_metrics": holdout_metrics,
            "n_parameters": int(total_params),
            "training_time": float(total_train_time),
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["EpsEnsemble"] = _to_builtin(res)
        add_row(
            method="EpsEnsemble",
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(total_train_time),
            avg_epoch_time=float(total_train_time / max(1, int(args.epochs))),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"members={eps_list} target={str(args.target)}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # Attach peak resources at end (best-effort).
    comp["resources"]["peak_rss_mb"] = peak_rss_mb()
    comp["resources"]["torch_cuda_peak_mb"] = torch_cuda_peak_mb()

    # Summary helpers
    mses = [row.get("Test_MSE") for row in table if isinstance(row, dict)]
    mses = [float(x) for x in mses if isinstance(x, (int, float)) and math.isfinite(float(x))]
    comp["summary"]["methods_tested"] = int(len(table))
    if mses:
        comp["summary"]["best_mse"] = float(min(mses))

    out_json = os.path.join(args.output_dir, "comprehensive_comparison.json")
    out_csv = os.path.join(args.output_dir, "comparison_table.csv")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(_to_builtin(comp), fh, indent=2)

    import csv

    fieldnames: List[str] = []
    for row in table:
        for k in row.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(table)

    print(f"Results saved to:\n  - {out_json}\n  - {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
