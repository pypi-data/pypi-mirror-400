from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import torch

from examples.brachy.brachy_dataset import dataset_info_dict, flatten_xy, flatten_xy_with_prior, load_brachy_dataset
from examples.brachy.models import (
    FourierMLP,
    FourierMLPConfig,
    MLP,
    MLPConfig,
    ProjectivePQ,
    ProjectivePQConfig,
    Rational2DPoly,
    Rational2DPolyConfig,
    Siren,
    SirenConfig,
)
from examples.torch_baselines.trainer import TrainConfig, evaluate_regression, evaluate_regression_mse, train_loop, train_loop_with_selection
from zeroproofml.benchmark import TorchMicrobenchConfig, torch_microbench
from zeroproofml.experiment_protocol import protocol_v1
from zeroproofml.resources import collect_system_info, peak_rss_mb, torch_cuda_peak_mb


def _set_seed(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(int(seed))
    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))


def _infer_device(req: str) -> str:
    if req == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if req == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return req


def _bucket_key(edges: List[float], i: int) -> str:
    lo = edges[i]
    hi = edges[i + 1]
    lo_s = f"{lo:.0e}" if math.isfinite(lo) else "inf"
    hi_s = f"{hi:.0e}" if math.isfinite(hi) else "inf"
    return f"({lo_s},{hi_s}]"


def _bucketize(x: float, edges: List[float]) -> int:
    for b in range(len(edges) - 1):
        lo, hi = float(edges[b]), float(edges[b + 1])
        if (x >= lo if b == 0 else x > lo) and x <= hi:
            return b
    return len(edges) - 2


def _bucket_mse(per_sample_mse: List[float], r_vals: List[float], edges: List[float]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    per_bucket: Dict[str, List[float]] = {_bucket_key(edges, i): [] for i in range(len(edges) - 1)}
    counts: Dict[str, int] = {_bucket_key(edges, i): 0 for i in range(len(edges) - 1)}
    for mse, r in zip(per_sample_mse, r_vals):
        b = _bucketize(float(r), edges)
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


def _tg43_like_oracle(
    r_mm: float,
    theta_rad: float,
    *,
    p: Dict[str, Any],
) -> float:
    S = float(p.get("S", 1.0))
    mu = float(p.get("mu", 0.0))
    a1 = float(p.get("a1", 0.0))
    a2 = float(p.get("a2", 0.0))
    A = max(0.05, 1.0 + a1 * math.cos(float(theta_rad)) + a2 * math.cos(2.0 * float(theta_rad)))
    r = max(1e-12, float(r_mm))
    return float(S) * float(A) * math.exp(-float(mu) * r) / (r * r)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Torch-first brachy primary-dose comparator (Phase 14 scaffold)")
    ap.add_argument("--dataset", required=True, help="Path to brachy dataset JSON")
    ap.add_argument("--output_dir", required=True, help="Output directory")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    ap.add_argument("--task", choices=["primary", "residual"], default="primary")
    ap.add_argument(
        "--correction",
        choices=["additive", "log_factor", "gate_factor"],
        default="additive",
        help="Residual correction mode for --task residual: additive uses y=y_tg43+Δ; log_factor uses log(y+eps)=log(y_tg43+eps)+g.",
    )
    ap.add_argument("--correction-eps", type=float, default=1e-12, help="epsilon for log_factor correction (log(y+eps))")
    ap.add_argument("--gate-min", type=float, default=0.01, help="Minimum transmission for gate_factor correction.")
    ap.add_argument(
        "--gate-loss",
        choices=["logit", "dose"],
        default="logit",
        help="When --correction gate_factor: supervise shutter logit (logit) or optimize total-dose error directly (dose).",
    )
    ap.add_argument(
        "--target",
        choices=["dose", "log_dose", "r2_dose"],
        default="dose",
        help="Training target transform for learned models (evaluation remains in dose space).",
    )
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--batch_size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--hidden_dims", nargs="*", type=int, default=[64, 64])
    ap.add_argument("--models", nargs="*", default=None, help="Subset of methods to run")
    ap.add_argument("--r_near_mm", type=float, default=5.0, help="Near-field cutoff (mm) for headline metrics")
    ap.add_argument("--r_reweight_alpha", type=float, default=0.0, help="If >0, upweight small-r via 1+alpha*exp(-r/tau).")
    ap.add_argument("--r_reweight_tau", type=float, default=None, help="r scale for weighting (default: r_near_mm).")
    ap.add_argument("--no-microbench", action="store_true")
    ap.add_argument("--microbench-iters", type=int, default=120)
    ap.add_argument("--microbench-warmup", type=int, default=30)
    ap.add_argument("--val-ratio", type=float, default=0.1, help="Fraction of train split reserved for validation (0 disables).")
    ap.add_argument("--scheduler", choices=["cosine", "none"], default="cosine")
    ap.add_argument("--eta-min", type=float, default=None, help="Scheduler eta_min (default: min(1e-7, lr*0.01))")
    ap.add_argument("--no-restore-best", action="store_true", help="Do not restore best validation checkpoint.")

    # Projective baselines
    ap.add_argument("--eps", type=float, default=1e-3, help="Fixed epsilon for Rational+ε")
    ap.add_argument("--alpha", type=float, default=1e-3, help="Fixed alpha for Smooth")
    ap.add_argument("--ens_eps", nargs="*", type=float, default=[1e-4, 1e-3, 1e-2], help="EpsEnsemble eps list")

    # Strong coordinate baselines
    ap.add_argument("--fourier-freqs", type=int, default=6)
    ap.add_argument("--siren-w0", type=float, default=30.0)
    ap.add_argument("--log-dose-eps", type=float, default=1e-12, help="epsilon for log(y+eps) baseline")

    # Rational shutter baseline (2D poly rational)
    ap.add_argument("--rational2d-degree", type=int, default=4, help="Degree for Rational2DPoly baseline")
    ap.add_argument("--rational2d-r-scale-mm", type=float, default=None, help="r scaling for Rational2DPoly (default: dataset r_max_mm)")
    ap.add_argument("--rational2d-q-min", type=float, default=1e-6, help="Minimum added to Q for Rational2DPoly baseline")

    # Parametric TG-43 fit baseline
    ap.add_argument("--tg43-fit-steps", type=int, default=2000)
    ap.add_argument("--tg43-fit-lr", type=float, default=5e-2)

    args = ap.parse_args(argv)

    os.makedirs(args.output_dir, exist_ok=True)
    device = _infer_device(str(args.device))
    _set_seed(args.seed)

    target_mode = str(args.target)
    task = str(args.task)
    correction = str(args.correction)
    corr_eps = float(args.correction_eps)
    gate_min = float(args.gate_min)
    gate_loss = str(args.gate_loss)
    factorized_method = "Factorized-SIREN-ProjectivePQ"
    if task == "residual" and target_mode == "log_dose":
        raise SystemExit("--task residual does not support --target=log_dose (residuals may be signed).")
    if task == "residual" and correction == "log_factor" and target_mode != "dose":
        raise SystemExit("--correction log_factor currently requires --target=dose (g is already a log-space target).")
    if task == "residual" and correction == "gate_factor" and target_mode != "dose":
        raise SystemExit("--correction gate_factor currently requires --target=dose.")
    if corr_eps <= 0.0 or not math.isfinite(corr_eps):
        raise SystemExit("--correction-eps must be a finite positive number.")
    if not (0.0 <= gate_min < 1.0):
        raise SystemExit("--gate-min must satisfy 0 <= gate_min < 1.")

    enabled = set(
        args.models
        or [
            *(
                [
                    "TG43-Oracle",
                    "TG43-Fit",
                    "MLP",
                    "FourierMLP",
                    "SIREN",
                    factorized_method,
                    *([] if target_mode != "dose" else ["LogMLP"]),
                    "Rational+ε",
                    "Smooth",
                    "LearnableEps",
                    "EpsEnsemble",
                ]
                if task == "primary"
                else [
                    "TG43-Prior",
                    "TG43+MLP",
                    "TG43+FourierMLP",
                    "TG43+SIREN",
                    "TG43+Factorized-SIREN",
                    "TG43+Rational2DPoly",
                ]
            )
        ]
    )

    data = load_brachy_dataset(args.dataset)
    if task == "primary":
        info, x, y, r_mm, theta, param_ids, train_idx, test_idx = flatten_xy(data, dataset_path=str(args.dataset))
        y_tg43 = None
    else:
        info, x, y, y_tg43_list, r_mm, theta, param_ids, train_idx, test_idx = flatten_xy_with_prior(data, dataset_path=str(args.dataset))
        if any(not math.isfinite(float(v)) for v in y_tg43_list):
            raise SystemExit("Residual task requires y_tg43 in dataset (regenerate with Phase 15 dataset generator).")
        y_tg43 = [float(v) for v in y_tg43_list]
    edges = info.r_bucket_edges_mm or [0.0, 1.0, 2.0, 5.0, 10.0, 30.0, float("inf")]
    input_dim = int(info.input_dim)
    r_scale_mm = float(args.rational2d_r_scale_mm) if args.rational2d_r_scale_mm is not None else float(info.r_max_mm or 30.0)

    x_t = torch.tensor(x, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
    y_prior_t = torch.tensor([float(v) for v in y_tg43], dtype=torch.float32).unsqueeze(-1) if y_tg43 is not None else None
    r_t = torch.tensor([float(v) for v in r_mm], dtype=torch.float32).unsqueeze(-1)

    x_train = x_t[train_idx]
    y_train = y_t[train_idx]
    r_train = r_t[train_idx]
    x_test = x_t[test_idx]
    y_test = y_t[test_idx]
    r_test = r_t[test_idx]
    y_prior_train = y_prior_t[train_idx] if y_prior_t is not None else None
    y_prior_test = y_prior_t[test_idx] if y_prior_t is not None else None
    r_test_list = [float(r_mm[i]) for i in test_idx]
    theta_test_list = [float(theta[i]) for i in test_idx]
    pid_test_list = [int(param_ids[i]) for i in test_idx]

    # Deterministic train/val split inside the declared train set (never touch the test split).
    val_ratio = float(args.val_ratio)
    if not math.isfinite(val_ratio) or val_ratio < 0.0:
        val_ratio = 0.0
    if val_ratio > 0.5:
        val_ratio = 0.5
    n_train = int(x_train.shape[0])
    n_val = 0
    if val_ratio > 0.0 and n_train >= 4:
        n_val = int(max(1, min(n_train - 2, math.floor(val_ratio * n_train))))

    if n_val:
        gen = torch.Generator()
        gen.manual_seed(int(args.seed))
        perm = torch.randperm(n_train, generator=gen)
        val_sel = perm[:n_val]
        train_sel = perm[n_val:]
        x_val, y_val, r_val = x_train[val_sel], y_train[val_sel], r_train[val_sel]
        x_tr, y_tr, r_tr = x_train[train_sel], y_train[train_sel], r_train[train_sel]
        if task == "residual":
            assert y_prior_train is not None
            prior_val = y_prior_train[val_sel]
            prior_tr = y_prior_train[train_sel]
            val_loader = torch.utils.data.DataLoader(
                torch.utils.data.TensorDataset(x_val, y_val, r_val, prior_val),
                batch_size=int(args.batch_size),
                shuffle=False,
            )
        else:
            val_loader = torch.utils.data.DataLoader(
                torch.utils.data.TensorDataset(x_val, y_val, r_val),
                batch_size=int(args.batch_size),
                shuffle=False,
            )
    else:
        x_tr, y_tr, r_tr = x_train, y_train, r_train
        prior_tr = y_prior_train
        val_loader = None

    if task == "residual":
        assert prior_tr is not None and y_prior_test is not None
        train_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_tr, y_tr, r_tr, prior_tr),
            batch_size=int(args.batch_size),
            shuffle=True,
        )
        train_eval_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_tr, y_tr, r_tr, prior_tr),
            batch_size=int(args.batch_size),
            shuffle=False,
        )
        test_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_test, y_test, r_test, y_prior_test),
            batch_size=int(args.batch_size),
            shuffle=False,
        )
    else:
        train_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_tr, y_tr, r_tr),
            batch_size=int(args.batch_size),
            shuffle=True,
        )
        train_eval_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_tr, y_tr, r_tr),
            batch_size=int(args.batch_size),
            shuffle=False,
        )
        test_loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_test, y_test, r_test),
            batch_size=int(args.batch_size),
            shuffle=False,
        )

    comp: Dict[str, Any] = {
        "protocol": protocol_v1(domain="brachy_primary", suite_name="paper_suite_brachy"),
        "resources": {"system": collect_system_info()},
        "dataset_info": {
            **dataset_info_dict(info),
            "train_indices": train_idx,
            "test_indices": test_idx,
            "val_ratio": float(val_ratio),
            "n_val": int(n_val),
            "task": str(task),
            "target_transform": target_mode,
            "target_log_eps": float(args.log_dose_eps),
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

    r_reweight_tau = float(args.r_reweight_tau) if args.r_reweight_tau is not None else float(args.r_near_mm)

    def sample_weights(r_batch: torch.Tensor) -> torch.Tensor:
        if float(args.r_reweight_alpha) <= 0.0:
            return torch.ones_like(r_batch)
        tau = max(1e-12, float(r_reweight_tau))
        return 1.0 + float(args.r_reweight_alpha) * torch.exp(-r_batch / tau)

    def weighted_mse(pred: torch.Tensor, yb: torch.Tensor, rb: torch.Tensor) -> torch.Tensor:
        w = sample_weights(rb)
        return torch.mean(w * (pred - yb) ** 2)

    def transform_target(yb: torch.Tensor, rb: torch.Tensor) -> torch.Tensor:
        if target_mode == "dose":
            return yb
        if target_mode == "log_dose":
            return torch.log(yb + float(args.log_dose_eps))
        if target_mode == "r2_dose":
            r2 = torch.clamp_min(rb, 1e-12) ** 2
            return yb * r2
        raise ValueError(f"Unknown --target: {target_mode}")

    def inverse_target(pred_tgt: torch.Tensor, rb: torch.Tensor) -> torch.Tensor:
        if target_mode == "dose":
            return pred_tgt
        if target_mode == "log_dose":
            return torch.exp(pred_tgt) - float(args.log_dose_eps)
        if target_mode == "r2_dose":
            r2 = torch.clamp_min(rb, 1e-12) ** 2
            return pred_tgt / r2
        raise ValueError(f"Unknown --target: {target_mode}")

    def near_field_metrics(preds: List[float], targets: List[float], r_vals: List[float], *, r_thr: float) -> Dict[str, Any]:
        sel = []
        rel = []
        under_abs = []
        under_rel = []
        for p, t, r in zip(preds, targets, r_vals):
            if not (math.isfinite(float(p)) and math.isfinite(float(t)) and float(r) <= float(r_thr)):
                continue
            sel.append((float(p) - float(t)) ** 2)
            rel.append(abs(float(p) - float(t)) / max(1e-12, abs(float(t))))
            ua = max(0.0, float(t) - float(p))
            under_abs.append(ua)
            under_rel.append(ua / max(1e-12, abs(float(t))))
        if not sel:
            return {
                "r_thr_mm": float(r_thr),
                "mse": None,
                "n": 0,
                "rel_p95": None,
                "rel_p99": None,
                "underdose_abs_p95": None,
                "underdose_abs_p99": None,
                "underdose_rel_p95": None,
                "underdose_rel_p99": None,
            }
        sel.sort()
        rel.sort()
        under_abs.sort()
        under_rel.sort()

        def _pct(xs: List[float], q: float) -> float:
            if not xs:
                return float("nan")
            i = int(round((len(xs) - 1) * float(q)))
            return float(xs[max(0, min(len(xs) - 1, i))])

        return {
            "r_thr_mm": float(r_thr),
            "mse": float(sum(sel) / len(sel)),
            "n": int(len(sel)),
            "rel_p95": _pct(rel, 0.95),
            "rel_p99": _pct(rel, 0.99),
            "underdose_abs_p95": _pct(under_abs, 0.95),
            "underdose_abs_p99": _pct(under_abs, 0.99),
            "underdose_rel_p95": _pct(under_rel, 0.95),
            "underdose_rel_p99": _pct(under_rel, 0.99),
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

    # --------------------------
    # TG43 oracle (Tier A reference)
    # --------------------------
    if "TG43-Oracle" in enabled and task == "primary":
        params = data.get("parameter_sets") if isinstance(data.get("parameter_sets"), list) else []
        params_by_id = {int(p.get("param_id", -1)): p for p in params if isinstance(p, dict)}
        preds: List[List[float]] = []
        for r, th, pid in zip(r_test_list, theta_test_list, pid_test_list):
            p = params_by_id.get(int(pid), {})
            preds.append([_tg43_like_oracle(r, th, p=p)])

        # Build test metrics matching evaluate_regression schema
        per_mse = []
        for pred, tgt in zip(preds, y_test.tolist()):
            e = (float(pred[0]) - float(tgt[0])) ** 2
            per_mse.append(float(e))
        test_mse = float(sum(per_mse) / len(per_mse)) if per_mse else float("inf")
        train_mse = test_mse
        b_mse, b_counts = _bucket_mse(per_mse, r_test_list, edges)
        nf = near_field_metrics([p[0] for p in preds], [float(t[0]) for t in y_test.tolist()], r_test_list, r_thr=float(args.r_near_mm))
        bench = maybe_microbench(predict_fn=lambda xb: xb.new_tensor([[0.0]]).expand(xb.shape[0], 1), label="tg43_oracle_stub")
        res = {
            "model_type": "TG43Oracle",
            "config": {"note": "Uses dataset parameter_sets; Tier A oracle/reference"},
            "training_results": {"training_time": 0.0, "final_train_mse": train_mse, "final_val_mse": train_mse, "optimizer_steps": 0},
            "test_metrics": {
                "mse": test_mse,
                "n_samples": int(len(per_mse)),
                "n_valid": int(len(per_mse)),
                "success_rate": 1.0,
                "predictions": preds,
                "per_sample_mse": per_mse,
                "inference_us_per_sample": None,
            },
            "near_field_metrics": nf,
            "n_parameters": 0,
            "training_time": 0.0,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["TG43-Oracle"] = _to_builtin(res)
        add_row(
            method="TG43-Oracle",
            params=0,
            epochs=0,
            train_mse=float(train_mse),
            test_mse=float(test_mse),
            training_time=0.0,
            avg_epoch_time=0.0,
            success_rate=1.0,
            inference_us_per_sample=None,
            notes="TG-43-like oracle (Tier A reference)",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # --------------------------
    # Parametric TG43 fit (low-dim learned baseline)
    # --------------------------
    if "TG43-Fit" in enabled and task == "primary":
        # Fit y(r,theta)=S*A(theta)*exp(-mu*r)/r^2 with A(theta)=softplus(b0+b1 cos + b2 cos2)+0.05
        class ParamTG43(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.log_S = torch.nn.Parameter(torch.tensor(0.0))
                self.mu_raw = torch.nn.Parameter(torch.tensor(-3.0))
                self.b0 = torch.nn.Parameter(torch.tensor(1.0))
                self.b1 = torch.nn.Parameter(torch.tensor(0.0))
                self.b2 = torch.nn.Parameter(torch.tensor(0.0))

            def forward(self, xb: torch.Tensor) -> torch.Tensor:
                r = xb[:, 0:1].clamp_min(1e-6)
                th = xb[:, 1:2]
                S = torch.exp(self.log_S)
                mu = torch.nn.functional.softplus(self.mu_raw)
                A = torch.nn.functional.softplus(self.b0 + self.b1 * torch.cos(th) + self.b2 * torch.cos(2.0 * th)) + 0.05
                return S * A * torch.exp(-mu * r) / (r * r)

        model = ParamTG43().to(device)
        x_train_dev = x_tr.to(device)
        y_train_dev = y_tr.to(device)
        opt = torch.optim.Adam(model.parameters(), lr=float(args.tg43_fit_lr))
        steps = int(args.tg43_fit_steps)
        if bool(args.quick):
            steps = min(600, steps)

        t0 = time.perf_counter()
        for _ in range(steps):
            opt.zero_grad(set_to_none=True)
            pred = model(x_train_dev)
            loss = torch.mean((pred - y_train_dev) ** 2)
            loss.backward()
            opt.step()
        training_time = float(time.perf_counter() - t0)

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            return model(xb)

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        bench = maybe_microbench(predict_fn=lambda xb: model(xb.to(device)), label="tg43_fit_forward")
        res = {
            "model_type": "TG43Fit",
            "config": {"steps": int(steps), "lr": float(args.tg43_fit_lr)},
            "training_results": {
                "training_time": training_time,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "optimizer_steps": int(steps),
                "params": {
                    "S": float(torch.exp(model.log_S).detach().cpu().item()),
                    "mu": float(torch.nn.functional.softplus(model.mu_raw).detach().cpu().item()),
                    "b": [float(x.detach().cpu().item()) for x in (model.b0, model.b1, model.b2)],
                },
            },
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": training_time,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["TG43-Fit"] = _to_builtin(res)
        add_row(
            method="TG43-Fit",
            params=5,
            epochs=0,
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(training_time),
            avg_epoch_time=float(training_time),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes="Parametric TG43 fit (softplus anisotropy)",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    def train_regression_model(
        *,
        method: str,
        model: torch.nn.Module,
        loss_mode: str,
        extra_notes: str,
        log_space: bool = False,
    ) -> None:
        train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            if log_space:
                pred = torch.exp(model(xb)) - float(args.log_dose_eps)
            else:
                out_tgt = model(xb)
                rb = batch[2].to(device)
                pred = inverse_target(out_tgt, rb)
            if task == "residual":
                prior = batch[3].to(device)
                if correction == "log_factor":
                    log_total = torch.log(prior + corr_eps) + pred
                    return torch.exp(log_total) - corr_eps
                if correction == "gate_factor":
                    # pred is a logit for the shutter in [gate_min,1]
                    shutter = torch.sigmoid(pred)
                    shutter = gate_min + (1.0 - gate_min) * shutter
                    return prior * shutter
                return prior + pred
            return pred

        def loss_fn(batch):
            xb = batch[0].to(device)
            yb = batch[1].to(device)
            rb = batch[2].to(device)
            prior = batch[3].to(device) if task == "residual" else None
            if log_space:
                pred = torch.exp(model(xb)) - float(args.log_dose_eps)
                tgt = yb
            else:
                pred = model(xb)
                if task == "residual":
                    assert prior is not None
                    if correction == "log_factor":
                        # g = log(y_gt+eps) - log(y_prior+eps)
                        tgt = torch.log(yb + corr_eps) - torch.log(prior + corr_eps)
                    elif correction == "gate_factor":
                        if gate_loss == "dose":
                            shutter = torch.sigmoid(pred)
                            shutter = gate_min + (1.0 - gate_min) * shutter
                            y_hat = prior * shutter
                            if loss_mode == "weighted":
                                return weighted_mse(y_hat, yb, rb)
                            return torch.mean((y_hat - yb) ** 2)
                        # gate_loss == "logit": supervise the shutter logit directly.
                        ratio = (yb + corr_eps) / (prior + corr_eps)
                        ratio = torch.clamp(ratio, min=gate_min, max=1.0)
                        z = (ratio - gate_min) / max(1e-12, (1.0 - gate_min))
                        z = torch.clamp(z, min=1e-6, max=1.0 - 1e-6)
                        tgt = torch.log(z) - torch.log1p(-z)
                    else:
                        tgt = transform_target(yb - prior, rb)
                else:
                    tgt = transform_target(yb, rb)
            if loss_mode == "weighted":
                return weighted_mse(pred, tgt, rb)
            return torch.mean((pred - tgt) ** 2)

        def val_mse() -> float:
            if val_loader is None:
                return float("inf")
            return float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=pred_fn))

        if val_loader is not None:
            log = train_loop_with_selection(
                model,
                train_loader,
                loss_fn,
                cfg=train_cfg,
                val_loader=val_loader,
                val_mse_fn=val_mse,
                scheduler=str(args.scheduler),
                eta_min=(float(args.eta_min) if args.eta_min is not None else None),
                restore_best=not bool(args.no_restore_best),
            )
        else:
            log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        if log_space or target_mode == "log_dose":
            bench = maybe_microbench(predict_fn=lambda xb: torch.exp(model(xb.to(device))) - float(args.log_dose_eps), label=f"{method}_forward")
        elif target_mode == "r2_dose":
            bench = maybe_microbench(
                predict_fn=lambda xb: model(xb.to(device)) / (torch.clamp_min(xb[:, 0:1].to(device), 1e-12) ** 2),
                label=f"{method}_forward",
            )
        else:
            bench = maybe_microbench(predict_fn=lambda xb: model(xb.to(device)), label=f"{method}_forward")

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        val_mse_final = float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=pred_fn)) if val_loader is not None else None
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        res = {
            "model_type": method,
            "config": {
                "task": str(task),
                "correction": str(correction),
                "correction_eps": float(corr_eps),
                "gate_min": float(gate_min),
                "gate_loss": str(gate_loss),
                "hidden_dims": list(args.hidden_dims),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "lr": float(args.lr),
                "r_reweight_alpha": float(args.r_reweight_alpha),
                "r_reweight_tau": float(r_reweight_tau),
                "loss_mode": str(loss_mode),
                "log_space": bool(log_space),
                "log_dose_eps": float(args.log_dose_eps),
                "target_transform": ("log_dose" if log_space else target_mode),
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": val_mse_final,
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
                "val_mse_history": getattr(log, "val_mse_history", None),
                "best_epoch": getattr(log, "best_epoch", None),
                "best_val_mse": getattr(log, "best_val_mse", None),
                "restored_best": getattr(log, "restored_best", False),
            },
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
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
            notes=f"{extra_notes} reweight={float(args.r_reweight_alpha):.2f} tau={float(r_reweight_tau):.2f}mm",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if task == "residual":
        if y_prior_test is None:
            raise SystemExit("Residual task requires y_tg43 prior values in dataset.")

        if "TG43-Prior" in enabled:
            class _Null(torch.nn.Module):
                def forward(self, xb: torch.Tensor) -> torch.Tensor:  # pragma: no cover
                    return xb

            null_model = _Null().to(device)

            @torch.no_grad()
            def pred_fn(batch):
                # batch = (x, y_gt, r, y_prior)
                return batch[3].to(device)

            train_metrics = evaluate_regression(null_model, train_eval_loader, device=device, predict_fn=pred_fn)
            test_metrics = evaluate_regression(null_model, test_loader, device=device, predict_fn=pred_fn)
            b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
            nf = near_field_metrics(
                [float(p[0]) for p in test_metrics["predictions"]],
                [float(t[0]) for t in y_test.tolist()],
                r_test_list,
                r_thr=float(args.r_near_mm),
            )
            res = {
                "model_type": "TG43Prior",
                "config": {"task": "residual"},
                "training_results": {"training_time": 0.0, "final_train_mse": train_metrics["mse"], "final_val_mse": None, "optimizer_steps": 0},
                "test_metrics": test_metrics,
                "near_field_metrics": nf,
                "n_parameters": 0,
                "training_time": 0.0,
                "seed": int(args.seed),
                "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
                "microbench": None,
            }
            individual["TG43-Prior"] = _to_builtin(res)
            add_row(
                method="TG43-Prior",
                params=0,
                epochs=0,
                train_mse=float(train_metrics["mse"]),
                test_mse=float(test_metrics["mse"]),
                training_time=0.0,
                avg_epoch_time=0.0,
                success_rate=float(test_metrics["success_rate"]),
                inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
                notes="TG43 prior only (no learned correction)",
                bucket_counts=b_counts,
            )

        if "TG43+MLP" in enabled:
            model = MLP(MLPConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims))).to(device)
            train_regression_model(method="TG43+MLP", model=model, loss_mode="weighted", extra_notes="Residual: MLP")

        if "TG43+FourierMLP" in enabled:
            model = FourierMLP(
                FourierMLPConfig(
                    input_dim=input_dim,
                    n_frequencies=int(args.fourier_freqs),
                    hidden_dims=tuple(int(x) for x in args.hidden_dims),
                )
            ).to(device)
            train_regression_model(method="TG43+FourierMLP", model=model, loss_mode="weighted", extra_notes=f"Residual: FourierMLP freqs={int(args.fourier_freqs)}")

        if "TG43+SIREN" in enabled:
            model = Siren(SirenConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), w0=float(args.siren_w0))).to(device)
            train_regression_model(method="TG43+SIREN", model=model, loss_mode="weighted", extra_notes=f"Residual: SIREN w0={float(args.siren_w0)}")

        if "TG43+Factorized-SIREN" in enabled:
            class FactorizedHybrid(torch.nn.Module):
                def __init__(self) -> None:
                    super().__init__()
                    self.radial = ProjectivePQ(
                        ProjectivePQConfig(input_dim=1, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones")
                    )
                    self.angular = Siren(
                        SirenConfig(input_dim=1, hidden_dims=tuple(int(x) for x in args.hidden_dims), w0=float(args.siren_w0))
                    )
                    with torch.no_grad():
                        torch.nn.init.zeros_(self.radial.head_q.weight)
                        torch.nn.init.zeros_(self.radial.head_q.bias)
                        torch.nn.init.zeros_(self.radial.head_p.weight)
                        torch.nn.init.constant_(self.radial.head_p.bias, 0.0)
                        if hasattr(self.angular, "net") and len(self.angular.net) > 0 and isinstance(self.angular.net[-1], torch.nn.Linear):
                            torch.nn.init.zeros_(self.angular.net[-1].weight)
                            # Important: don't zero-init both branches in a multiplicative model, or gradients vanish.
                            # Start with f(theta) ~= 1 so g(r) can learn the residual scale.
                            torch.nn.init.constant_(self.angular.net[-1].bias, 1.0)

                def forward(self, xb: torch.Tensor) -> torch.Tensor:
                    r = xb[:, 0:1]
                    th = xb[:, 1:2]
                    th_n = (th / math.pi) * 2.0 - 1.0
                    P, Q = self.radial(r)
                    radial = P / (Q + 1e-6)
                    ang_raw = self.angular(th_n)
                    ang_norm = ang_raw / torch.clamp_min(torch.abs(ang_raw).mean().detach(), 1e-6)
                    return radial * ang_norm

            model = FactorizedHybrid().to(device)
            train_regression_model(method="TG43+Factorized-SIREN", model=model, loss_mode="weighted", extra_notes="Residual: Factorized")

        if "TG43+Rational2DPoly" in enabled:
            p_bias_init = 6.0 if correction == "gate_factor" else 0.0
            model = Rational2DPoly(
                Rational2DPolyConfig(
                    degree=int(args.rational2d_degree),
                    r_scale_mm=float(r_scale_mm),
                    q_min=float(args.rational2d_q_min),
                    p_bias_init=float(p_bias_init),
                    q_bias_init=1.0,
                )
            ).to(device)
            train_regression_model(method="TG43+Rational2DPoly", model=model, loss_mode="weighted", extra_notes=f"Residual: Rational2DPoly d={int(args.rational2d_degree)}")

    if "MLP" in enabled and task == "primary":
        model = MLP(MLPConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims))).to(device)
        train_regression_model(method="MLP", model=model, loss_mode="weighted", extra_notes="MLP")

    if "FourierMLP" in enabled and task == "primary":
        model = FourierMLP(
            FourierMLPConfig(
                input_dim=input_dim,
                n_frequencies=int(args.fourier_freqs),
                hidden_dims=tuple(int(x) for x in args.hidden_dims),
            )
        ).to(device)
        train_regression_model(method="FourierMLP", model=model, loss_mode="weighted", extra_notes=f"freqs={int(args.fourier_freqs)}")

    if "SIREN" in enabled and task == "primary":
        model = Siren(SirenConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), w0=float(args.siren_w0))).to(device)
        train_regression_model(method="SIREN", model=model, loss_mode="weighted", extra_notes=f"w0={float(args.siren_w0)}")

    if factorized_method in enabled and task == "primary":
        # Factorized model: y_tgt(r,theta) ≈ g(r) * f(theta)
        # - g(r): 1D ProjectivePQ on r, decoded in target space.
        # - f(theta): 1D SIREN on normalized theta, forced positive (anisotropy-like).
        class FactorizedHybrid(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.radial = ProjectivePQ(
                    ProjectivePQConfig(input_dim=1, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones")
                )
                self.angular = Siren(
                    SirenConfig(input_dim=1, hidden_dims=tuple(int(x) for x in args.hidden_dims), w0=float(args.siren_w0))
                )
                with torch.no_grad():
                    # Safe initialization:
                    # - Start radial denominator ~1 (via q_anchor + zero head_q).
                    # - Start radial numerator ~1 (constant).
                    torch.nn.init.zeros_(self.radial.head_q.weight)
                    torch.nn.init.zeros_(self.radial.head_q.bias)
                    torch.nn.init.zeros_(self.radial.head_p.weight)
                    torch.nn.init.constant_(self.radial.head_p.bias, 1.0)
                    # Start angular output ~0 so softplus(0)+0.05 is a stable positive constant.
                    if hasattr(self.angular, "net") and len(self.angular.net) > 0 and isinstance(self.angular.net[-1], torch.nn.Linear):
                        torch.nn.init.zeros_(self.angular.net[-1].weight)
                        torch.nn.init.zeros_(self.angular.net[-1].bias)

            def forward(self, xb: torch.Tensor) -> torch.Tensor:
                r = xb[:, 0:1]
                th = xb[:, 1:2]
                th_n = (th / math.pi) * 2.0 - 1.0
                P, Q = self.radial(r)
                radial_tgt = P / (Q + 1e-6)
                ang_raw = self.angular(th_n)
                ang_pos = torch.nn.functional.softplus(ang_raw) + 0.05
                # Normalize angular branch (detached) so radial learns the scale and training is less degenerate.
                ang_norm = ang_pos / torch.clamp_min(ang_pos.mean().detach(), 1e-6)
                return radial_tgt * ang_norm

        model = FactorizedHybrid().to(device)
        train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb = batch[0].to(device)
            yb = batch[1].to(device)
            rb = batch[2].to(device)
            pred_tgt = model(xb)
            tgt = transform_target(yb, rb)
            return weighted_mse(pred_tgt, tgt, rb)

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            rb = batch[2].to(device)
            pred_tgt = model(xb)
            return inverse_target(pred_tgt, rb)

        def val_mse() -> float:
            if val_loader is None:
                return float("inf")
            return float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=pred_fn))

        if val_loader is not None:
            log = train_loop_with_selection(
                model,
                train_loader,
                loss_fn,
                cfg=train_cfg,
                val_loader=val_loader,
                val_mse_fn=val_mse,
                scheduler=str(args.scheduler),
                eta_min=(float(args.eta_min) if args.eta_min is not None else None),
                restore_best=not bool(args.no_restore_best),
            )
        else:
            log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)

        def bench_predict(xb: torch.Tensor) -> torch.Tensor:
            out_tgt = model(xb.to(device))
            if target_mode == "dose":
                return out_tgt
            if target_mode == "log_dose":
                return torch.exp(out_tgt) - float(args.log_dose_eps)
            r2 = torch.clamp_min(xb[:, 0:1].to(device), 1e-12) ** 2
            return out_tgt / r2

        bench = maybe_microbench(predict_fn=bench_predict, label=f"{factorized_method}_forward")

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        val_mse_final = float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=pred_fn)) if val_loader is not None else None
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        res = {
            "model_type": "FactorizedHybrid",
            "config": {
                "radial": "ProjectivePQ(r)->decoded",
                "angular": f"SIREN(theta) w0={float(args.siren_w0)}",
                "hidden_dims": list(args.hidden_dims),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "lr": float(args.lr),
                "r_reweight_alpha": float(args.r_reweight_alpha),
                "r_reweight_tau": float(r_reweight_tau),
                "target_transform": target_mode,
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": val_mse_final,
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
                "val_mse_history": getattr(log, "val_mse_history", None),
                "best_epoch": getattr(log, "best_epoch", None),
                "best_val_mse": getattr(log, "best_val_mse", None),
                "restored_best": getattr(log, "restored_best", False),
            },
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual[factorized_method] = _to_builtin(res)
        add_row(
            method=factorized_method,
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(log.training_time_s),
            avg_epoch_time=float(log.avg_epoch_time_s),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes="Factorized: ProjectivePQ(r) × SIREN(theta) (Torch baseline; not SCM strict inference)",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if "LogMLP" in enabled and task == "primary":
        if target_mode != "dose":
            raise SystemExit("LogMLP baseline is only supported with --target=dose (use --target=log_dose to run everything in log space).")
        # Train on log(y+eps) to handle dynamic range.
        log_eps = float(args.log_dose_eps)
        y_train_log = torch.log(torch.clamp_min(y_tr, 0.0) + log_eps)
        train_loader_log = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(x_tr, y_train_log, r_tr),
            batch_size=int(args.batch_size),
            shuffle=True,
        )
        model = MLP(MLPConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims))).to(device)
        train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb = batch[0].to(device)
            yb = batch[1].to(device)
            rb = batch[2].to(device)
            pred = model(xb)
            w = sample_weights(rb)
            return torch.mean(w * (pred - yb) ** 2)

        @torch.no_grad()
        def val_pred_fn(batch):
            xb = batch[0].to(device)
            out_log = model(xb)
            return torch.exp(out_log) - log_eps

        def val_mse() -> float:
            if val_loader is None:
                return float("inf")
            return float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=val_pred_fn))

        if val_loader is not None:
            log = train_loop_with_selection(
                model,
                train_loader_log,
                loss_fn,
                cfg=train_cfg,
                val_loader=val_loader,
                val_mse_fn=val_mse,
                scheduler=str(args.scheduler),
                eta_min=(float(args.eta_min) if args.eta_min is not None else None),
                restore_best=not bool(args.no_restore_best),
            )
        else:
            log = train_loop(model, train_loader_log, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: model(xb.to(device)), label="LogMLP_forward")

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            out_log = model(xb)
            return torch.exp(out_log) - log_eps

        # Evaluate against the original y targets (not log space).
        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        val_mse_final = float(evaluate_regression_mse(model, val_loader, device=device, predict_fn=pred_fn)) if val_loader is not None else None
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        res = {
            "model_type": "LogMLP",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "lr": float(args.lr),
                "log_dose_eps": float(log_eps),
                "r_reweight_alpha": float(args.r_reweight_alpha),
                "r_reweight_tau": float(r_reweight_tau),
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": val_mse_final,
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
                "val_mse_history": getattr(log, "val_mse_history", None),
                "best_epoch": getattr(log, "best_epoch", None),
                "best_val_mse": getattr(log, "best_val_mse", None),
                "restored_best": getattr(log, "restored_best", False),
            },
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": int(args.seed),
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["LogMLP"] = _to_builtin(res)
        add_row(
            method="LogMLP",
            params=res["n_parameters"],
            epochs=int(args.epochs),
            train_mse=float(train_metrics["mse"]),
            test_mse=float(test_metrics["mse"]),
            training_time=float(log.training_time_s),
            avg_epoch_time=float(log.avg_epoch_time_s),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"log(y+{log_eps:.0e}) MLP",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    def train_projective_decoded(method: str, *, decode_fn, extra_notes: str) -> None:
        model = ProjectivePQ(ProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones")).to(device)
        train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb = batch[0].to(device)
            yb = batch[1].to(device)
            rb = batch[2].to(device)
            P, Q = model(xb)
            pred_tgt = decode_fn(P, Q)
            tgt = transform_target(yb, rb)
            return weighted_mse(pred_tgt, tgt, rb)

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)

        def _bench_predict(xb: torch.Tensor) -> torch.Tensor:
            out_tgt = decode_fn(*model(xb.to(device)))
            if target_mode == "dose":
                return out_tgt
            if target_mode == "log_dose":
                return torch.exp(out_tgt) - float(args.log_dose_eps)
            r2 = torch.clamp_min(xb[:, 0:1].to(device), 1e-12) ** 2
            return out_tgt / r2

        bench = maybe_microbench(predict_fn=_bench_predict, label=f"{method}_forward")

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            rb = batch[2].to(device)
            P, Q = model(xb)
            pred_tgt = decode_fn(P, Q)
            return inverse_target(pred_tgt, rb)

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        res = {
            "model_type": "ProjectivePQ",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "epochs": int(args.epochs),
                "batch_size": int(args.batch_size),
                "lr": float(args.lr),
                "r_reweight_alpha": float(args.r_reweight_alpha),
                "r_reweight_tau": float(r_reweight_tau),
                "decode": str(extra_notes),
                "target_transform": target_mode,
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
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
            notes=f"{extra_notes}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if "Rational+ε" in enabled:
        eps = float(args.eps)
        train_projective_decoded("Rational+ε", decode_fn=lambda P, Q: P / (Q + eps), extra_notes=f"eps={eps:.0e}")

    if "Smooth" in enabled:
        alpha = float(args.alpha)
        train_projective_decoded("Smooth", decode_fn=lambda P, Q: P / torch.sqrt(Q * Q + (alpha * alpha)), extra_notes=f"alpha={alpha:.0e}")

    if "LearnableEps" in enabled:
        model = ProjectivePQ(ProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones")).to(device)
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
                xb, yb, rb = batch[0].to(device), batch[1].to(device), batch[2].to(device)
                P, Q = model(xb)
                pred_tgt = decode(P, Q)
                tgt = transform_target(yb, rb)
                loss = weighted_mse(pred_tgt, tgt, rb)
                loss.backward()
                opt.step()
                batch_losses.append(float(loss.detach().cpu().item()))
            losses.append(sum(batch_losses) / max(1, len(batch_losses)))
        training_time = float(time.perf_counter() - t0)

        @torch.no_grad()
        def pred_fn(batch):
            xb, rb = batch[0].to(device), batch[2].to(device)
            P, Q = model(xb)
            pred_tgt = decode(P, Q)
            return inverse_target(pred_tgt, rb)

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=pred_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        eps_final = float(torch.nn.functional.softplus(log_eps).detach().cpu().item())
        def _bench_predict(xb: torch.Tensor) -> torch.Tensor:
            out_tgt = decode(*model(xb.to(device)))
            if target_mode == "dose":
                return out_tgt
            if target_mode == "log_dose":
                return torch.exp(out_tgt) - float(args.log_dose_eps)
            r2 = torch.clamp_min(xb[:, 0:1].to(device), 1e-12) ** 2
            return out_tgt / r2

        bench = maybe_microbench(predict_fn=_bench_predict, label="LearnableEps_forward")
        res = {
            "model_type": "LearnableEps",
            "config": {"eps_final": float(eps_final), "hidden_dims": list(args.hidden_dims), "target_transform": target_mode},
            "training_results": {"training_time": training_time, "training_history": losses, "optimizer_steps": steps, "final_train_mse": train_metrics["mse"], "final_val_mse": train_metrics["mse"]},
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
            "n_parameters": int(sum(p.numel() for p in model.parameters())) + 1,
            "training_time": training_time,
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
            training_time=float(training_time),
            avg_epoch_time=float(training_time / max(1, int(args.epochs))),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"eps_final≈{eps_final:.2e}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if "EpsEnsemble" in enabled:
        eps_list = [float(x) for x in args.ens_eps]
        members: List[Tuple[float, ProjectivePQ]] = []
        total_params = 0
        total_train_time = 0.0
        total_steps = 0
        for eps in eps_list:
            m = ProjectivePQ(ProjectivePQConfig(input_dim=input_dim, hidden_dims=tuple(int(x) for x in args.hidden_dims), q_anchor="ones")).to(device)
            train_cfg = TrainConfig(epochs=int(args.epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

            def loss_fn(batch, *, _eps: float = eps, _m=m):
                xb, yb, rb = batch[0].to(device), batch[1].to(device), batch[2].to(device)
                P, Q = _m(xb)
                pred_tgt = P / (Q + float(_eps))
                tgt = transform_target(yb, rb)
                return weighted_mse(pred_tgt, tgt, rb)

            log = train_loop(m, train_loader, loss_fn, cfg=train_cfg)
            total_train_time += float(log.training_time_s)
            total_steps += int(log.optimizer_steps)
            total_params += int(sum(p.numel() for p in m.parameters()))
            members.append((float(eps), m))

        @torch.no_grad()
        def pred_fn(batch):
            xb = batch[0].to(device)
            rb = batch[2].to(device)
            outs = []
            for eps, m in members:
                P, Q = m(xb)
                outs.append(P / (Q + float(eps)))
            pred_tgt = torch.mean(torch.stack(outs, dim=0), dim=0)
            return inverse_target(pred_tgt, rb)

        @torch.no_grad()
        def bench_predict(xb: torch.Tensor) -> torch.Tensor:
            outs = []
            for eps, m in members:
                P, Q = m(xb.to(device))
                outs.append(P / (Q + float(eps)))
            pred_tgt = torch.mean(torch.stack(outs, dim=0), dim=0)
            if target_mode == "dose":
                return pred_tgt
            if target_mode == "log_dose":
                return torch.exp(pred_tgt) - float(args.log_dose_eps)
            r2 = torch.clamp_min(xb[:, 0:1].to(device), 1e-12) ** 2
            return pred_tgt / r2

        train_metrics = evaluate_regression(members[0][1], train_eval_loader, device=device, predict_fn=pred_fn)
        test_metrics = evaluate_regression(members[0][1], test_loader, device=device, predict_fn=pred_fn)
        b_mse, b_counts = _bucket_mse(test_metrics["per_sample_mse"], r_test_list, edges)
        nf = near_field_metrics(
            [float(p[0]) for p in test_metrics["predictions"]],
            [float(t[0]) for t in y_test.tolist()],
            r_test_list,
            r_thr=float(args.r_near_mm),
        )
        bench = maybe_microbench(predict_fn=bench_predict, label="EpsEnsemble_forward")
        res = {
            "model_type": "EpsEnsemble",
            "config": {"ens_eps": eps_list, "hidden_dims": list(args.hidden_dims), "target_transform": target_mode},
            "training_results": {"training_time": total_train_time, "optimizer_steps": total_steps},
            "test_metrics": test_metrics,
            "near_field_metrics": nf,
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
            notes=f"members={eps_list}",
            bucket_counts=b_counts,
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    comp["resources"]["peak_rss_mb"] = peak_rss_mb()
    comp["resources"]["torch_cuda_peak_mb"] = torch_cuda_peak_mb()

    # Summary
    mses = [row.get("Test_MSE") for row in table if isinstance(row, dict)]
    mses = [float(x) for x in mses if isinstance(x, (int, float)) and math.isfinite(float(x))]
    comp["summary"]["methods_tested"] = int(len(table))
    if mses:
        comp["summary"]["best_mse"] = float(min(mses))

    out_json = os.path.join(args.output_dir, "comprehensive_comparison.json")
    out_csv = os.path.join(args.output_dir, "comparison_table.csv")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(_to_builtin(comp), fh, indent=2)

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
