from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def _finite_float(x: Any) -> Optional[float]:
    if not isinstance(x, (int, float)):
        return None
    v = float(x)
    # Treat +/-inf as valid extreme scores (useful for safety-conservative invalid policies).
    if math.isnan(v):
        return None
    return v


def _sorted_pairs(y_true: List[int], y_score: List[float]) -> List[Tuple[float, int]]:
    pairs: List[Tuple[float, int]] = []
    for yt, ys in zip(y_true, y_score):
        s = _finite_float(ys)
        if s is None:
            continue
        pairs.append((float(s), 1 if int(yt) else 0))
    pairs.sort(key=lambda t: t[0], reverse=True)
    return pairs


def roc_auc(y_true: List[int], y_score: List[float]) -> Optional[float]:
    pairs = _sorted_pairs(y_true, y_score)
    if not pairs:
        return None
    n_pos = sum(y for _s, y in pairs)
    n_neg = len(pairs) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    tp = 0
    fp = 0
    prev_score = None
    auc = 0.0
    prev_fpr = 0.0
    prev_tpr = 0.0
    for score, y in pairs:
        if prev_score is None or score != prev_score:
            # trapezoid area between prev point and current point
            auc += (prev_fpr - float(fp) / n_neg) * (prev_tpr + float(tp) / n_pos) / 2.0
            prev_fpr = float(fp) / n_neg
            prev_tpr = float(tp) / n_pos
            prev_score = score
        if y == 1:
            tp += 1
        else:
            fp += 1
    auc += (prev_fpr - 1.0) * (prev_tpr + 1.0) / 2.0
    return float(-auc)  # accumulated with decreasing fpr, flip sign


def pr_auc(y_true: List[int], y_score: List[float]) -> Optional[float]:
    pairs = _sorted_pairs(y_true, y_score)
    if not pairs:
        return None
    n_pos = sum(y for _s, y in pairs)
    if n_pos == 0:
        return None
    tp = 0
    fp = 0
    # Step-wise integral over recall, using precision at each threshold (standard AP-style).
    ap = 0.0
    prev_recall = 0.0
    for _score, y in pairs:
        if y == 1:
            tp += 1
        else:
            fp += 1
        recall = float(tp) / float(n_pos)
        precision = float(tp) / float(max(1, tp + fp))
        ap += (recall - prev_recall) * precision
        prev_recall = recall
    return float(ap)


def pr_curve(y_true: List[int], y_score: List[float]) -> Dict[str, List[float]]:
    pairs = _sorted_pairs(y_true, y_score)
    n_pos = sum(y for _s, y in pairs)
    if not pairs or n_pos == 0:
        return {"precision": [], "recall": [], "thresholds": []}
    tp = 0
    fp = 0
    precision: List[float] = []
    recall: List[float] = []
    thresholds: List[float] = []
    prev_score = None
    for score, y in pairs:
        if prev_score is None or score != prev_score:
            if tp + fp > 0:
                precision.append(float(tp) / float(tp + fp))
                recall.append(float(tp) / float(n_pos))
                thresholds.append(float(score))
            prev_score = score
        if y == 1:
            tp += 1
        else:
            fp += 1
    if tp + fp > 0:
        precision.append(float(tp) / float(tp + fp))
        recall.append(float(tp) / float(n_pos))
        thresholds.append(float(pairs[-1][0]))
    return {"precision": precision, "recall": recall, "thresholds": thresholds}


def fnr_at_fpr(
    y_true: List[int], y_score: List[float], *, fpr_budget: float
) -> Optional[Dict[str, float]]:
    pairs = _sorted_pairs(y_true, y_score)
    if not pairs:
        return None
    n_pos = sum(y for _s, y in pairs)
    n_neg = len(pairs) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None

    tp = 0
    fp = 0
    best: Optional[Dict[str, float]] = None
    prev_score = None
    for score, y in pairs:
        # Update counts *after* crossing threshold (score is inclusive).
        if y == 1:
            tp += 1
        else:
            fp += 1
        if prev_score is None or score != prev_score:
            fpr = float(fp) / float(n_neg)
            fnr = float(n_pos - tp) / float(n_pos)
            if fpr <= float(fpr_budget) + 1e-12:
                cand = {"threshold": float(score), "fpr": float(fpr), "fnr": float(fnr)}
                if best is None or cand["fnr"] < best["fnr"]:
                    best = cand
            prev_score = score
    return best


def binary_summary(
    y_true: List[int],
    y_score: List[float],
    *,
    fpr_budget: float,
) -> Dict[str, Any]:
    n = 0
    n_pos = 0
    n_neg = 0
    for yt, ys in zip(y_true, y_score):
        s = _finite_float(ys)
        if s is None:
            continue
        n += 1
        if int(yt):
            n_pos += 1
        else:
            n_neg += 1
    out: Dict[str, Any] = {
        "n_valid": int(n),
        "n_pos": int(n_pos),
        "n_neg": int(n_neg),
        "auroc": roc_auc(y_true, y_score),
        "auprc": pr_auc(y_true, y_score),
        "fnr_at_fpr": fnr_at_fpr(y_true, y_score, fpr_budget=float(fpr_budget)),
    }
    return out
