from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class BrachyDatasetInfo:
    file: str
    hash_sha256: Optional[str]
    backend: str
    n_samples: int
    n_train: int
    n_test: int
    input_dim: int
    r_bucket_edges_mm: List[float]
    r_min_mm: float
    r_max_mm: float
    split_by_paramset: bool


def sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def load_brachy_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Dataset must be a JSON object")
    return data


def flatten_xy(
    data: Dict[str, Any],
    *,
    dataset_path: str | None = None,
) -> Tuple[
    BrachyDatasetInfo,
    List[List[float]],
    List[float],
    List[float],
    List[float],
    List[int],
    List[int],
    List[int],
]:
    md = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise ValueError("Dataset JSON must contain a list at key 'samples'")

    x: List[List[float]] = []
    y: List[float] = []
    r_mm: List[float] = []
    theta: List[float] = []
    param_ids: List[int] = []
    train_idx: List[int] = []
    test_idx: List[int] = []

    for s in samples:
        if not isinstance(s, dict):
            continue
        xv = s.get("x")
        if not isinstance(xv, list) or len(xv) < 2:
            continue
        idx = len(x)
        x.append([float(xv[0]), float(xv[1])])
        y.append(float(s.get("y_primary", float("nan"))))
        r_mm.append(float(s.get("r_mm", xv[0])))
        theta.append(float(s.get("theta_rad", xv[1])))
        param_ids.append(int(s.get("param_id", -1)))
        split = str(s.get("split", "")).lower()
        if split == "train":
            train_idx.append(idx)
        elif split == "test":
            test_idx.append(idx)

    if not train_idx or not test_idx:
        raise ValueError("Dataset must contain non-empty train and test splits")

    edges_raw = md.get("r_bucket_edges_mm") or []
    try:
        edges = [float(e) for e in edges_raw]
    except Exception:
        edges = []
    info = BrachyDatasetInfo(
        file=str(dataset_path) if dataset_path is not None else "<in-memory>",
        hash_sha256=(sha256_file(dataset_path) if dataset_path is not None else None),
        backend=str(md.get("backend", "unknown")),
        n_samples=int(len(x)),
        n_train=int(len(train_idx)),
        n_test=int(len(test_idx)),
        input_dim=int(len(x[0]) if x else 0),
        r_bucket_edges_mm=edges,
        r_min_mm=float(md.get("r_min_mm", 0.0) or 0.0),
        r_max_mm=float(md.get("r_max_mm", 0.0) or 0.0),
        split_by_paramset=bool(md.get("split_by_paramset", False)),
    )
    return info, x, y, r_mm, theta, param_ids, train_idx, test_idx


def flatten_xy_with_prior(
    data: Dict[str, Any],
    *,
    dataset_path: str | None = None,
) -> Tuple[
    BrachyDatasetInfo,
    List[List[float]],
    List[float],
    List[float],
    List[float],
    List[float],
    List[int],
    List[int],
    List[int],
]:
    """
    Like flatten_xy, but also returns TG43 prior values (if present).

    Returns:
      info, x, y_gt, y_tg43, r_mm, theta, param_ids, train_idx, test_idx
    """
    md = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise ValueError("Dataset JSON must contain a list at key 'samples'")

    x: List[List[float]] = []
    y_gt: List[float] = []
    y_tg43: List[float] = []
    r_mm: List[float] = []
    theta: List[float] = []
    param_ids: List[int] = []
    train_idx: List[int] = []
    test_idx: List[int] = []

    for s in samples:
        if not isinstance(s, dict):
            continue
        xv = s.get("x")
        if not isinstance(xv, list) or len(xv) < 2:
            continue
        idx = len(x)
        x.append([float(xv[0]), float(xv[1])])
        y_gt.append(float(s.get("y_primary", float("nan"))))
        y_tg43.append(float(s.get("y_tg43", float("nan"))))
        r_mm.append(float(s.get("r_mm", xv[0])))
        theta.append(float(s.get("theta_rad", xv[1])))
        param_ids.append(int(s.get("param_id", -1)))
        split = str(s.get("split", "")).lower()
        if split == "train":
            train_idx.append(idx)
        elif split == "test":
            test_idx.append(idx)

    if not train_idx or not test_idx:
        raise ValueError("Dataset must contain non-empty train and test splits")

    edges_raw = md.get("r_bucket_edges_mm") or []
    try:
        edges = [float(e) for e in edges_raw]
    except Exception:
        edges = []
    info = BrachyDatasetInfo(
        file=str(dataset_path) if dataset_path is not None else "<in-memory>",
        hash_sha256=(sha256_file(dataset_path) if dataset_path is not None else None),
        backend=str(md.get("backend", "unknown")),
        n_samples=int(len(x)),
        n_train=int(len(train_idx)),
        n_test=int(len(test_idx)),
        input_dim=int(len(x[0]) if x else 0),
        r_bucket_edges_mm=edges,
        r_min_mm=float(md.get("r_min_mm", 0.0) or 0.0),
        r_max_mm=float(md.get("r_max_mm", 0.0) or 0.0),
        split_by_paramset=bool(md.get("split_by_paramset", False)),
    )
    return info, x, y_gt, y_tg43, r_mm, theta, param_ids, train_idx, test_idx


def dataset_info_dict(info: BrachyDatasetInfo) -> Dict[str, Any]:
    return asdict(info)
