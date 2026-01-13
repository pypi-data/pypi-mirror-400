# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""2D near-pole metrics for the RR arm robotics example.

Ported from v0.3 to provide paper-compatible reporting in v0.4 SCM runs.
Implementation is pure-Python (no NumPy dependency required).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    "compute_ple_to_lines",
    "compute_pole_metrics_2d",
]


def _forward_kinematics(
    theta1: float, theta2: float, L1: float = 1.0, L2: float = 1.0
) -> Tuple[float, float]:
    x = L1 * math.cos(theta1) + L2 * math.cos(theta1 + theta2)
    y = L1 * math.sin(theta1) + L2 * math.sin(theta1 + theta2)
    return x, y


def _wrap_pi(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def compute_residual_consistency(
    test_inputs: List[List[float]],
    predictions: List[List[float]],
    *,
    L1: float = 1.0,
    L2: float = 1.0,
) -> float:
    """Mean squared residual between desired and achieved displacement."""

    if not test_inputs or not predictions:
        return float("inf")
    errs: List[float] = []
    for inp, pred in zip(test_inputs, predictions):
        if len(inp) < 4 or len(pred) < 2:
            continue
        th1, th2, dx_t, dy_t = (float(inp[0]), float(inp[1]), float(inp[2]), float(inp[3]))
        dth1, dth2 = (float(pred[0]), float(pred[1]))
        x0, y0 = _forward_kinematics(th1, th2, L1, L2)
        x1, y1 = _forward_kinematics(th1 + dth1, th2 + dth2, L1, L2)
        dx_hat, dy_hat = (x1 - x0), (y1 - y0)
        errs.append((dx_hat - dx_t) ** 2 + (dy_hat - dy_t) ** 2)
    if not errs:
        return float("inf")
    return float(sum(errs) / len(errs))


def compute_ple_to_lines(
    test_inputs: List[List[float]],
    predictions: List[List[float]],
    *,
    top_k_ratio: float = 0.05,
) -> float:
    """Approximate PLE to analytic singularity lines θ2∈{0,π}."""

    if not test_inputs or not predictions:
        return float("inf")
    n = min(len(test_inputs), len(predictions))
    norms: List[Tuple[int, float]] = []
    for i in range(n):
        pred = predictions[i]
        if len(pred) < 2:
            continue
        norms.append((i, math.hypot(float(pred[0]), float(pred[1]))))
    if not norms:
        return float("inf")
    norms.sort(key=lambda x: x[1], reverse=True)
    k = max(1, int(len(norms) * float(top_k_ratio)))
    top_idx = [idx for idx, _ in norms[:k]]
    dists: List[float] = []
    for i in top_idx:
        th2 = float(test_inputs[i][1])
        d0 = abs(_wrap_pi(th2))
        d_pi = abs(_wrap_pi(th2 - math.pi))
        dists.append(min(d0, d_pi))
    if not dists:
        return float("inf")
    return float(sum(dists) / len(dists))


def compute_sign_consistency_rate(
    test_inputs: List[List[float]],
    predictions: List[List[float]],
    *,
    n_paths: int = 5,
    th1_tol: float = 0.05,
    th2_window: float = 0.2,
) -> float:
    """Estimate sign flip consistency across θ2=0 crossing."""

    if not test_inputs or not predictions:
        return 0.0

    th1_vals = [float(inp[0]) for inp in test_inputs]
    th2_vals = [float(inp[1]) for inp in test_inputs]
    dth2_vals = [float(pred[1]) if len(pred) > 1 else 0.0 for pred in predictions]
    if len(th1_vals) < 2:
        return 0.0

    mn, mx = min(th1_vals), max(th1_vals)
    if n_paths <= 1 or mn == mx:
        anchors = [(mn + mx) / 2.0]
    else:
        step = (mx - mn) / (n_paths - 1)
        anchors = [mn + i * step for i in range(n_paths)]

    flips = 0
    valid = 0
    for a in anchors:
        idx = [
            i
            for i, (th1, th2) in enumerate(zip(th1_vals, th2_vals))
            if abs(th1 - a) <= th1_tol and abs(th2) <= th2_window
        ]
        if len(idx) < 4:
            continue
        before = [dth2_vals[i] for i in idx if th2_vals[i] < 0.0 and dth2_vals[i] != 0.0]
        after = [dth2_vals[i] for i in idx if th2_vals[i] > 0.0 and dth2_vals[i] != 0.0]
        if not before or not after:
            continue
        sign_before = math.copysign(1.0, sum(1.0 if v > 0 else -1.0 for v in before))
        sign_after = math.copysign(1.0, sum(1.0 if v > 0 else -1.0 for v in after))
        valid += 1
        if sign_before != sign_after:
            flips += 1
    return float(flips / valid) if valid > 0 else 0.0


def compute_slope_error_near_pole(
    test_inputs: List[List[float]],
    predictions: List[List[float]],
    *,
    detj_eps: float = 1e-6,
    max_detj: float = 1e-2,
) -> float:
    """Fit slope of log||dθ|| vs log|sin(θ2)| near poles; expect ~-1."""

    if not test_inputs or not predictions:
        return float("inf")
    xs: List[float] = []
    ys: List[float] = []
    for inp, pred in zip(test_inputs, predictions):
        if len(inp) < 2 or len(pred) < 2:
            continue
        th2 = float(inp[1])
        q = abs(math.sin(th2))
        if q <= max_detj:
            xs.append(math.log10(max(float(detj_eps), q)))
            ys.append(math.log10(max(1e-12, math.hypot(float(pred[0]), float(pred[1])))))
    if len(xs) < 5:
        return float("inf")
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0.0:
        return float("inf")
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    return float(abs(slope + 1.0))


def compute_pole_metrics_2d(
    test_inputs: List[List[float]],
    predictions: List[List[float]],
    *,
    L1: float = 1.0,
    L2: float = 1.0,
) -> Dict[str, float]:
    """Compute a bundle of 2D near-pole metrics."""

    return {
        "ple": compute_ple_to_lines(test_inputs, predictions),
        "sign_consistency": compute_sign_consistency_rate(test_inputs, predictions),
        "slope_error": compute_slope_error_near_pole(test_inputs, predictions),
        "residual_consistency": compute_residual_consistency(
            test_inputs, predictions, L1=L1, L2=L2
        ),
    }
