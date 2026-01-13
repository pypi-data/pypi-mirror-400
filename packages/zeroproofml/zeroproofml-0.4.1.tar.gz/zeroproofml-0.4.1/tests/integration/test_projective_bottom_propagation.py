import pytest

torch = pytest.importorskip("torch")

from zeroproof.inference.mode import InferenceConfig, strict_inference
from zeroproof.layers import SCMRationalLayer


def _evaluate_tuple(layer: SCMRationalLayer, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Recompute (P, Q) projective tuple from the layer parameters."""

    basis_feats = layer.basis(x, max(layer.numerator_degree, layer.denominator_degree))
    p_feats = basis_feats[..., : layer.numerator_degree + 1]
    q_feats = basis_feats[..., : layer.denominator_degree + 1]

    numerator = torch.sum(p_feats * layer.numerator, dim=-1)
    denominator = torch.sum(q_feats * layer.denominator, dim=-1)
    return numerator, denominator


def test_projective_decode_uses_single_output_bottom_check() -> None:
    layer = SCMRationalLayer(0, 1)
    with torch.no_grad():
        layer.numerator.copy_(torch.tensor([1.0]))
        layer.denominator.copy_(torch.tensor([0.0, 1.0]))

    x = torch.tensor([-1.0, 0.0, 2.0])
    raw_output, layer_bottom_mask = layer(x)

    # Forward pass reports singular denominator but leaves raw outputs untouched.
    assert torch.allclose(raw_output[[0, 2]], torch.tensor([-1.0, 0.5]))
    assert torch.isinf(raw_output[1])
    assert layer_bottom_mask.tolist() == [False, True, False]

    numerator, denominator = _evaluate_tuple(layer, x)
    decoded, infer_bottom_mask, gap_mask = strict_inference(
        numerator, denominator, config=InferenceConfig(tau_infer=1e-6)
    )

    # Decoding applies the single bottom check on the denominator and propagates ⊥ once.
    assert torch.equal(layer_bottom_mask, infer_bottom_mask)
    assert torch.isnan(decoded[1])
    assert torch.allclose(decoded[[0, 2]], torch.tensor([-1.0, 0.5]))
    assert not gap_mask.any()
