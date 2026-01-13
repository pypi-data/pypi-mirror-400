"""
JAX TR-Rational functions.

Functional evaluation of y = P(x)/Q(x) using TRJaxArray primitives
with custom_vjp gradient rules. Designed to be jit/vmap/pmap friendly
by passing (delta, gmax) explicitly.
"""

from __future__ import annotations

from typing import Optional, Tuple

try:  # Optional JAX imports
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    jax = None  # type: ignore
    jnp = None  # type: ignore
    JAX_AVAILABLE = False

from ..bridge.jax_bridge import TAG_CODES, TRJaxArray

if JAX_AVAILABLE:
    from ..autodiff.jax_hybrid import JaxHybridConfig  # type: ignore
    from ..bridge.jax_bridge import tr_add as tr_add_jax
    from ..bridge.jax_bridge import tr_div as tr_div_jax
    from ..bridge.jax_bridge import tr_mul as tr_mul_jax


def _param_tr(value: "jnp.ndarray", like_vals: "jnp.ndarray") -> TRJaxArray:
    """Create a REAL TRJaxArray by broadcasting value to like_vals.shape."""
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for _param_tr")
    vals = jnp.broadcast_to(value, like_vals.shape)
    tags = jnp.full(like_vals.shape, TAG_CODES["REAL"], dtype=jnp.uint8)
    return TRJaxArray(vals, tags)


def _horner_Q_jax(
    X: TRJaxArray,
    phi: "jnp.ndarray",
    *,
    delta: Optional[float] = None,
    gmax: Optional[float] = None,
) -> TRJaxArray:
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for _horner_Q_jax")
    Q_tail = _param_tr(phi[-1], X.values)
    for idx in range(phi.shape[0] - 2, -1, -1):
        Q_tail = tr_mul_jax(X, Q_tail, delta, gmax)
        Q_tail = tr_add_jax(Q_tail, _param_tr(phi[idx], X.values), delta, gmax)
    Q = tr_add_jax(
        tr_mul_jax(X, Q_tail, delta, gmax), _param_tr(jnp.asarray(1.0), X.values), delta, gmax
    )
    return Q


def tr_rational_jax(
    X: TRJaxArray,
    theta: "jnp.ndarray",
    phi: "jnp.ndarray",
    *,
    delta: Optional[float] = None,
    gmax: Optional[float] = None,
) -> TRJaxArray:
    """
    Evaluate y = P(x)/Q(x) via Horner using TR primitives.

    Args:
        X: TRJaxArray input
        theta: shape [d_p+1]
        phi: shape [d_q]
        delta: Hybrid threshold (optional)
        gmax: SAT bound (optional)
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for tr_rational_jax")

    # P Horner: start from highest degree coefficient
    P = _param_tr(theta[-1], X.values)
    for k in range(theta.shape[0] - 2, -1, -1):
        P = tr_mul_jax(X, P, delta, gmax)
        P = tr_add_jax(P, _param_tr(theta[k], X.values), delta, gmax)

    # Q Horner: 1 + x * (phi_1 + x * (phi_2 + ...))
    Q = _horner_Q_jax(X, phi, delta=delta, gmax=gmax)

    return tr_div_jax(P, Q, delta, gmax)


def _expand_last_dim(X: TRJaxArray, size: int) -> TRJaxArray:
    """Expand X by adding a last dimension of given size (broadcast)."""
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for _expand_last_dim")
    vals = jnp.expand_dims(X.values, axis=-1)
    tags = jnp.expand_dims(X.tags, axis=-1)
    vals = jnp.broadcast_to(vals, (*X.values.shape, size))
    tags = jnp.broadcast_to(tags, (*X.tags.shape, size))
    return TRJaxArray(vals, tags)


def tr_rational_multi_jax(
    X: TRJaxArray,
    theta: "jnp.ndarray",
    phi: "jnp.ndarray",
    *,
    delta: Optional[float] = None,
    gmax: Optional[float] = None,
) -> TRJaxArray:
    """
    Evaluate multi‑head y_h = P_h(x)/Q(x) with shared Q.

    Args:
        X: TRJaxArray input
        theta: shape [H, d_p+1]
        phi: shape [d_q]
        delta: Hybrid threshold (optional)
        gmax: SAT bound (optional)

    Returns:
        TRJaxArray with last dimension H.
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for tr_rational_multi_jax")

    H = int(theta.shape[0])
    XH = _expand_last_dim(X, H)
    # P_h Horner
    P = _param_tr(theta[:, -1], XH.values)
    for k in range(theta.shape[1] - 2, -1, -1):
        P = tr_mul_jax(XH, P, delta, gmax)
        P = tr_add_jax(P, _param_tr(theta[:, k], XH.values), delta, gmax)
    # Shared Q
    Q = _horner_Q_jax(X, phi, delta=delta, gmax=gmax)
    QH = _expand_last_dim(Q, H)
    return tr_div_jax(P, QH, delta, gmax)


if JAX_AVAILABLE:

    def _percentile_sorted(x: "jnp.ndarray", pct: float) -> "jnp.ndarray":
        n = x.shape[0]
        k = jnp.clip(
            jnp.floor((pct / 100.0) * jnp.maximum(n - 1, 0)).astype(jnp.int32),
            0,
            jnp.maximum(n - 1, 0),
        )
        xs = jnp.sort(x)
        return xs[k]

    def tr_rational_hybrid_jax(
        X: TRJaxArray,
        theta: "jnp.ndarray",
        phi: "jnp.ndarray",
        epoch: int,
        cfg: JaxHybridConfig,
        tau_on: float,
        tau_off: float,
    ) -> TRJaxArray:
        """
        Evaluate TR rational with a jit/vmap‑safe Hybrid schedule.

        - Computes Q(x) in-graph, derives q_p10 and decides SAT vs MR via hysteresis.
        - delta is exponentially annealed during transition; set to None during warmup.
        - Passes (delta, gmax) into primitives to clip gradients only in SAT regions.
        """
        # Compute Q and |Q|
        Q = _horner_Q_jax(X, phi, delta=None, gmax=None)
        q_abs = jnp.where(Q.tags == TAG_CODES["REAL"], jnp.abs(Q.values), jnp.inf).reshape(-1)
        # Batch statistic (p10)
        p10 = _percentile_sorted(q_abs, 10.0)
        # Epoch‑dependent delta (exponential interpolation) using jax ops
        e = jnp.asarray(epoch, dtype=jnp.int32)
        warm = jnp.asarray(cfg.warmup_epochs, dtype=jnp.int32)
        tr = jnp.maximum(0.0, jnp.minimum(1.0, (e - warm) / jnp.maximum(1, cfg.transition_epochs)))
        di = jnp.asarray(cfg.delta_init, dtype=jnp.float64)
        df = jnp.asarray(cfg.delta_final, dtype=jnp.float64)
        ratio = jnp.where(di > 0, df / di, 1.0)
        delta_sched = jnp.where(e < warm, 0.0, jnp.where(di > 0, di * (ratio**tr), df))
        # Hysteresis decision
        prev_sat = False  # stateless API; caller can thread prev if needed
        enter = p10 <= float(tau_on)
        exit_ = p10 >= float(tau_off)
        sat_mode = jnp.where(prev_sat, jnp.logical_not(exit_), enter)
        # Select (delta, gmax)
        delta = jnp.where(sat_mode, delta_sched, 0.0)
        gmax = jnp.where(sat_mode, jnp.asarray(cfg.gmax, dtype=jnp.float64), jnp.inf)
        # Evaluate P/Q using selected (delta, gmax)
        P = _param_tr(theta[-1], X.values)
        for k in range(theta.shape[0] - 2, -1, -1):
            P = tr_mul_jax(X, P, delta, gmax)
            P = tr_add_jax(P, _param_tr(theta[k], X.values), delta, gmax)
        Y = tr_div_jax(P, Q, delta, gmax)
        return Y
