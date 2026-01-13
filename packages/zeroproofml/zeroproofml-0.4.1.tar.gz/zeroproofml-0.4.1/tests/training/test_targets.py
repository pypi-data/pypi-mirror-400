import pytest

torch = pytest.importorskip("torch")

try:  # pragma: no cover - optional dependency
    import jax.numpy as jnp
except Exception:  # pragma: no cover - optional dependency
    jnp = None

from zeroproof.training import lift_targets, lift_targets_jax


def test_lift_targets_handles_finite_values():
    targets = torch.tensor([0.5, -2.0, 3.14])
    numer, denom = lift_targets(targets)

    assert torch.allclose(numer, targets)
    assert torch.allclose(denom, torch.ones_like(targets))


def test_lift_targets_maps_infinities_to_projective_point():
    targets = torch.tensor([float("inf"), float("-inf")])
    numer, denom = lift_targets(targets)

    assert torch.allclose(numer, torch.tensor([1.0, -1.0]))
    assert torch.allclose(denom, torch.zeros_like(targets))


def test_lift_targets_treats_nan_as_bottom():
    targets = torch.tensor([float("nan"), 1.0])
    numer, denom = lift_targets(targets)

    assert torch.allclose(numer, torch.tensor([1.0, 1.0]), equal_nan=False)
    assert torch.allclose(denom, torch.tensor([0.0, 1.0]))


@pytest.mark.skipif(jnp is None, reason="JAX not installed")
def test_lift_targets_jax_matches_torch_semantics():
    targets = jnp.array([jnp.inf, -jnp.inf, jnp.nan, 2.0])
    numer, denom = lift_targets_jax(targets)

    assert jnp.allclose(numer, jnp.array([1.0, -1.0, 1.0, 2.0]))
    assert jnp.allclose(denom, jnp.array([0.0, 0.0, 0.0, 1.0]))
