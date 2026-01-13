import pytest

torch = pytest.importorskip("torch")
from torch.autograd import gradcheck

from zeroproof.losses.implicit import implicit_loss
from zeroproof.losses.sign import sign_consistency_loss


def _requires_grad_tensor(values):
    return torch.tensor(values, dtype=torch.float64, requires_grad=True)


@pytest.mark.autograd
def test_implicit_loss_backward_matches_detached_scale_formula():
    P = _requires_grad_tensor([0.7, -0.2])
    Q = _requires_grad_tensor([0.3, 0.8])
    Y_n = _requires_grad_tensor([0.1, -0.5])
    Y_d = _requires_grad_tensor([1.2, -1.1])

    gamma = 1e-9
    loss = implicit_loss(P, Q, Y_n, Y_d, gamma=gamma)
    loss.backward()

    assert P.grad is not None
    assert Q.grad is not None
    assert torch.isfinite(P.grad).all()
    assert torch.isfinite(Q.grad).all()

    with torch.no_grad():
        P_det = P.detach()
        Q_det = Q.detach()
        Y_n_det = Y_n.detach()
        Y_d_det = Y_d.detach()
        cross = P_det * Y_d_det - Q_det * Y_n_det
        scale_sq = (Q_det.pow(2) * Y_d_det.pow(2) + P_det.pow(2) * Y_n_det.pow(2)) + gamma
        denom = float(cross.numel())
        expected_grad_P = (2.0 * cross * Y_d_det / scale_sq) / denom
        expected_grad_Q = (-2.0 * cross * Y_n_det / scale_sq) / denom

    assert torch.allclose(P.grad, expected_grad_P, atol=1e-9, rtol=1e-6)
    assert torch.allclose(Q.grad, expected_grad_Q, atol=1e-9, rtol=1e-6)


@pytest.mark.autograd
def test_sign_consistency_gradients_match_finite_differences():
    P = _requires_grad_tensor([0.25, -0.4])
    Q = _requires_grad_tensor([0.9, 0.2])
    Y_n = _requires_grad_tensor([-0.15, 0.6])
    Y_d = _requires_grad_tensor([1.1, -0.7])

    assert gradcheck(
        lambda p, q, yn, yd: sign_consistency_loss(p, q, yn, yd),
        (P, Q, Y_n, Y_d),
        eps=1e-6,
        atol=1e-4,
    )
