from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_BUCKET_EDGES: List[float] = [0.0, 1e-5, 1e-4, 1e-3, 1e-2, float("inf")]


@dataclass(frozen=True)
class RRDatasetInfo:
    file: str
    hash_sha256: Optional[str]
    n_samples: int
    n_train: int
    n_test: int
    bucket_edges: List[float]
    train_indices: List[int]
    test_indices: List[int]


def sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def load_rr_samples(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise ValueError("Dataset JSON must contain a list at key 'samples'")
    return samples


def samples_to_xy(samples: List[Dict[str, Any]]) -> Tuple[List[List[float]], List[List[float]]]:
    x: List[List[float]] = []
    y: List[List[float]] = []
    for s in samples:
        x.append([float(s["theta1"]), float(s["theta2"]), float(s["dx"]), float(s["dy"])])
        y.append([float(s["dtheta1"]), float(s["dtheta2"])])
    return x, y


def base_split_indices(n: int, train_ratio: float = 0.8) -> Tuple[List[int], List[int]]:
    n_train = int(train_ratio * n)
    train_idx = list(range(n_train))
    test_idx = list(range(n_train, n))
    return train_idx, test_idx


def _bucketize_detj(detj: float, edges: List[float]) -> int:
    for b in range(len(edges) - 1):
        lo, hi = edges[b], edges[b + 1]
        if (detj >= lo if b == 0 else detj > lo) and detj <= hi:
            return b
    return len(edges) - 2


def quick_subsample_indices(
    samples: List[Dict[str, Any]],
    train_idx: List[int],
    test_idx: List[int],
    *,
    edges: List[float] | None = None,
    max_train: int = 2000,
    max_test: int = 500,
) -> Tuple[List[int], List[int]]:
    """
    Deterministic quick subsample that keeps near-pole buckets non-empty where possible.

    Mirrors the legacy comparator's approach to maintain paper parity.
    """
    edges = edges or DEFAULT_BUCKET_EDGES

    def detj_for_i(i: int) -> float:
        th2 = float(samples[i]["theta2"])
        return abs(math.sin(th2))

    def bucketize(idx_list: List[int]) -> Dict[int, List[int]]:
        buckets: Dict[int, List[int]] = {i: [] for i in range(len(edges) - 1)}
        for i in idx_list:
            dj = detj_for_i(i)
            b = _bucketize_detj(dj, edges)
            buckets[b].append(i)
        return buckets

    tb = bucketize(test_idx)
    selected_test: List[int] = []
    # Preselect one from B0–B3 if available
    for b in range(min(4, len(edges) - 1)):
        if tb.get(b):
            selected_test.append(tb[b][0])
            tb[b] = tb[b][1:]
    # Fill remaining in round-robin across buckets, preserving order
    rr_order = [b for b in range(len(edges) - 1) if tb.get(b)]
    ptrs = {b: 0 for b in rr_order}
    while len(selected_test) < min(max_test, len(test_idx)) and rr_order:
        new_rr: List[int] = []
        for b in rr_order:
            blist = tb.get(b, [])
            p = ptrs[b]
            if p < len(blist):
                selected_test.append(blist[p])
                ptrs[b] = p + 1
                if ptrs[b] < len(blist):
                    new_rr.append(b)
            if len(selected_test) >= min(max_test, len(test_idx)):
                break
        rr_order = new_rr
        if not rr_order:
            break
    if len(selected_test) < min(max_test, len(test_idx)):
        remaining = [i for i in test_idx if i not in selected_test]
        selected_test.extend(remaining[: (min(max_test, len(test_idx)) - len(selected_test))])

    selected_train = train_idx[: min(max_train, len(train_idx))]
    return selected_train, selected_test


def dataset_info(
    dataset_path: str,
    *,
    quick: bool,
    train_ratio: float = 0.8,
    edges: Optional[List[float]] = None,
    max_train: int = 2000,
    max_test: int = 500,
) -> Tuple[RRDatasetInfo, List[Dict[str, Any]], List[List[float]], List[List[float]]]:
    samples = load_rr_samples(dataset_path)
    x, y = samples_to_xy(samples)
    train_idx, test_idx = base_split_indices(len(samples), train_ratio=train_ratio)
    edges = edges or DEFAULT_BUCKET_EDGES
    if quick:
        train_idx, test_idx = quick_subsample_indices(
            samples, train_idx, test_idx, edges=edges, max_train=max_train, max_test=max_test
        )
    info = RRDatasetInfo(
        file=str(dataset_path),
        hash_sha256=sha256_file(dataset_path),
        n_samples=len(samples),
        n_train=len(train_idx),
        n_test=len(test_idx),
        bucket_edges=list(edges),
        train_indices=list(train_idx),
        test_indices=list(test_idx),
    )
    return info, samples, x, y


def dataset_info_dict(info: RRDatasetInfo) -> Dict[str, Any]:
    return asdict(info)

