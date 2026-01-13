"""
Minimal JAX trainer for TR rational functions.

Trains theta (numerator) and phi (denominator) coefficients for the JAX
functional TRRational using Mask‑REAL/HYBRID gradients from custom_vjp
primitives. Stateless hybrid schedule (delta,gmax) is handled via
tr_rational_hybrid_jax.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:  # Optional JAX
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    jax = None  # type: ignore
    jnp = None  # type: ignore
    JAX_AVAILABLE = False

if JAX_AVAILABLE:
    from ..layers.jax_rational import tr_rational_hybrid_jax
    from ..autodiff.jax_hybrid import JaxHybridConfig
    from ..bridge.jax_bridge import from_jax, to_jax

from ..loggers import ZPTBWriter  # type: ignore


@dataclass
class JaxTrainingConfig:
    learning_rate: float = 1e-2
    max_epochs: int = 200
    warmup_epochs: int = 10
    transition_epochs: int = 20
    delta_init: float = 1e-2
    delta_final: float = 1e-6
    gmax: float = 1.0
    tau_on: float = 1e-3
    tau_off: float = 2e-3
    seed: Optional[int] = None
    # Logging
    enable_tensorboard: bool = False
    tb_log_dir: Optional[str] = None
    # Optional JSON export of final metrics
    output_json: Optional[str] = None
    # Optional dataset checksum for metadata
    dataset_checksum: Optional[str] = None


def _jit_loss_fn(X_vals, targets, epoch, cfg: JaxTrainingConfig):
    """Build a jit loss function for given schedule parameters."""
    assert JAX_AVAILABLE

    hybrid_cfg = JaxHybridConfig(
        warmup_epochs=cfg.warmup_epochs,
        transition_epochs=cfg.transition_epochs,
        delta_init=cfg.delta_init,
        delta_final=cfg.delta_final,
        gmax=cfg.gmax,
    )

    def loss(theta: jnp.ndarray, phi: jnp.ndarray) -> jnp.ndarray:
        X = from_jax(X_vals)
        Y = tr_rational_hybrid_jax(
            X,
            theta,
            phi,
            epoch=epoch,
            cfg=hybrid_cfg,
            tau_on=cfg.tau_on,
            tau_off=cfg.tau_off,
        )
        y_pred = to_jax(Y)
        # Standard MSE ignoring NaNs (non-REALs propagate as NaNs)
        return jnp.nanmean((y_pred - targets) ** 2)

    return jax.jit(loss)


def train_jax_rational(
    theta_init: "jnp.ndarray",
    phi_init: "jnp.ndarray",
    x: "jnp.ndarray",
    y: "jnp.ndarray",
    config: Optional[JaxTrainingConfig] = None,
) -> Tuple[Dict[str, float], "jnp.ndarray", "jnp.ndarray"]:
    """
    Train TR rational coefficients with simple SGD.

    Args:
        theta_init: Initial theta coeffs [d_p+1]
        phi_init: Initial phi coeffs [d_q]
        x: Input samples (1D)
        y: Target samples (1D)
        config: JaxTrainingConfig

    Returns:
        (metrics dict, theta, phi)
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for train_jax_rational")

    cfg = config or JaxTrainingConfig()
    if cfg.seed is not None:
        try:
            # Best-effort: set NumPy/jax PRNG
            import numpy as _np  # type: ignore

            _np.random.seed(cfg.seed)
        except Exception:
            pass

    theta = jnp.asarray(theta_init, dtype=jnp.float64)
    phi = jnp.asarray(phi_init, dtype=jnp.float64)
    X_vals = jnp.asarray(x, dtype=jnp.float64).reshape(-1)
    targets = jnp.asarray(y, dtype=jnp.float64).reshape(-1)

    lr = jnp.asarray(cfg.learning_rate, dtype=jnp.float64)

    # Optional TB writer
    writer = (
        ZPTBWriter(cfg.tb_log_dir or "runs/jax_tr", flush_secs=10)
        if cfg.enable_tensorboard and ZPTBWriter is not None
        else None
    )
    if writer is not None:
        try:
            writer.log_hparams(
                {
                    "lr": float(cfg.learning_rate),
                    "epochs": int(cfg.max_epochs),
                    "seed": int(cfg.seed or -1),
                    "warmup_epochs": int(cfg.warmup_epochs),
                    "transition_epochs": int(cfg.transition_epochs),
                    "delta_init": float(cfg.delta_init),
                    "delta_final": float(cfg.delta_final),
                    "gmax": float(cfg.gmax),
                    "tau_on": float(cfg.tau_on),
                    "tau_off": float(cfg.tau_off),
                }
            )
            # Run metadata (seed, dataset checksum)
            try:
                from ..loggers.tensorboard import RunMeta  # type: ignore

                writer.log_run_metadata(
                    RunMeta(
                        run_dir=(cfg.tb_log_dir or "runs/jax_tr"),
                        seed=cfg.seed,
                        dataset_checksum=cfg.dataset_checksum,
                        policy_flags=None,
                    )
                )
            except Exception:
                pass
        except Exception:
            pass

    for ep in range(cfg.max_epochs):
        loss_fn = _jit_loss_fn(X_vals, targets, ep + 1, cfg)
        # Value and gradients
        loss_val, grads = jax.value_and_grad(loss_fn, argnums=(0, 1))(theta, phi)
        g_theta, g_phi = grads
        # SGD update
        theta = theta - lr * g_theta
        phi = phi - lr * g_phi
        # TB scalar per epoch
        if writer is not None:
            try:
                writer.log_scalars({"loss": float(loss_val)}, step=ep + 1, prefix="jax")
            except Exception:
                pass
        # Optional TB histograms and per-bucket MSE (sampled on full X_vals for simplicity)
        if writer is not None:
            try:
                hybrid_cfg = JaxHybridConfig(
                    warmup_epochs=cfg.warmup_epochs,
                    transition_epochs=cfg.transition_epochs,
                    delta_init=cfg.delta_init,
                    delta_final=cfg.delta_final,
                    gmax=cfg.gmax,
                )
                X = from_jax(X_vals)
                Y = tr_rational_hybrid_jax(
                    X,
                    theta,
                    phi,
                    epoch=ep + 1,
                    cfg=hybrid_cfg,
                    tau_on=cfg.tau_on,
                    tau_off=cfg.tau_off,
                )
                y_pred = to_jax(Y)
                # Tags histogram
                try:
                    tags_list = [int(t) for t in jnp.ravel(Y.tags).tolist()]
                    writer.log_histogram("jax/tags", tags_list, step=ep + 1, bins=4)
                except Exception:
                    pass
                # Q_abs histogram
                from ..bridge.jax_bridge import TAG_CODES
                from ..layers.jax_rational import _horner_Q_jax as _Qjax  # type: ignore

                Q = _Qjax(X, phi, delta=None, gmax=None)
                q_abs = jnp.where(Q.tags == TAG_CODES["REAL"], jnp.abs(Q.values), jnp.inf)
                try:
                    writer.log_histogram(
                        "jax/Q_abs", [float(v) for v in jnp.ravel(q_abs).tolist()], step=ep + 1
                    )
                except Exception:
                    pass
                # Per-bucket MSE scalars (REAL outputs only)
                edges = jnp.asarray([0.0, 1e-5, 1e-4, 1e-3, 1e-2, jnp.inf], dtype=jnp.float64)
                real_mask = (Y.tags == TAG_CODES["REAL"]) & jnp.isfinite(y_pred)
                bucket_scalars = {}
                for j in range(edges.shape[0] - 1):
                    lo = float(edges[j])
                    hi = float(edges[j + 1])
                    mask = (q_abs >= lo) & (q_abs <= hi) & real_mask
                    cnt = int(jnp.sum(mask))
                    if cnt > 0:
                        e = (y_pred[mask] - targets[mask]) ** 2
                        mse = float(jnp.mean(e))
                    else:
                        mse = float("nan")
                    bucket_scalars[f"B{j}_mse"] = mse
                writer.log_scalars(bucket_scalars, step=ep + 1, prefix="jax")
                # Optional: bucketed MSE bar image
                try:
                    import matplotlib.pyplot as _plt  # type: ignore
                    import numpy as _np  # type: ignore

                    buckets = [f"B{j}" for j in range(edges.shape[0] - 1)]
                    mse_vals = [
                        float(bucket_scalars.get(f"B{j}_mse", _np.nan)) for j in range(len(buckets))
                    ]
                    fig, ax = _plt.subplots(figsize=(4.0, 3.0), dpi=100)
                    xs = _np.arange(len(buckets))
                    ax.bar(xs, mse_vals, color="#1f77b4")
                    ax.set_xticks(xs)
                    ax.set_xticklabels(buckets)
                    ax.set_ylabel("MSE")
                    ax.set_title(f"Bucketed MSE (epoch {ep + 1})")
                    fig.tight_layout()
                    # Convert to HxWxC uint8 image and log
                    fig.canvas.draw()
                    w, h = fig.canvas.get_width_height()
                    img = _np.frombuffer(fig.canvas.tostring_rgb(), dtype=_np.uint8).reshape(
                        h, w, 3
                    )
                    writer.log_image("jax/bucket_mse", img, step=ep + 1)
                    # Optionally save alongside tb_log_dir
                    try:
                        import os as _os

                        out_dir = cfg.tb_log_dir or "runs/jax_tr"
                        _os.makedirs(_os.path.join(out_dir, "plots"), exist_ok=True)
                        fig_path = _os.path.join(
                            out_dir, "plots", f"bucket_mse_epoch_{ep + 1:04d}.png"
                        )
                        fig.savefig(fig_path)
                    except Exception:
                        pass
                    _plt.close(fig)
                except Exception:
                    pass
                # Grad histogram
                try:
                    g_abs = jnp.concatenate([jnp.abs(g_theta).ravel(), jnp.abs(g_phi).ravel()])
                    writer.log_histogram(
                        "jax/grad_abs", [float(v) for v in g_abs.tolist()], step=ep + 1
                    )
                except Exception:
                    pass
            except Exception:
                pass

    final_loss = float(_jit_loss_fn(X_vals, targets, cfg.max_epochs, cfg)(theta, phi))

    # Coverage: fraction of REAL outputs at final epoch
    try:
        X = from_jax(X_vals)
        hybrid_cfg = JaxHybridConfig(
            warmup_epochs=cfg.warmup_epochs,
            transition_epochs=cfg.transition_epochs,
            delta_init=cfg.delta_init,
            delta_final=cfg.delta_final,
            gmax=cfg.gmax,
        )
        Y = tr_rational_hybrid_jax(
            X,
            theta,
            phi,
            epoch=cfg.max_epochs,
            cfg=hybrid_cfg,
            tau_on=cfg.tau_on,
            tau_off=cfg.tau_off,
        )
        real_ratio = float(jnp.mean((Y.tags == 0).astype(jnp.float32)))
    except Exception:
        real_ratio = 0.0

    metrics = {"loss": final_loss, "coverage": real_ratio, "non_real_frac": float(1.0 - real_ratio)}
    # Per-bucket MSE summary using final epoch predictions
    try:
        from ..bridge.jax_bridge import TAG_CODES
        from ..layers.jax_rational import _horner_Q_jax as _Qjax  # type: ignore

        X = from_jax(X_vals)
        hybrid_cfg = JaxHybridConfig(
            warmup_epochs=cfg.warmup_epochs,
            transition_epochs=cfg.transition_epochs,
            delta_init=cfg.delta_init,
            delta_final=cfg.delta_final,
            gmax=cfg.gmax,
        )
        Y = tr_rational_hybrid_jax(
            X,
            theta,
            phi,
            epoch=cfg.max_epochs,
            cfg=hybrid_cfg,
            tau_on=cfg.tau_on,
            tau_off=cfg.tau_off,
        )
        y_pred = to_jax(Y)
        Q = _Qjax(X, phi, delta=None, gmax=None)
        q_abs = jnp.where(Q.tags == TAG_CODES["REAL"], jnp.abs(Q.values), jnp.inf)
        edges = jnp.asarray([0.0, 1e-5, 1e-4, 1e-3, 1e-2, jnp.inf], dtype=jnp.float64)
        real_mask = (Y.tags == TAG_CODES["REAL"]) & jnp.isfinite(y_pred)
        # Compute per-bucket MSE
        for j in range(edges.shape[0] - 1):
            lo = float(edges[j])
            hi = float(edges[j + 1])
            mask = (q_abs >= lo) & (q_abs <= hi) & real_mask
            cnt = int(jnp.sum(mask))
            if cnt > 0:
                e = (y_pred[mask] - targets[mask]) ** 2
                mse = float(jnp.mean(e))
            else:
                mse = float("nan")
            metrics[f"B{j}_mse"] = mse
            metrics[f"B{j}_count"] = float(cnt)
    except Exception:
        pass
    # TB close
    if writer is not None:
        try:
            writer.log_scalars(
                {"final/loss": final_loss, "final/coverage": real_ratio},
                step=cfg.max_epochs,
                prefix="jax",
            )
            writer.flush()
            writer.close()
        except Exception:
            pass
    # Optional JSON export
    try:
        if cfg.output_json:
            import json

            with open(cfg.output_json, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
    except Exception:
        pass
    return metrics, theta, phi
