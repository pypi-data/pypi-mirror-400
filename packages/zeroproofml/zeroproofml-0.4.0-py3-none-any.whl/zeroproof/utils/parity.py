"""
Backend parity runner: trains small rational models across NumPy, Torch, and JAX
on the same synthetic dataset and returns comparable metrics (including
bucketed MSE B0..B4) for quick parity checks.

All backends are optional; unavailable ones are skipped.
"""

from __future__ import annotations

from typing import Dict, Tuple


def _numpy_run(n_samples: int = 512, epochs: int = 200) -> Tuple[Dict[str, float], str]:
    try:
        import numpy as np

        from ..layers import NPRational
        from ..training import NumpyTrainingConfig, NumpyTRTrainer

        x = np.linspace(-2.0, 2.0, n_samples)
        y = np.sin(x)
        model = NPRational(d_p=3, d_q=2)
        cfg = NumpyTrainingConfig(learning_rate=1e-2, max_epochs=epochs, lambda_rej=1.0)
        trainer = NumpyTRTrainer(model, cfg)
        metrics = trainer.train(x, y)
        # Add checksum
        import hashlib

        m = hashlib.sha256()
        m.update(x.tobytes())
        m.update(y.tobytes())
        return metrics, m.hexdigest()[:16]
    except Exception as e:  # pragma: no cover - optional
        return {"error": f"numpy: {e}"}, ""


def _torch_run(n_samples: int = 512, epochs: int = 200) -> Tuple[Dict[str, float], str]:
    try:
        import torch

        from ..layers import TorchTRRational
        from ..training import TorchTrainingConfig, train_torch_rational

        torch.set_default_dtype(torch.float64)
        # Inputs need not require gradients for parameter training; keep graph simple
        x = torch.linspace(-2.0, 2.0, n_samples, dtype=torch.float64, requires_grad=False)
        y = torch.sin(x)
        model = TorchTRRational(d_p=3, d_q=2)
        cfg = TorchTrainingConfig(
            learning_rate=1e-3, max_epochs=epochs, seed=42, enable_tensorboard=False
        )
        metrics = train_torch_rational(model, x, y, cfg)
        # checksum
        import hashlib

        m = hashlib.sha256()
        m.update(x.detach().cpu().numpy().tobytes())
        m.update(y.detach().cpu().numpy().tobytes())
        return metrics, m.hexdigest()[:16]
    except Exception as e:  # pragma: no cover - optional
        return {"error": f"torch: {e}"}, ""


def _jax_run(n_samples: int = 512, epochs: int = 200) -> Tuple[Dict[str, float], str]:
    try:
        import jax

        # Ensure 64-bit enabled for consistency with training configs
        try:
            jax.config.update("jax_enable_x64", True)  # type: ignore[attr-defined]
        except Exception:
            pass
        import jax.numpy as jnp

        from ..training import JaxTrainingConfig, train_jax_rational

        x = jnp.linspace(-2.0, 2.0, n_samples)
        y = jnp.sin(x)
        d_p, d_q = 3, 2
        theta0 = jnp.zeros((d_p + 1,), dtype=jnp.float64)
        phi0 = jnp.zeros((d_q,), dtype=jnp.float64)
        cfg = JaxTrainingConfig(
            learning_rate=1e-2,
            max_epochs=epochs,
            warmup_epochs=10,
            transition_epochs=30,
            delta_init=1e-2,
            delta_final=1e-6,
            gmax=1.0,
            tau_on=1e-3,
            tau_off=2e-3,
            seed=42,
            enable_tensorboard=False,
        )
        metrics, theta, phi = train_jax_rational(theta0, phi0, x, y, cfg)
        # checksum
        import hashlib

        m = hashlib.sha256()
        m.update(x.tobytes())
        m.update(y.tobytes())
        return metrics, m.hexdigest()[:16]
    except Exception as e:  # pragma: no cover - optional
        return {"error": f"jax: {e}"}, ""


def run_backend_parity(n_samples: int = 512, epochs: int = 200) -> Dict[str, Dict[str, float]]:
    """Run all available backends and return their metrics dicts."""
    results: Dict[str, Dict[str, float]] = {}
    np_res, np_hash = _numpy_run(n_samples=n_samples, epochs=epochs)
    if "error" not in np_res:
        np_res["dataset_checksum"] = np_hash
        results["numpy"] = np_res
    torch_res, thash = _torch_run(n_samples=n_samples, epochs=epochs)
    if "error" not in torch_res:
        torch_res["dataset_checksum"] = thash
        results["torch"] = torch_res
    jax_res, jhash = _jax_run(n_samples=n_samples, epochs=epochs)
    if "error" not in jax_res:
        jax_res["dataset_checksum"] = jhash
        results["jax"] = jax_res
    return results


def parity_within_tolerance(results: Dict[str, Dict[str, float]], tol: float = 0.2) -> bool:
    """Check per-bucket MSE parity within tolerance across available backends.

    Returns True if all pairwise differences for B0..B4 are <= tol (ignoring NaNs).
    """
    backends = list(results.keys())
    if len(backends) < 2:
        return True
    buckets = [f"B{j}_mse" for j in range(5)]
    import math

    for b in buckets:
        vals = []
        for be in backends:
            v = results[be].get(b)
            if isinstance(v, (int, float)) and not math.isnan(v):
                vals.append(float(v))
        if len(vals) < 2:
            continue
        lo, hi = min(vals), max(vals)
        if hi - lo > tol:
            return False
    return True
