"""
Minimal NumPy trainer for TR rational models (reference backend).

Uses analytic REAL‑path gradients for y = P/Q under Mask‑REAL gating.
Emits simple metrics compatible with other backends (coverage, non_real_frac, q_min_epoch, loss).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore
    NUMPY_AVAILABLE = False

from ..bridge.numpy_bridge import from_numpy, to_numpy_array
from ..core import TRTag
from ..layers.numpy_rational import NPRational


def _monomial_basis(x: "np.ndarray", max_deg: int) -> "np.ndarray":
    x = np.asarray(x, dtype=float).reshape(-1)
    psi = np.ones((x.shape[0], max_deg + 1), dtype=float)
    if max_deg >= 1:
        for k in range(1, max_deg + 1):
            psi[:, k] = psi[:, k - 1] * x
    return psi


@dataclass
class NumpyTrainingConfig:
    learning_rate: float = 1e-2
    max_epochs: int = 100
    lambda_rej: float = 1.0
    # Optional metrics export
    output_json: Optional[str] = None


class NumpyTRTrainer:
    def __init__(self, model: NPRational, config: Optional[NumpyTrainingConfig] = None):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for NumpyTRTrainer")
        self.model = model
        self.config = config or NumpyTrainingConfig()
        self.epoch = 0
        self.history: Dict[str, List[float]] = {"loss": [], "coverage": [], "non_real_frac": []}

    def _forward_tr(self, x: "np.ndarray"):
        y_tr = self.model.forward(x)
        y = to_numpy_array(y_tr)
        # Build simple tag list from TRArray tags
        tags = []
        flat_tags = y_tr.tags.reshape(-1)
        for t in flat_tags:
            # Map uint8 code to TRTag order [REAL, PINF, NINF, PHI]
            if int(t) == 0:
                tags.append(TRTag.REAL)
            elif int(t) == 1:
                tags.append(TRTag.PINF)
            elif int(t) == 2:
                tags.append(TRTag.NINF)
            else:
                tags.append(TRTag.PHI)
        return y, tags

    def _compute_gradients(
        self, x: "np.ndarray", y: "np.ndarray", t: "np.ndarray"
    ) -> Tuple["np.ndarray", "np.ndarray", float, float, float]:
        # Monomial basis
        psi = _monomial_basis(x, max(self.model.d_p, self.model.d_q))
        P = psi[:, : self.model.d_p + 1] @ self.model.theta
        Q = 1.0 + psi[:, 1 : self.model.d_q + 1] @ self.model.phi
        # Mask REAL path: Q finite and !=0
        mask = np.isfinite(Q) & (Q != 0.0) & np.isfinite(P) & np.isfinite(x)
        n = max(1, int(mask.sum()))
        # Pred values
        y_pred = np.divide(P, Q, out=np.zeros_like(P), where=(Q != 0))
        err = y_pred - t
        err[~mask] = 0.0
        # Gradients
        # d/d theta_k: err * psi_k / Q
        G_theta = np.zeros_like(self.model.theta)
        for k in range(self.model.theta.shape[0]):
            G_theta[k] = np.sum(err[mask] * psi[mask, k] / Q[mask]) / n
        # d/d phi_k: err * ( -P * psi_{k} / Q^2 ) for k>=1
        G_phi = np.zeros_like(self.model.phi)
        for k in range(self.model.phi.shape[0]):
            G_phi[k] = np.sum(err[mask] * (-(P[mask] * psi[mask, k + 1]) / (Q[mask] ** 2))) / n
        # Coverage + non-real frac
        total = x.shape[0]
        coverage = float(mask.sum()) / float(total) if total > 0 else 0.0
        non_real_frac = 1.0 - coverage
        # Loss: MSE over REAL path + lambda_rej * non_real_frac
        mse = 0.5 * float(np.mean((err[mask]) ** 2)) if n > 0 else 0.0
        loss = mse + self.config.lambda_rej * non_real_frac
        # q_min
        q_abs = np.abs(Q[mask]) if n > 0 else np.array([])
        q_min = float(np.min(q_abs)) if q_abs.size > 0 else float("inf")
        return G_theta, G_phi, loss, coverage, q_min

    def train(self, x: "np.ndarray", y: "np.ndarray") -> Dict[str, float]:
        x = np.asarray(x, dtype=float).reshape(-1)
        y = np.asarray(y, dtype=float).reshape(-1)
        for ep in range(self.config.max_epochs):
            self.epoch = ep + 1
            # Forward to compute current tags and predictions
            y_pred, tags = self._forward_tr(x)
            # Gradients and metrics
            G_theta, G_phi, loss, coverage, q_min = self._compute_gradients(x, y_pred, y)
            # Update
            self.model.theta -= self.config.learning_rate * G_theta
            self.model.phi -= self.config.learning_rate * G_phi
            # History
            self.history["loss"].append(loss)
            self.history["coverage"].append(coverage)
            self.history["non_real_frac"].append(1.0 - coverage)
        # Final metrics
        final = {
            "loss": self.history["loss"][-1] if self.history["loss"] else float("nan"),
            "coverage": self.history["coverage"][-1] if self.history["coverage"] else 0.0,
            "non_real_frac": (
                self.history["non_real_frac"][-1] if self.history["non_real_frac"] else 1.0
            ),
        }
        # Optional JSON export matching evaluator schema keys used downstream
        try:
            if self.config.output_json:
                payload: Dict[str, float] = dict(final)
                # Bucketed MSE (B0..B4) on full dataset
                bm = self._bucketed_mse(x, y)
                payload["bucket_overall_mse"] = float(bm["overall_mse"])  # type: ignore[index]
                for k, v in bm["per_bucket"].items():  # type: ignore[index]
                    payload[f"{k}_mse"] = float(v.get("mean_mse", float("nan")))
                    payload[f"{k}_count"] = float(v.get("count", 0.0))
                import json

                with open(self.config.output_json, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
        except Exception:
            pass
        return final

    def _bucketed_mse(
        self, x: "np.ndarray", y: "np.ndarray", edges: Optional[list[float]] = None
    ) -> Dict[str, object]:
        """Compute per-bucket MSE by |Q| with default edges matching docs.

        Returns dict with keys: bucket_edges, per_bucket, overall_mse.
        """
        edges = edges or [0.0, 1e-5, 1e-4, 1e-3, 1e-2, float("inf")]
        try:
            xv = np.asarray(x, dtype=float).reshape(-1)
            tv = np.asarray(y, dtype=float).reshape(-1)
            yhat = self.model.forward_values(xv).reshape(-1)
            q_vals = np.asarray(self.model.get_q_values(xv), dtype=float).reshape(-1)
            n_bins = len(edges) - 1
            per: Dict[str, Dict[str, float]] = {}
            overall_sse = 0.0
            overall_cnt = 0
            for j in range(n_bins):
                lo, hi = edges[j], edges[j + 1]
                mask = (q_vals >= lo) & (q_vals <= hi)
                cnt = int(mask.sum())
                if cnt > 0:
                    e = (yhat[mask] - tv[mask]) ** 2
                    mse = float(np.mean(e))
                    sse = float(np.sum(e))
                else:
                    mse = float("nan")
                    sse = 0.0
                per[f"B{j}"] = {"count": float(cnt), "mean_mse": mse}
                overall_sse += sse
                overall_cnt += cnt
            overall_mse = (overall_sse / overall_cnt) if overall_cnt > 0 else float("nan")
            return {"bucket_edges": edges, "per_bucket": per, "overall_mse": float(overall_mse)}
        except Exception:
            return {"bucket_edges": edges or [], "per_bucket": {}, "overall_mse": float("nan")}
