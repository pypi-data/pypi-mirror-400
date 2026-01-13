#!/usr/bin/env python3
"""
Torch-first RR IK baseline comparator (Phase 12).

Produces:
  - comprehensive_comparison.json
  - comparison_table.csv

Schema is intentionally compatible with the paper suite aggregation scripts.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import torch
from torch.utils.data import DataLoader, TensorDataset

from examples.baselines.dls_solver import DLSConfig, run_dls_reference
from examples.torch_baselines.models import TorchMLP, TorchMLPConfig, TorchMLPWithPoleHead, build_projective_rr_model
from examples.torch_baselines.rr_dataset import DEFAULT_BUCKET_EDGES, dataset_info_dict, dataset_info
from examples.torch_baselines.trainer import TrainConfig, evaluate_regression, train_loop
from zeroproof.metrics.pole_2d import compute_pole_metrics_2d
from zeroproofml.experiment_protocol import protocol_v1
from zeroproofml.benchmark import TorchMicrobenchConfig, torch_microbench
from zeroproofml.resources import collect_system_info, peak_rss_mb, torch_cuda_peak_mb


def _to_builtin(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj):
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return obj
    if isinstance(obj, dict):
        return {k: _to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_builtin(v) for v in obj]
    return obj


def _git_short_sha() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        s = out.decode("utf-8", "replace").strip()
        return s or "nogit"
    except Exception:
        return "nogit"


def _collect_env_info() -> Dict[str, Any]:
    env: Dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_sha": _git_short_sha(),
        "torch": getattr(torch, "__version__", None),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": getattr(torch.version, "cuda", None),
    }
    return env


def _load_dataset_metadata(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        md = d.get("metadata")
        return md if isinstance(md, dict) else {}
    except Exception:
        return {}


def _infer_dls_lambda_from_metadata(md: Dict[str, Any], default: float = 0.01) -> float:
    try:
        gen = md.get("generation")
        if isinstance(gen, dict) and "damping_factor" in gen:
            return float(gen.get("damping_factor"))
    except Exception:
        pass
    return float(default)


def _bucket_key(edges: List[float], i: int) -> str:
    lo = edges[i]
    hi = edges[i + 1]
    lo_s = f"{lo:.0e}" if math.isfinite(lo) else "inf"
    hi_s = f"{hi:.0e}" if math.isfinite(hi) else "inf"
    return f"({lo_s},{hi_s}]"


def _bucketize_detj(detj: float, edges: List[float]) -> int:
    for b in range(len(edges) - 1):
        lo, hi = edges[b], edges[b + 1]
        if (detj >= lo if b == 0 else detj > lo) and detj <= hi:
            return b
    return len(edges) - 2


def _compute_bucket_mse(per_sample_mse: List[float], detj_list: List[float], edges: List[float]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    per_bucket: Dict[str, List[float]] = {_bucket_key(edges, i): [] for i in range(len(edges) - 1)}
    bucket_counts: Dict[str, int] = {_bucket_key(edges, i): 0 for i in range(len(edges) - 1)}
    for mse, dj in zip(per_sample_mse, detj_list):
        b = _bucketize_detj(float(dj), edges)
        k = _bucket_key(edges, b)
        bucket_counts[k] += 1
        if isinstance(mse, (int, float)) and math.isfinite(float(mse)):
            per_bucket[k].append(float(mse))
    bucket_mse: Dict[str, Any] = {}
    for k, vals in per_bucket.items():
        bucket_mse[k] = (sum(vals) / len(vals)) if vals else None
    return bucket_mse, bucket_counts


def _set_seed(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(int(seed))
    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))


def _tensor_xy(x: List[List[float]], y: List[List[float]], idx: List[int]) -> Tuple[torch.Tensor, torch.Tensor]:
    xs = torch.tensor([x[i] for i in idx], dtype=torch.float32)
    ys = torch.tensor([y[i] for i in idx], dtype=torch.float32)
    return xs, ys


def _infer_device(req: str) -> str:
    if req == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if req == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return req


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Torch-first RR baselines comparator (Phase 12)")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Subset: mlp mlp_pole rational_eps smooth learnable_eps eps_ens dls dls_adaptive",
    )
    ap.add_argument("--mlp_epochs", type=int, default=2)
    ap.add_argument("--rat_epochs", type=int, default=5)
    ap.add_argument("--batch_size", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--hidden_dims", nargs="*", type=int, default=[64, 64])
    ap.add_argument("--numerator_degree", type=int, default=3)
    ap.add_argument("--denominator_degree", type=int, default=2)
    ap.add_argument("--eps", type=float, default=1e-2, help="Fixed epsilon for Rational+ε")
    ap.add_argument("--alpha", type=float, default=1e-1, help="Fixed alpha for Smooth")
    ap.add_argument("--ens_eps", nargs="*", type=float, default=[1e-4, 1e-3, 1e-2], help="EpsEnsemble eps list")
    ap.add_argument("--lambda_pole", type=float, default=0.1, help="Pole head loss weight for MLP+PoleHead")
    ap.add_argument("--pole_detj_threshold", type=float, default=1e-3, help="Near-pole threshold for pole head")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    ap.add_argument(
        "--eval-dls-predictive",
        action="store_true",
        help=(
            "Make DLS/DLS-Adaptive emit per-sample one-step Δθ predictions and report predictive "
            "test_metrics/pole_metrics apples-to-apples with learned models. When enabled, DLS is "
            "run with max_iterations=1 on the test subset."
        ),
    )
    ap.add_argument("--no-microbench", action="store_true", help="Skip microbenchmark timing tiers")
    ap.add_argument("--microbench-iters", type=int, default=120)
    ap.add_argument("--microbench-warmup", type=int, default=30)
    args = ap.parse_args(argv)

    os.makedirs(args.output_dir, exist_ok=True)
    device = _infer_device(str(args.device))
    _set_seed(args.seed)

    enabled = set(
        args.models
        if args.models
        else [
            "mlp",
            "mlp_pole",
            "rational_eps",
            "smooth",
            "learnable_eps",
            "eps_ens",
            "dls",
            "dls_adaptive",
        ]
    )

    info, samples, x, y = dataset_info(args.dataset, quick=bool(args.quick), edges=DEFAULT_BUCKET_EDGES)
    md = _load_dataset_metadata(str(args.dataset))
    dls_lambda = _infer_dls_lambda_from_metadata(md, default=0.01)
    x_train, y_train = _tensor_xy(x, y, info.train_indices)
    x_test, y_test = _tensor_xy(x, y, info.test_indices)

    train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=int(args.batch_size), shuffle=True)
    test_loader = DataLoader(TensorDataset(x_test, y_test), batch_size=int(args.batch_size), shuffle=False)
    train_eval_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=int(args.batch_size), shuffle=False)

    # detJ for buckets on test subset (RR: |sin(theta2)|)
    detj_test: List[float] = []
    for i in info.test_indices:
        th2 = float(samples[i]["theta2"])
        detj_test.append(abs(math.sin(th2)))

    individual: Dict[str, Any] = {}
    table: List[Dict[str, Any]] = []
    edges = list(info.bucket_edges)

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

    def add_row(
        *,
        method: str,
        params: int | str,
        epochs: int | str,
        train_mse: Any,
        test_mse: Any,
        training_time: float,
        avg_epoch_time: Any,
        success_rate: float,
        inference_us_per_sample: Any,
        notes: str,
        counts_b0_b3: List[int],
        micro_us_per_sample_b1: Any = None,
        micro_us_per_sample_bN: Any = None,
    ) -> None:
        table.append(
            {
                "Method": method,
                "Parameters": params,
                "Epochs": epochs,
                "Train_MSE": train_mse,
                "Test_MSE": test_mse,
                "Training_Time": training_time,
                "Avg_Epoch_Time": avg_epoch_time,
                "Success_Rate": success_rate,
                "Inference_us_per_sample": inference_us_per_sample,
                "Micro_us_per_sample_b1": micro_us_per_sample_b1,
                f"Micro_us_per_sample_b{int(args.batch_size)}": micro_us_per_sample_bN,
                "Notes": notes,
                "NearPoleCountsB0_B3": counts_b0_b3,
            }
        )

    def counts_b0_b3(bucket_counts: Dict[str, int]) -> List[int]:
        out = []
        for i in range(min(4, len(edges) - 1)):
            out.append(int(bucket_counts.get(_bucket_key(edges, i), 0)))
        while len(out) < 4:
            out.append(0)
        return out

    # 1) Torch MLP
    if "mlp" in enabled:
        cfg = TorchMLPConfig(hidden_dims=tuple(int(x) for x in args.hidden_dims))
        model = TorchMLP(cfg)
        train_cfg = TrainConfig(epochs=int(args.mlp_epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb, yb = batch[0].to(device), batch[1].to(device)
            pred = model(xb)
            return torch.mean((pred - yb) ** 2)

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: model(xb), label="rr_mlp_forward")
        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=lambda b: model(b[0].to(device)))
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=lambda b: model(b[0].to(device)))
        b_mse, b_counts = _compute_bucket_mse(test_metrics["per_sample_mse"], detj_test, edges)
        pole = compute_pole_metrics_2d(x_test.tolist(), test_metrics["predictions"])

        res = {
            "model_type": "TorchMLP",
            "config": {"hidden_dims": list(args.hidden_dims), "lr": float(args.lr), "epochs": int(args.mlp_epochs), "batch_size": int(args.batch_size)},
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "pole_metrics": pole,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": args.seed,
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["MLP"] = _to_builtin(res)
        add_row(
            method="MLP",
            params=res["n_parameters"],
            epochs=int(args.mlp_epochs),
            train_mse=train_metrics["mse"],
            test_mse=test_metrics["mse"],
            training_time=log.training_time_s,
            avg_epoch_time=log.avg_epoch_time_s,
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"hidden={list(args.hidden_dims)}",
            counts_b0_b3=counts_b0_b3(b_counts),
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # 1b) Torch MLP+PoleHead
    if "mlp_pole" in enabled:
        cfg = TorchMLPConfig(hidden_dims=tuple(int(x) for x in args.hidden_dims))
        model = TorchMLPWithPoleHead(cfg)
        train_cfg = TrainConfig(epochs=int(args.mlp_epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)
        bce = torch.nn.BCEWithLogitsLoss()

        def pole_label(xb: torch.Tensor) -> torch.Tensor:
            theta2 = xb[:, 1]
            detj = torch.abs(torch.sin(theta2))
            return (detj <= float(args.pole_detj_threshold)).float().unsqueeze(-1)

        def loss_fn(batch):
            xb, yb = batch[0].to(device), batch[1].to(device)
            pred, pole_logit = model(xb)
            mse = torch.mean((pred - yb) ** 2)
            pole = bce(pole_logit, pole_label(xb))
            return mse + float(args.lambda_pole) * pole

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(predict_fn=lambda xb: model(xb)[0], label="rr_mlp_pole_forward")
        train_metrics = evaluate_regression(
            model,
            train_eval_loader,
            device=device,
            predict_fn=lambda b: model(b[0].to(device))[0],
        )
        test_metrics = evaluate_regression(
            model,
            test_loader,
            device=device,
            predict_fn=lambda b: model(b[0].to(device))[0],
        )
        b_mse, b_counts = _compute_bucket_mse(test_metrics["per_sample_mse"], detj_test, edges)
        pole = compute_pole_metrics_2d(x_test.tolist(), test_metrics["predictions"])
        res = {
            "model_type": "TorchMLP+PoleHead",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.mlp_epochs),
                "batch_size": int(args.batch_size),
                "pole_detj_threshold": float(args.pole_detj_threshold),
                "lambda_pole": float(args.lambda_pole),
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "pole_metrics": pole,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": args.seed,
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["MLP+PoleHead"] = _to_builtin(res)
        add_row(
            method="MLP+PoleHead",
            params=res["n_parameters"],
            epochs=int(args.mlp_epochs),
            train_mse=train_metrics["mse"],
            test_mse=test_metrics["mse"],
            training_time=log.training_time_s,
            avg_epoch_time=log.avg_epoch_time_s,
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"hidden={list(args.hidden_dims)} pole_head=on",
            counts_b0_b3=counts_b0_b3(b_counts),
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    def train_projective_decoded(
        *,
        method: str,
        decode_fn,
        epochs: int,
        notes: str,
        extra_result: Optional[Dict[str, Any]] = None,
    ) -> None:
        model = build_projective_rr_model(
            hidden_dims=args.hidden_dims,
            numerator_degree=int(args.numerator_degree),
            denominator_degree=int(args.denominator_degree),
            q_anchor="ones",
            enable_pole_head=False,
        )
        train_cfg = TrainConfig(epochs=int(epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

        def loss_fn(batch):
            xb, yb = batch[0].to(device), batch[1].to(device)
            P, Q = model(xb)
            pred = decode_fn(P, Q)
            return torch.mean((pred - yb) ** 2)

        log = train_loop(model, train_loader, loss_fn, cfg=train_cfg)
        bench = maybe_microbench(
            predict_fn=lambda xb: decode_fn(*model(xb)),
            label=f"rr_{method}_forward",
        )

        def predict_fn(batch):
            xb = batch[0].to(device)
            P, Q = model(xb)
            return decode_fn(P, Q)

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=predict_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=predict_fn)
        b_mse, b_counts = _compute_bucket_mse(test_metrics["per_sample_mse"], detj_test, edges)
        pole = compute_pole_metrics_2d(x_test.tolist(), test_metrics["predictions"])

        res = {
            "model_type": "TorchProjectivePQ",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(epochs),
                "batch_size": int(args.batch_size),
                "numerator_degree": int(args.numerator_degree),
                "denominator_degree": int(args.denominator_degree),
            },
            "training_results": {
                "training_time": log.training_time_s,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": log.losses,
                "optimizer_steps": log.optimizer_steps,
            },
            "test_metrics": test_metrics,
            "pole_metrics": pole,
            "n_parameters": int(sum(p.numel() for p in model.parameters())),
            "training_time": log.training_time_s,
            "seed": args.seed,
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        if extra_result:
            res.update(extra_result)
        individual[method] = _to_builtin(res)
        add_row(
            method=method,
            params=res["n_parameters"],
            epochs=int(epochs),
            train_mse=train_metrics["mse"],
            test_mse=test_metrics["mse"],
            training_time=log.training_time_s,
            avg_epoch_time=log.avg_epoch_time_s,
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=notes,
            counts_b0_b3=counts_b0_b3(b_counts),
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # 2) Rational+ε / Smooth / LearnableEps / EpsEnsemble
    if "rational_eps" in enabled:
        eps = float(args.eps)
        train_projective_decoded(
            method="Rational+ε",
            decode_fn=lambda P, Q: P / (Q + eps),
            epochs=int(args.rat_epochs),
            notes=f"eps={eps}",
            extra_result={"epsilon": eps},
        )

    if "smooth" in enabled:
        alpha = float(args.alpha)
        train_projective_decoded(
            method="Smooth",
            decode_fn=lambda P, Q: P / torch.sqrt(Q * Q + (alpha * alpha)),
            epochs=int(args.rat_epochs),
            notes=f"alpha={alpha}",
            extra_result={"alpha": alpha},
        )

    if "learnable_eps" in enabled:
        # Learn log-eps (softplus) jointly with model parameters.
        model = build_projective_rr_model(
            hidden_dims=args.hidden_dims,
            numerator_degree=int(args.numerator_degree),
            denominator_degree=int(args.denominator_degree),
            q_anchor="ones",
            enable_pole_head=False,
        ).to(device)
        log_eps = torch.nn.Parameter(torch.tensor(-6.0, device=device))
        train_cfg = TrainConfig(epochs=int(args.rat_epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)
        opt = torch.optim.Adam(list(model.parameters()) + [log_eps], lr=float(args.lr))

        def decode(P, Q):
            eps = torch.nn.functional.softplus(log_eps)
            return P / (Q + eps)

        losses: List[float] = []
        steps = 0
        t0 = time.perf_counter()
        for _epoch in range(int(train_cfg.epochs)):
            batch_losses = []
            for batch in train_loader:
                steps += 1
                opt.zero_grad(set_to_none=True)
                xb, yb = batch[0].to(device), batch[1].to(device)
                P, Q = model(xb)
                pred = decode(P, Q)
                loss = torch.mean((pred - yb) ** 2)
                loss.backward()
                opt.step()
                batch_losses.append(float(loss.detach().cpu().item()))
            losses.append(sum(batch_losses) / max(1, len(batch_losses)))
        total = float(time.perf_counter() - t0)

        def predict_fn(batch):
            xb = batch[0].to(device)
            P, Q = model(xb)
            return decode(P, Q)

        train_metrics = evaluate_regression(model, train_eval_loader, device=device, predict_fn=predict_fn)
        test_metrics = evaluate_regression(model, test_loader, device=device, predict_fn=predict_fn)
        bench = maybe_microbench(predict_fn=lambda xb: decode(*model(xb)), label="rr_learnable_eps_forward")
        b_mse, b_counts = _compute_bucket_mse(test_metrics["per_sample_mse"], detj_test, edges)
        pole = compute_pole_metrics_2d(x_test.tolist(), test_metrics["predictions"])
        eps_final = float(torch.nn.functional.softplus(log_eps).detach().cpu().item())
        res = {
            "model_type": "TorchLearnableEps",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.rat_epochs),
                "batch_size": int(args.batch_size),
                "numerator_degree": int(args.numerator_degree),
                "denominator_degree": int(args.denominator_degree),
            },
            "training_results": {
                "training_time": total,
                "final_train_mse": train_metrics["mse"],
                "final_val_mse": train_metrics["mse"],
                "training_history": losses,
                "optimizer_steps": steps,
            },
            "test_metrics": {**test_metrics, "eps_final": eps_final},
            "pole_metrics": pole,
            "n_parameters": int(sum(p.numel() for p in model.parameters())) + 1,
            "training_time": total,
            "seed": args.seed,
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["LearnableEps"] = _to_builtin(res)
        add_row(
            method="LearnableEps",
            params=res["n_parameters"],
            epochs=int(args.rat_epochs),
            train_mse=train_metrics["mse"],
            test_mse=test_metrics["mse"],
            training_time=total,
            avg_epoch_time=(total / max(1, int(args.rat_epochs))),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"eps_final≈{eps_final:.2e}",
            counts_b0_b3=counts_b0_b3(b_counts),
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    if "eps_ens" in enabled:
        eps_list = [float(x) for x in args.ens_eps]
        member_results: List[Dict[str, Any]] = []
        member_models = []
        member_train_times: List[float] = []
        member_steps: List[int] = []
        member_params: List[int] = []
        for eps in eps_list:
            model = build_projective_rr_model(
                hidden_dims=args.hidden_dims,
                numerator_degree=int(args.numerator_degree),
                denominator_degree=int(args.denominator_degree),
                q_anchor="ones",
                enable_pole_head=False,
            )
            train_cfg = TrainConfig(epochs=int(args.rat_epochs), lr=float(args.lr), batch_size=int(args.batch_size), device=device)

            def loss_fn(batch, *, _eps=eps, _model=model):
                xb, yb = batch[0].to(device), batch[1].to(device)
                P, Q = _model(xb)
                pred = P / (Q + float(_eps))
                return torch.mean((pred - yb) ** 2)

            log = train_loop(model, train_loader, lambda b, _lf=loss_fn: _lf(b), cfg=train_cfg)
            member_train_times.append(log.training_time_s)
            member_steps.append(log.optimizer_steps)
            member_params.append(int(sum(p.numel() for p in model.parameters())))
            member_models.append(model)
            member_results.append({"eps": eps, "train_time": log.training_time_s, "steps": log.optimizer_steps})

        for m in member_models:
            m.to(device)
            m.eval()

        # Ensemble prediction: average decoded outputs
        def predict_fn(batch):
            xb = batch[0].to(device)
            preds = []
            for model, eps in zip(member_models, eps_list):
                P, Q = model(xb)
                preds.append(P / (Q + float(eps)))
            return torch.mean(torch.stack(preds, dim=0), dim=0)

        def bench_predict(xb: torch.Tensor) -> torch.Tensor:
            preds = []
            for model, eps in zip(member_models, eps_list):
                P, Q = model(xb)
                preds.append(P / (Q + float(eps)))
            return torch.mean(torch.stack(preds, dim=0), dim=0)

        test_metrics = evaluate_regression(member_models[0], test_loader, device=device, predict_fn=predict_fn)
        bench = maybe_microbench(
            predict_fn=bench_predict,
            label="rr_eps_ens_forward",
        )
        b_mse, b_counts = _compute_bucket_mse(test_metrics["per_sample_mse"], detj_test, edges)
        pole = compute_pole_metrics_2d(x_test.tolist(), test_metrics["predictions"])
        total_time = float(sum(member_train_times))
        total_params = int(sum(member_params))
        res = {
            "model_type": "TorchEpsEnsemble",
            "config": {
                "hidden_dims": list(args.hidden_dims),
                "lr": float(args.lr),
                "epochs": int(args.rat_epochs),
                "batch_size": int(args.batch_size),
                "numerator_degree": int(args.numerator_degree),
                "denominator_degree": int(args.denominator_degree),
                "member_eps": eps_list,
            },
            "training_results": {
                "training_time": total_time,
                "optimizer_steps_total": int(sum(member_steps)),
                "members": member_results,
            },
            "test_metrics": test_metrics,
            "pole_metrics": pole,
            "n_parameters": total_params,
            "training_time": total_time,
            "seed": args.seed,
            "near_pole_bucket_mse": {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts},
            "microbench": bench,
        }
        individual["EpsEnsemble"] = _to_builtin(res)
        add_row(
            method="EpsEnsemble",
            params=total_params,
            epochs=int(args.rat_epochs),
            train_mse="N/A",
            test_mse=test_metrics["mse"],
            training_time=total_time,
            avg_epoch_time=(total_time / max(1, int(args.rat_epochs))),
            success_rate=float(test_metrics["success_rate"]),
            inference_us_per_sample=test_metrics.get("inference_us_per_sample"),
            notes=f"members={eps_list}",
            counts_b0_b3=counts_b0_b3(b_counts),
            micro_us_per_sample_b1=micro_us_per_sample(bench, 1),
            micro_us_per_sample_bN=micro_us_per_sample(bench, int(args.batch_size)),
        )

    # 3) DLS references
    if "dls" in enabled:
        dls_cfg = DLSConfig(
            damping_factor=float(dls_lambda),
            max_iterations=(1 if bool(args.eval_dls_predictive) else (1 if args.quick else 100)),
        )
        # Always evaluate DLS on the test subset for correct alignment with bucketization.
        dls_eval_samples = [samples[i] for i in info.test_indices]
        dls_res = run_dls_reference(dls_eval_samples, dls_cfg, output_dir=f"{args.output_dir}/dls", seed=args.seed)
        if bool(args.eval_dls_predictive):
            preds = dls_res.get("predictions", [])
            y_true = y_test.tolist()
            x_inp = x_test.tolist()
            per_sample_mse: List[float] = []
            per_sample_mae: List[float] = []
            n_valid = 0
            for p, t in zip(preds, y_true):
                try:
                    if not (math.isfinite(float(p[0])) and math.isfinite(float(p[1]))):
                        per_sample_mse.append(float("nan"))
                        per_sample_mae.append(float("nan"))
                        continue
                    n_valid += 1
                    mse_i = ((float(p[0]) - float(t[0])) ** 2 + (float(p[1]) - float(t[1])) ** 2) / 2.0
                    mae_i = (abs(float(p[0]) - float(t[0])) + abs(float(p[1]) - float(t[1]))) / 2.0
                    per_sample_mse.append(float(mse_i))
                    per_sample_mae.append(float(mae_i))
                except Exception:
                    per_sample_mse.append(float("nan"))
                    per_sample_mae.append(float("nan"))
            mse_vals = [v for v in per_sample_mse if math.isfinite(float(v))]
            mae_vals = [v for v in per_sample_mae if math.isfinite(float(v))]
            mse = float(sum(mse_vals) / max(1, len(mse_vals))) if mse_vals else float("inf")
            mae = float(sum(mae_vals) / max(1, len(mae_vals))) if mae_vals else float("inf")
            # Use solver timing as inference proxy.
            infer_us = (
                float(dls_res.get("average_solve_time", 0.0)) * 1e6
                if dls_res.get("average_solve_time") is not None
                else None
            )
            dls_res["test_metrics"] = {
                "mse": mse,
                "mae": mae,
                "n_samples": int(len(y_true)),
                "n_valid": int(n_valid),
                "success_rate": (float(n_valid) / float(len(y_true))) if y_true else 0.0,
                "predictions": preds,
                "per_sample_mse": per_sample_mse,
                "per_sample_mae": per_sample_mae,
                "inference_time_total_s": float(dls_res.get("total_evaluation_time", 0.0)),
                "inference_us_per_sample": infer_us,
            }
            b_mse, b_counts = _compute_bucket_mse(per_sample_mse, detj_test, edges)
            dls_res["near_pole_bucket_mse"] = {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts}
            dls_res["pole_metrics"] = compute_pole_metrics_2d(x_inp, preds)
        else:
            b_mse, b_counts = _compute_bucket_mse(dls_res.get("final_errors", []), detj_test, edges)
            dls_res["near_pole_bucket_mse"] = {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts}
            dls_res["pole_metrics"] = {
                "ple": None,
                "sign_consistency": None,
                "slope_error": None,
                "residual_consistency": dls_res.get("average_error", None),
            }
        individual["DLS"] = _to_builtin(dls_res)
        add_row(
            method="DLS",
            params=0,
            epochs="N/A",
            train_mse="N/A",
            test_mse=(
                dls_res.get("test_metrics", {}).get("mse")
                if bool(args.eval_dls_predictive)
                else dls_res.get("average_error", float("inf"))
            ),
            training_time=0.0,
            avg_epoch_time="N/A",
            success_rate=float(
                dls_res.get("test_metrics", {}).get("success_rate")
                if bool(args.eval_dls_predictive)
                else dls_res.get("success_rate", 0.0)
            ),
            inference_us_per_sample=(
                dls_res.get("test_metrics", {}).get("inference_us_per_sample")
                if bool(args.eval_dls_predictive)
                else (
                    float(dls_res.get("average_solve_time", 0.0)) * 1e6
                    if dls_res.get("average_solve_time") is not None
                    else None
                )
            ),
            notes=f"lambda={dls_cfg.damping_factor}" + (" (predictive)" if bool(args.eval_dls_predictive) else ""),
            counts_b0_b3=counts_b0_b3(b_counts),
        )

    if "dls_adaptive" in enabled:
        dls_cfg = DLSConfig(
            damping_factor=float(dls_lambda),
            max_iterations=(1 if bool(args.eval_dls_predictive) else (1 if args.quick else 100)),
            detj_conditioned_damping=True,
            detj_pole_threshold=1e-3,
            detj_transition=5e-4,
            damping_factor_near_pole=0.1,
        )
        # Always evaluate DLS on the test subset for correct alignment with bucketization.
        dls_eval_samples = [samples[i] for i in info.test_indices]
        dls_res = run_dls_reference(dls_eval_samples, dls_cfg, output_dir=f"{args.output_dir}/dls_adaptive", seed=args.seed)
        if bool(args.eval_dls_predictive):
            preds = dls_res.get("predictions", [])
            y_true = y_test.tolist()
            x_inp = x_test.tolist()
            per_sample_mse = []
            per_sample_mae = []
            n_valid = 0
            for p, t in zip(preds, y_true):
                try:
                    if not (math.isfinite(float(p[0])) and math.isfinite(float(p[1]))):
                        per_sample_mse.append(float("nan"))
                        per_sample_mae.append(float("nan"))
                        continue
                    n_valid += 1
                    mse_i = ((float(p[0]) - float(t[0])) ** 2 + (float(p[1]) - float(t[1])) ** 2) / 2.0
                    mae_i = (abs(float(p[0]) - float(t[0])) + abs(float(p[1]) - float(t[1]))) / 2.0
                    per_sample_mse.append(float(mse_i))
                    per_sample_mae.append(float(mae_i))
                except Exception:
                    per_sample_mse.append(float("nan"))
                    per_sample_mae.append(float("nan"))
            mse_vals = [v for v in per_sample_mse if math.isfinite(float(v))]
            mae_vals = [v for v in per_sample_mae if math.isfinite(float(v))]
            mse = float(sum(mse_vals) / max(1, len(mse_vals))) if mse_vals else float("inf")
            mae = float(sum(mae_vals) / max(1, len(mae_vals))) if mae_vals else float("inf")
            infer_us = (
                float(dls_res.get("average_solve_time", 0.0)) * 1e6
                if dls_res.get("average_solve_time") is not None
                else None
            )
            dls_res["test_metrics"] = {
                "mse": mse,
                "mae": mae,
                "n_samples": int(len(y_true)),
                "n_valid": int(n_valid),
                "success_rate": (float(n_valid) / float(len(y_true))) if y_true else 0.0,
                "predictions": preds,
                "per_sample_mse": per_sample_mse,
                "per_sample_mae": per_sample_mae,
                "inference_time_total_s": float(dls_res.get("total_evaluation_time", 0.0)),
                "inference_us_per_sample": infer_us,
            }
            b_mse, b_counts = _compute_bucket_mse(per_sample_mse, detj_test, edges)
            dls_res["near_pole_bucket_mse"] = {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts}
            dls_res["pole_metrics"] = compute_pole_metrics_2d(x_inp, preds)
        else:
            b_mse, b_counts = _compute_bucket_mse(dls_res.get("final_errors", []), detj_test, edges)
            dls_res["near_pole_bucket_mse"] = {"edges": edges, "bucket_mse": b_mse, "bucket_counts": b_counts}
            dls_res["pole_metrics"] = {
                "ple": None,
                "sign_consistency": None,
                "slope_error": None,
                "residual_consistency": dls_res.get("average_error", None),
            }
        individual["DLS-Adaptive"] = _to_builtin(dls_res)
        add_row(
            method="DLS-Adaptive",
            params=0,
            epochs="N/A",
            train_mse="N/A",
            test_mse=(
                dls_res.get("test_metrics", {}).get("mse")
                if bool(args.eval_dls_predictive)
                else dls_res.get("average_error", float("inf"))
            ),
            training_time=0.0,
            avg_epoch_time="N/A",
            success_rate=float(
                dls_res.get("test_metrics", {}).get("success_rate")
                if bool(args.eval_dls_predictive)
                else dls_res.get("success_rate", 0.0)
            ),
            inference_us_per_sample=(
                dls_res.get("test_metrics", {}).get("inference_us_per_sample")
                if bool(args.eval_dls_predictive)
                else (
                    float(dls_res.get("average_solve_time", 0.0)) * 1e6
                    if dls_res.get("average_solve_time") is not None
                    else None
                )
            ),
            notes=("detJ-conditioned damping" + (" (predictive)" if bool(args.eval_dls_predictive) else "")),
            counts_b0_b3=counts_b0_b3(b_counts),
        )

    # Comprehensive JSON
    comprehensive = {
        "protocol": protocol_v1(domain="robotics_rr", suite_name="paper_suite"),
        "resources": {
            "system": collect_system_info(),
            "peak_rss_mb": peak_rss_mb(),
            "torch_cuda_peak_mb": torch_cuda_peak_mb(),
        },
        "global": {
            "seed": args.seed,
            "quick": bool(args.quick),
            "loss_name": "mse_mean",
            "env": _collect_env_info(),
        },
        "dataset_info": dataset_info_dict(info),
        "individual_results": individual,
        "comparison_table": table,
        "summary": {
            "methods_tested": len(table),
            "best_mse": min(
                [float(r["Test_MSE"]) for r in table if isinstance(r.get("Test_MSE"), (int, float))]
            )
            if table
            else None,
        },
    }

    out_json = os.path.join(args.output_dir, "comprehensive_comparison.json")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(_to_builtin(comprehensive), fh, indent=2)

    out_csv = os.path.join(args.output_dir, "comparison_table.csv")
    if table:
        fieldnames: List[str] = []
        for row in table:
            for k in row.keys():
                if k not in fieldnames:
                    fieldnames.append(k)
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(table)

    print("Results saved to:")
    print(f"  - {out_json}")
    print(f"  - {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
