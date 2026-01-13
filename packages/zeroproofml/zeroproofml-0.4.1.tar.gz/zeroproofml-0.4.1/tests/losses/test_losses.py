import pytest

torch = pytest.importorskip("torch")

try:  # pragma: no cover - optional dependency
    import jax.numpy as jnp
except Exception:  # pragma: no cover - optional dependency
    jnp = None

from zeroproof.losses import (
    LossConfig,
    SCMTrainingLoss,
    coverage,
    implicit_loss,
    implicit_loss_jax,
    margin_loss,
    rejection_loss,
    sign_consistency_loss,
)


def test_implicit_loss_matches_expected_value():
    P = torch.tensor([1.0, 0.5])
    Q = torch.tensor([1.0, 2.0])
    Y_n = torch.tensor([1.0, 1.0])
    Y_d = torch.tensor([1.0, 1.0])

    expected = ((P * Y_d - Q * Y_n) ** 2 / (Q**2 * Y_d**2 + P**2 * Y_n**2 + 1e-9)).mean()
    loss = implicit_loss(P, Q, Y_n, Y_d)

    assert torch.allclose(loss, expected)


def test_implicit_loss_handles_origin_gracefully():
    zeros = torch.zeros(3)
    loss = implicit_loss(zeros, zeros, zeros, zeros)
    assert torch.isfinite(loss)
    assert loss == 0


@pytest.mark.skipif(jnp is None, reason="JAX not installed")
def test_implicit_loss_jax_matches_torch_formula():
    P = jnp.array([1.0, 0.0])
    Q = jnp.array([1.0, 1.0])
    Y_n = jnp.array([1.0, -1.0])
    Y_d = jnp.array([1.0, 1.0])

    expected = ((P * Y_d - Q * Y_n) ** 2 / (Q**2 * Y_d**2 + P**2 * Y_n**2 + 1e-9)).mean()
    loss = implicit_loss_jax(P, Q, Y_n, Y_d)

    assert jnp.allclose(loss, expected)


def test_implicit_loss_is_scale_invariant_when_gamma_negligible():
    P = torch.tensor([1.0, 0.5])
    Q = torch.tensor([1.0, 2.0])
    Y_n = torch.tensor([1.0, 1.0])
    Y_d = torch.tensor([1.0, 1.0])

    loss = implicit_loss(P, Q, Y_n, Y_d)
    loss_scaled = implicit_loss(10.0 * P, 10.0 * Q, Y_n, Y_d)

    assert torch.allclose(loss, loss_scaled, rtol=1e-6, atol=1e-7)


def test_margin_loss_respects_mask():
    Q = torch.tensor([1e-5, 1e-3])
    mask = torch.tensor([1.0, 0.0])
    loss = margin_loss(Q, tau_train=1e-4, mask_finite=mask)

    expected = (torch.relu(1e-4 - torch.abs(Q)) ** 2 * mask).mean()
    assert torch.allclose(loss, expected)


def test_sign_consistency_distinguishes_orientation():
    P = torch.tensor([1.0])
    Q = torch.tensor([0.0])
    Y_pos = torch.tensor([1.0])
    Y_neg = torch.tensor([-1.0])
    Y_d = torch.tensor([0.0])

    loss_pos = sign_consistency_loss(P, Q, Y_pos, Y_d)
    loss_neg = sign_consistency_loss(P, Q, Y_neg, Y_d)

    assert loss_pos < 1e-4  # near perfect alignment
    assert loss_neg > 1.5  # strong penalty for opposite sign


def test_coverage_and_rejection_loss():
    is_bottom = torch.tensor([True, False, False, True])
    cov = coverage(torch.zeros_like(is_bottom, dtype=torch.float32), is_bottom)
    rej = rejection_loss(is_bottom, target_coverage=0.75)

    assert torch.isclose(cov, torch.tensor(0.5))
    assert torch.isclose(rej, torch.tensor((0.75 - 0.5) ** 2))


def test_training_loss_combines_components():
    fit_loss = torch.tensor(1.0)
    P = torch.tensor([1.0, -1.0])
    Q = torch.tensor([1.0, 1.0])
    Y_n = torch.tensor([1.0, 1.0])
    Y_d = torch.tensor([1.0, 1.0])
    is_bottom = torch.tensor([False, True])
    mask_finite = torch.tensor([1.0, 0.0])

    config = LossConfig(lambda_margin=0.1, lambda_sign=1.0, lambda_rej=0.01, target_coverage=0.9)
    trainer_loss = SCMTrainingLoss(config)
    total, parts = trainer_loss(
        fit_loss,
        P,
        Q,
        Y_n,
        Y_d,
        is_bottom=is_bottom,
        mask_finite=mask_finite,
    )

    margin = margin_loss(Q, tau_train=config.tau_train, mask_finite=mask_finite)
    sign = sign_consistency_loss(P, Q, Y_n, Y_d, gamma=config.gamma)
    rejection = rejection_loss(is_bottom, target_coverage=config.target_coverage)
    expected_total = fit_loss + 0.1 * margin + 1.0 * sign + 0.01 * rejection

    assert torch.allclose(total, expected_total)
    assert torch.allclose(parts["total"], expected_total)
    assert torch.allclose(parts["rejection"], rejection)
