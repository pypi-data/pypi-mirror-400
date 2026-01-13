"""
TensorBoard logging wrapper for ZeroProofML.

Provides a unified writer that accepts dict[str, float] scalars per step,
plus helpers for histograms and run metadata. Gracefully degrades when
TensorBoard isn't installed.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


def _now_ts() -> float:
    try:
        return time.time()
    except Exception:
        return 0.0


try:  # pragma: no cover - optional dependency
    from torch.utils.tensorboard import SummaryWriter  # type: ignore

    _TB_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    SummaryWriter = None  # type: ignore
    _TB_AVAILABLE = False


@dataclass
class RunMeta:
    run_dir: str
    seed: Optional[int] = None
    dataset_checksum: Optional[str] = None
    policy_flags: Optional[dict[str, Any]] = None
    commit_hash: Optional[str] = None


class ZPTBWriter:
    """
    Unified TensorBoard writer.

    - Accepts scalar dicts per step via log_scalars.
    - Supports histograms via log_histogram.
    - Records run metadata and hyperparameters.
    - No hard dependency on TensorBoard; operations are no-ops if unavailable.
    """

    def __init__(self, log_dir: str, flush_secs: int = 10, enabled: Optional[bool] = None) -> None:
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Allow explicit disable; default to True if TB present
        self.enabled = _TB_AVAILABLE if enabled is None else bool(enabled and _TB_AVAILABLE)
        self._writer = (
            SummaryWriter(log_dir=self.log_dir, flush_secs=flush_secs) if self.enabled else None
        )
        self._start_ts = _now_ts()

    def is_enabled(self) -> bool:
        return bool(self.enabled and self._writer is not None)

    # --- Scalars ---
    def log_scalars(
        self, scalars: Dict[str, float], step: int, prefix: Optional[str] = None
    ) -> None:
        """
        Log a dict of scalar metrics at a given step.
        Keys are flattened with optional prefix.
        """
        if not self.is_enabled():
            return
        assert self._writer is not None
        for k, v in scalars.items():
            try:
                if v is None:
                    continue
                name = f"{prefix}/{k}" if prefix else k
                # Convert numpy scalars if present
                val = float(v) if hasattr(v, "item") else v
                self._writer.add_scalar(name, val, global_step=step)
            except Exception:
                # Best-effort; skip malformed entries
                continue

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            val = float(value) if hasattr(value, "item") else value
            self._writer.add_scalar(tag, val, global_step=step)
        except Exception:
            pass

    # --- Histograms ---
    def log_histogram(
        self, tag: str, values: Iterable[float], step: int, bins: Optional[int] = None
    ) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            self._writer.add_histogram(tag, values, global_step=step, bins=(bins or "tensorflow"))
        except Exception:
            pass

    # --- HParams / metadata ---
    def log_hparams(
        self, hparams: Dict[str, Any], metrics: Optional[Dict[str, float]] = None
    ) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            # torch.utils.tensorboard.SummaryWriter.add_hparams writes a separate event file
            self._writer.add_hparams(hparams, metric_dict=(metrics or {}))
        except Exception:
            pass

    def log_run_metadata(self, meta: RunMeta) -> None:
        if not self.is_enabled():
            return
        # Encode as scalars/text
        assert self._writer is not None
        try:
            if meta.seed is not None:
                self._writer.add_scalar("hparams/seed", int(meta.seed), 0)
            if meta.dataset_checksum is not None:
                self._writer.add_text("hparams/dataset_checksum", str(meta.dataset_checksum), 0)
            if meta.commit_hash is None:
                # Best effort to fetch commit hash
                try:
                    import subprocess

                    commit = (
                        subprocess.check_output(
                            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
                        )
                        .decode()
                        .strip()
                    )
                except Exception:
                    commit = None
                meta.commit_hash = commit
            if meta.commit_hash is not None:
                self._writer.add_text("hparams/commit", meta.commit_hash, 0)
            if meta.policy_flags:
                for k, v in meta.policy_flags.items():
                    key = f"hparams/policy/{k}"
                    try:
                        if isinstance(v, (int, float)):
                            self._writer.add_scalar(key, float(v), 0)
                        else:
                            self._writer.add_text(key, str(v), 0)
                    except Exception:
                        pass
        except Exception:
            pass

    # --- Images (optional) ---
    def log_image(self, tag: str, img_tensor: Any, step: int) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            self._writer.add_image(tag, img_tensor, global_step=step)
        except Exception:
            pass

    # --- Lifecycle ---
    def flush(self) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            self._writer.flush()
        except Exception:
            pass

    def close(self) -> None:
        if not self.is_enabled():
            return
        assert self._writer is not None
        try:
            self._writer.close()
        except Exception:
            pass
