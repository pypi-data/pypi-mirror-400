import pytest

pytest.importorskip("numpy")
import numpy as np

from zeroproof.scm import (
    scm_add_jax,
    scm_add_numpy,
    scm_add_torch,
    scm_div_numpy,
    scm_inv_jax,
    scm_mul_torch,
)


def test_numpy_vectorized_bottom_absorption():
    x = np.array([1.0, -2.0])
    y = np.array([3.0, 4.0])
    mask_x = np.array([False, True])

    result, mask = scm_add_numpy(x, y, mask_x)

    assert mask.tolist() == [False, True]
    assert np.allclose(result, np.array([4.0, 0.0]))


def test_numpy_division_flags_zero_denominator():
    x = np.array([1.0, 2.0])
    y = np.array([0.0, 4.0])

    result, mask = scm_div_numpy(x, y)

    assert mask.tolist() == [True, False]
    assert np.allclose(result, np.array([0.0, 0.5]))


def test_torch_vectorized_matches_native_when_finite():
    torch = pytest.importorskip("torch")

    x = torch.tensor([1.0, -2.0], dtype=torch.float64)
    y = torch.tensor([3.0, 4.0], dtype=torch.float64)

    result, mask = scm_mul_torch(x, y)

    assert torch.equal(mask, torch.tensor([False, False]))
    assert torch.allclose(result, x * y)


def test_torch_bottom_mask_propagates():
    torch = pytest.importorskip("torch")

    x = torch.tensor([1.0, -2.0], dtype=torch.float64)
    y = torch.tensor([3.0, 4.0], dtype=torch.float64)
    mask_x = torch.tensor([False, True])

    result, mask = scm_mul_torch(x, y, mask_x)

    assert torch.equal(mask, mask_x)
    assert torch.allclose(result, torch.tensor([3.0, 0.0], dtype=torch.float64))


def test_jax_inverse_marks_zeros_as_bottom():
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp

    values = jnp.array([1.0, 0.0])

    result, mask = scm_inv_jax(values)

    assert np.asarray(mask).tolist() == [False, True]
    assert np.allclose(np.asarray(result), np.array([1.0, 0.0]))


def test_jax_addition_respects_existing_mask():
    jax = pytest.importorskip("jax")
    import jax.numpy as jnp

    x = jnp.array([1.0, 2.0])
    y = jnp.array([3.0, 4.0])
    mask_y = jnp.array([False, True])

    result, mask = scm_add_jax(x, y, mask_y=mask_y)

    assert np.asarray(mask).tolist() == [False, True]
    assert np.allclose(np.asarray(result), np.array([4.0, 0.0]))
