import pytest

torch = pytest.importorskip("torch")

from zeroproof.layers import (
    FractermRationalUnit,
    SCMNorm,
    SCMRationalLayer,
    SCMSoftmax,
)
from zeroproof.layers.scm_rational import apply_policy_vectorized
from zeroproof.autodiff.policies import GradientPolicy


def test_fru_enforces_depth_and_bounds():
    fru = FractermRationalUnit(numerator_degree=1, denominator_degree=2, depth=3)
    # depth=3 -> factor 4 * max(1,2) = 8
    assert fru.current_bounds == (8, 8)
    profile = fru.degree_profile()
    assert profile[0] == (2, 2)
    assert profile[-1] == (8, 8)

    fru.extend(1)
    assert fru.current_bounds == (16, 16)


def test_fru_rejects_depth_over_max():
    fru = FractermRationalUnit(numerator_degree=1, denominator_degree=1, depth=5)
    try:
        fru.extend(1)
        assert False, "Expected ValueError for depth overflow"
    except ValueError:
        pass


def test_scm_rational_forward_and_bottom_mask():
    layer = SCMRationalLayer(1, 1)
    with torch.no_grad():
        layer.numerator.copy_(torch.tensor([0.0, 1.0]))
        layer.denominator.copy_(torch.tensor([1.0, 0.0]))

    x = torch.tensor([1.0, 2.0])
    output, mask = layer(x)
    assert torch.allclose(output, x)
    assert not mask.any()

    # Force denominator to zero to trigger bottom masking
    with torch.no_grad():
        layer.denominator.zero_()
    output, mask = layer(x)
    assert mask.all()
    assert torch.isinf(output).all()


def test_scm_norm_excludes_bottom_and_handles_singular_variance():
    norm = SCMNorm()
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    bottom_mask = torch.tensor([[False, True], [False, False]])
    out, out_mask = norm(x, bottom_mask=bottom_mask)

    # First column has variance, second column singular due to single valid entry
    assert out_mask[:, 1].all()
    assert not out_mask[:, 0].any()
    # Column 0 normalisation should be centred
    assert torch.allclose(out[:, 0], torch.tensor([-1.0, 1.0]))


def test_scm_softmax_one_hot_on_singular_rows():
    softmax = SCMSoftmax()
    logits = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    bottom_mask = torch.tensor([[False, False], [True, False]])
    probs, row_mask = softmax(logits, bottom_mask=bottom_mask)

    assert not row_mask[0]
    assert row_mask[1]
    assert torch.allclose(probs[1], torch.tensor([0.0, 1.0]))


def test_apply_policy_vectorized_tensor_masks():
    grads = torch.tensor([[-2.0, 0.5], [3.0, -0.1]])
    mask = torch.tensor([[False, True], [True, False]])

    projected = apply_policy_vectorized(grads, mask, GradientPolicy.PROJECT)
    assert torch.equal(
        projected, torch.tensor([[-2.0, 0.0], [0.0, -0.1]])
    )

    clamped = apply_policy_vectorized(grads, mask, GradientPolicy.CLAMP)
    assert torch.equal(
        clamped, torch.tensor([[-1.0, 0.0], [0.0, -0.1]])
    )


def test_apply_policy_vectorized_complex_passthrough():
    grads = torch.tensor([1 + 2j, 3 + 4j])
    mask = torch.tensor([True, False])

    clamped = apply_policy_vectorized(grads, mask, GradientPolicy.CLAMP)
    assert torch.equal(clamped, torch.tensor([0.0 + 0.0j, 3.0 + 4.0j]))
