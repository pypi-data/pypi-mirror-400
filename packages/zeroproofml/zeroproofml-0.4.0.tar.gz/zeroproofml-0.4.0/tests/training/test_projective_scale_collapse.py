import pytest

torch = pytest.importorskip("torch")

from zeroproof.losses.implicit import implicit_loss


def _decoded_mse(P: torch.Tensor, Q: torch.Tensor, Y: torch.Tensor, *, tau_train: float) -> torch.Tensor:
    q_abs = torch.abs(Q)
    q_sign = torch.sign(Q)
    q_sign = torch.where(q_sign == 0, torch.ones_like(q_sign), q_sign)
    denom_safe = q_sign * torch.clamp_min(q_abs, float(tau_train))
    decoded = P / denom_safe
    return torch.mean((decoded - Y) ** 2)


def test_projective_scale_collapse_can_reduce_implicit_loss_but_hurt_decoded_mse():
    # This test encodes a key failure mode: in projective space, the implicit
    # cross-product loss can be reduced by shrinking (P,Q), especially when
    # gamma dominates the detached scale, even if decoded-space error under the
    # τ-clamped decoding gets worse.
    tau = 1e-4
    gamma = 1e-9

    Y = torch.tensor([2.0], dtype=torch.float64)
    Y_n = Y.clone()
    Y_d = torch.ones_like(Y)

    P_good = torch.tensor([1.9], dtype=torch.float64)
    Q_good = torch.tensor([1.0], dtype=torch.float64)

    k = 1e-8
    P_collapse = k * P_good
    Q_collapse = k * Q_good

    implicit_good = implicit_loss(P_good, Q_good, Y_n, Y_d, gamma=gamma)
    implicit_collapse = implicit_loss(P_collapse, Q_collapse, Y_n, Y_d, gamma=gamma)
    assert float(implicit_collapse.item()) < float(implicit_good.item())

    decoded_good = _decoded_mse(P_good, Q_good, Y, tau_train=tau)
    decoded_collapse = _decoded_mse(P_collapse, Q_collapse, Y, tau_train=tau)
    assert float(decoded_collapse.item()) > float(decoded_good.item())

    # Sanity: the combined objective used by SCM runners should penalize this.
    lambda_decoded = 1.0
    lambda_implicit = 0.1
    combined_good = lambda_decoded * decoded_good + lambda_implicit * implicit_good
    combined_collapse = lambda_decoded * decoded_collapse + lambda_implicit * implicit_collapse
    assert float(combined_collapse.item()) > float(combined_good.item())

