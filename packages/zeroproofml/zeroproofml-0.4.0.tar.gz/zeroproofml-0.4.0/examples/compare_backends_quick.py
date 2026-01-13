"""
Compare backends (NumPy, Torch, JAX) on a simple 1D task.

Trains y = sin(x) with small models for a few epochs and prints
final metrics for a quick parity check. Backends are optional; any
unavailable backend is skipped.
"""

from __future__ import annotations

import hashlib


def checksum_np(x, y) -> str:
    m = hashlib.sha256()
    m.update(x.tobytes())
    m.update(y.tobytes())
    return m.hexdigest()[:16]


def checksum_torch(torch, x, y) -> str:
    m = hashlib.sha256()
    m.update(x.detach().cpu().numpy().tobytes())
    m.update(y.detach().cpu().numpy().tobytes())
    return m.hexdigest()[:16]


def run_numpy():
    try:
        import numpy as np
        from zeroproof.layers import NPRational
        from zeroproof.training import NumpyTRTrainer, NumpyTrainingConfig

        x = np.linspace(-2.0, 2.0, 512)
        y = np.sin(x)
        model = NPRational(d_p=3, d_q=2)
        cfg = NumpyTrainingConfig(learning_rate=1e-2, max_epochs=200, lambda_rej=1.0)
        trainer = NumpyTRTrainer(model, cfg)
        metrics = trainer.train(x, y)
        print("[NumPy]", metrics, "checksum=", checksum_np(x, y))
    except Exception as e:
        print("[NumPy] skipped:", e)


def run_torch():
    try:
        import torch
        from zeroproof.layers import TorchTRRational
        from zeroproof.training import TorchTrainingConfig, train_torch_rational

        torch.set_default_dtype(torch.float64)
        x = torch.linspace(-2.0, 2.0, 512, dtype=torch.float64, requires_grad=True)
        y = torch.sin(x)
        model = TorchTRRational(d_p=3, d_q=2)
        cfg = TorchTrainingConfig(learning_rate=1e-3, max_epochs=200, seed=42, enable_tensorboard=False)
        metrics = train_torch_rational(model, x, y, cfg)
        print("[Torch]", metrics, "checksum=", checksum_torch(torch, x, y))
    except Exception as e:
        print("[Torch] skipped:", e)


def run_jax():
    try:
        import jax
        import jax.numpy as jnp
        from zeroproof.training import JaxTrainingConfig, train_jax_rational

        x = jnp.linspace(-2.0, 2.0, 512)
        y = jnp.sin(x)
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
        metrics, theta, phi = train_jax_rational(theta0, phi0, x, y, cfg)
        print("[JAX]", metrics, "checksum=", checksum_np(x, y))
    except Exception as e:
        print("[JAX] skipped:", e)


def main() -> None:
    run_numpy()
    run_torch()
    run_jax()


if __name__ == "__main__":
    main()

