"""
JAX hybrid schedule helpers (stateless, jit/vmap-friendly).

Provides utilities to compute schedule deltas and decide HYBRID vs MASK-REAL
based on in-graph Q statistics, using only JAX primitives (no Python branching).
"""

from __future__ import annotations

from typing import NamedTuple, Optional, Tuple

try:
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    jax = None  # type: ignore
    jnp = None  # type: ignore
    JAX_AVAILABLE = False


class JaxHybridConfig(NamedTuple):
    warmup_epochs: int
    transition_epochs: int
    delta_init: float
    delta_final: float
    gmax: float


def schedule_delta_jax(epoch: int, cfg: JaxHybridConfig) -> Optional[float]:
    """
    Compute schedule delta for given epoch using exponential interpolation.

    Returns None during warmup to indicate pure MASK-REAL.
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for schedule_delta_jax")
    e = jnp.asarray(epoch, dtype=jnp.int32)
    warm = jnp.asarray(cfg.warmup_epochs, dtype=jnp.int32)
    if int(epoch) < int(cfg.warmup_epochs):
        return None
    # Progress in [0,1]
    tr = jnp.maximum(0.0, jnp.minimum(1.0, (e - warm) / jnp.maximum(1, cfg.transition_epochs)))
    # Exponential interpolation: delta = di * (df/di)^tr
    di = jnp.asarray(cfg.delta_init, dtype=jnp.float64)
    df = jnp.asarray(cfg.delta_final, dtype=jnp.float64)
    ratio = jnp.where(di > 0, df / di, 1.0)
    delta = jnp.where(di > 0, di * (ratio**tr), df)
    return float(delta)


def _percentile_sorted(x: "jnp.ndarray", pct: float) -> "jnp.ndarray":
    """Percentile via sort and index; pct in [0,100]."""
    n = x.shape[0]
    k = jnp.clip(jnp.floor((pct / 100.0) * (n - 1)).astype(jnp.int32), 0, jnp.maximum(n - 1, 0))
    xs = jnp.sort(x)
    return xs[k]


def hybrid_hysteresis_decision(
    q_abs: "jnp.ndarray", tau_on: float, tau_off: float, prev_sat: bool
) -> Tuple[bool, bool]:
    """
    Decide SAT vs MR using hysteresis on batch statistics.

    - Enter SAT if q_p10 <= tau_on
    - Exit to MR if q_p10 >= tau_off

    Returns (sat_mode, flipped).
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for hybrid_hysteresis_decision")
    q_abs = jnp.asarray(q_abs, dtype=jnp.float64).reshape(-1)
    p10 = _percentile_sorted(q_abs, 10.0)
    sat_enter = p10 <= float(tau_on)
    sat_exit = p10 >= float(tau_off)
    sat_mode = jnp.where(prev_sat, jnp.logical_not(sat_exit), sat_enter)
    flipped = jnp.logical_xor(prev_sat, sat_mode)
    return bool(sat_mode), bool(flipped)
