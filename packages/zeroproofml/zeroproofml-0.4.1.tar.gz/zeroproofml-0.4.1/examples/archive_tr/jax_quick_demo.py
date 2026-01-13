"""
Quick JAX TRRational demo with Hybrid schedule.

Trains theta/phi on y = sin(x) using a simple SGD loop and logs final metrics.

Usage:
  python examples/jax_quick_demo.py
"""

from __future__ import annotations

import hashlib


def _require_jax():
    try:
        import jax  # type: ignore
        import jax.numpy as jnp  # type: ignore

        return jax, jnp
    except Exception as e:
        print("JAX not available:", e)
        raise SystemExit(0)


def dataset_checksum(x, y) -> str:
    m = hashlib.sha256()
    m.update(x.tobytes())
    m.update(y.tobytes())
    return m.hexdigest()[:16]


def main() -> None:
    jax, jnp = _require_jax()
    from zeroproof.training import JaxTrainingConfig, train_jax_rational

    # Synthetic dataset
    x = jnp.linspace(-2.0, 2.0, 1024)
    y = jnp.sin(x)

    # Degrees
    d_p, d_q = 3, 2
    theta0 = jnp.zeros((d_p + 1,), dtype=jnp.float64)
    phi0 = jnp.zeros((d_q,), dtype=jnp.float64)

    cfg = JaxTrainingConfig(
        learning_rate=1e-2,
        max_epochs=200,
        warmup_epochs=10,
        transition_epochs=30,
        delta_init=1e-2,
        delta_final=1e-6,
        gmax=1.0,
        tau_on=1e-3,
        tau_off=2e-3,
        seed=42,
    )

    print("Training JAX TRRational on y=sin(x) ...")
    metrics, theta, phi = train_jax_rational(theta0, phi0, x, y, cfg)
    print("Final metrics:", metrics)
    print("Dataset checksum:", dataset_checksum(x, y))


if __name__ == "__main__":
    main()

