import pytest

torch = pytest.importorskip("torch")

from zeroproof.layers.projective_rational import (
    ProjectiveRationalMultiHead,
    ProjectiveRRModelConfig,
    RRProjectiveRationalModel,
)


def test_projective_rational_multihead_shapes_and_backward():
    head = ProjectiveRationalMultiHead(
        output_dim=2, numerator_degree=3, denominator_degree=2, q_anchor="ones"
    )
    z_num = torch.randn(5, 2, dtype=torch.float64, requires_grad=True)
    z_den = torch.randn(5, 1, dtype=torch.float64, requires_grad=True)
    P, Q = head(z_num, z_den)
    assert P.shape == (5, 2)
    assert Q.shape == (5, 2)

    loss = (P.pow(2) + Q.pow(2)).mean()
    loss.backward()
    assert z_num.grad is not None
    assert z_den.grad is not None


def test_rr_projective_rational_model_forward_shapes():
    cfg = ProjectiveRRModelConfig(
        hidden_dims=(8,), numerator_degree=2, denominator_degree=2, q_anchor="ones"
    )
    model = RRProjectiveRationalModel(cfg)
    x = torch.randn(7, 4)
    P, Q = model(x)
    assert P.shape == (7, 2)
    assert Q.shape == (7, 2)
