from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    if p <= 0:
        return xs[0]
    if p >= 100:
        return xs[-1]
    k = (len(xs) - 1) * (p / 100.0)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return xs[f]
    d0 = xs[f] * (c - k)
    d1 = xs[c] * (k - f)
    return d0 + d1


@dataclass(frozen=True)
class TorchMicrobenchConfig:
    batch_sizes: Sequence[int] = (1, 256)
    warmup_iters: int = 20
    iters: int = 100
    device: str = "cpu"
    num_threads: Optional[int] = None
    label: str = "forward"


def torch_microbench(
    *,
    predict_fn: Callable[[Any], Any],
    example_batch: Any,
    cfg: TorchMicrobenchConfig,
) -> Dict[str, Any]:
    """
    Microbenchmark a PyTorch callable in a way that is comparable across methods.

    - Measures wall-clock time for forward-only calls.
    - Synchronizes CUDA before/after each timed iteration if on GPU.
    - Returns per-batch and per-sample timing stats for each requested batch size.
    """
    import torch

    prev_threads: Optional[int] = None
    if cfg.num_threads is not None:
        try:
            prev_threads = int(torch.get_num_threads())
            torch.set_num_threads(int(cfg.num_threads))
        except Exception:
            prev_threads = None

    def _sync() -> None:
        if str(cfg.device).startswith("cuda") and torch.cuda.is_available():
            torch.cuda.synchronize()

    def _slice_batch(batch: Any, n: int) -> Any:
        if isinstance(batch, torch.Tensor):
            if int(batch.shape[0]) >= int(n):
                return batch[: int(n)]
            reps = int(math.ceil(float(n) / float(max(1, int(batch.shape[0])))))
            out = batch.repeat((reps,) + (1,) * (batch.ndim - 1))[: int(n)]
            return out
        if isinstance(batch, (tuple, list)):
            return type(batch)(_slice_batch(b, n) for b in batch)
        if isinstance(batch, dict):
            return {k: _slice_batch(v, n) for k, v in batch.items()}
        return batch

    results: Dict[str, Any] = {"config": asdict(cfg), "batches": {}}
    try:
        with torch.inference_mode():
            for bs in cfg.batch_sizes:
                bs_i = int(bs)
                batch = _slice_batch(example_batch, bs_i)
                # Warmup
                for _ in range(int(cfg.warmup_iters)):
                    _ = predict_fn(batch)
                _sync()
                times_s: List[float] = []
                for _ in range(int(cfg.iters)):
                    _sync()
                    t0 = time.perf_counter()
                    _ = predict_fn(batch)
                    _sync()
                    times_s.append(float(time.perf_counter() - t0))
                mean_s = float(sum(times_s) / max(1, len(times_s)))
                results["batches"][str(bs_i)] = {
                    "mean_us_per_batch": 1e6 * mean_s,
                    "p50_us_per_batch": 1e6 * _percentile(times_s, 50.0),
                    "p95_us_per_batch": 1e6 * _percentile(times_s, 95.0),
                    "mean_us_per_sample": (1e6 * mean_s / max(1, bs_i)),
                    "iters": int(cfg.iters),
                    "warmup_iters": int(cfg.warmup_iters),
                }
    finally:
        if prev_threads is not None:
            try:
                torch.set_num_threads(int(prev_threads))
            except Exception:
                pass
    return results
