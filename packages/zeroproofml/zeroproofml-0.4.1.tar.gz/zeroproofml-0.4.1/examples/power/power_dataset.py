from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class PowerDatasetInfo:
    file: str
    hash_sha256: Optional[str]
    backend: str
    n_samples: int
    n_train: int
    n_test: int
    n_holdout: int
    input_dim: int
    target: str
    delta_lambda_bucket_edges: List[float]
    train_scenarios: List[int]
    test_scenarios: List[int]


def sha256_file(path: str) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def load_power_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Dataset must be a JSON object")
    return data


def flatten_xy(
    data: Dict[str, Any],
    *,
    dataset_path: str | None = None,
    target: str = "vmin",
) -> Tuple[
    PowerDatasetInfo,
    List[List[float]],
    List[float],
    List[float],
    List[str],
    List[int],
    List[int],
    List[int],
    List[int],
    List[float],
]:
    md = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise ValueError("Dataset JSON must contain a list at key 'samples'")
    splits = data.get("splits") if isinstance(data.get("splits"), dict) else {}
    train_scenarios = [int(x) for x in (splits.get("train_scenarios") or [])]
    test_scenarios = [int(x) for x in (splits.get("test_scenarios") or [])]

    x: List[List[float]] = []
    y: List[float] = []
    delta: List[float] = []
    bucket: List[str] = []
    train_indices: List[int] = []
    test_indices: List[int] = []
    holdout_indices: List[int] = []
    scenario_ids: List[int] = []
    lambdas: List[float] = []
    for s in samples:
        if not isinstance(s, dict):
            continue
        if not bool(s.get("converged", True)):
            continue
        xv = s.get("x")
        if not isinstance(xv, list):
            continue
        x.append([float(v) for v in xv])
        if target == "vmin":
            y.append(float(s["y_vmin"]))
        elif target == "delta_lambda":
            y.append(float(s.get("y_delta_lambda", s.get("delta_lambda", 0.0))))
        elif target == "dvmin_dlambda":
            y.append(float(s.get("y_dvmin_dlambda", float("nan"))))
        else:
            raise ValueError("target must be one of: vmin, delta_lambda, dvmin_dlambda")
        delta.append(float(s.get("delta_lambda", 0.0)))
        bucket.append(str(s.get("delta_bucket", "")))
        scenario_ids.append(int(s.get("scenario_id", -1)))
        lambdas.append(float(s.get("lambda", float("nan"))))
        split = str(s.get("split", "")).lower()
        if split == "train":
            train_indices.append(len(x) - 1)
        elif split == "train_holdout":
            holdout_indices.append(len(x) - 1)
        elif split == "test":
            test_indices.append(len(x) - 1)

    n_train = int(len(train_indices))
    n_test = int(len(test_indices))
    n_holdout = int(len(holdout_indices))

    info = PowerDatasetInfo(
        file=str(dataset_path) if dataset_path is not None else "<in-memory>",
        hash_sha256=(sha256_file(dataset_path) if dataset_path is not None else None),
        backend=str(md.get("backend", "unknown")),
        n_samples=len(x),
        n_train=n_train,
        n_test=n_test,
        n_holdout=n_holdout,
        input_dim=(len(x[0]) if x else 0),
        target=str(target),
        delta_lambda_bucket_edges=[float(v) for v in (md.get("delta_lambda_bucket_edges") or [])],
        train_scenarios=train_scenarios,
        test_scenarios=test_scenarios,
    )
    return info, x, y, delta, bucket, train_indices, test_indices, holdout_indices, scenario_ids, lambdas




def dataset_info_dict(info: PowerDatasetInfo) -> Dict[str, Any]:
    return asdict(info)
