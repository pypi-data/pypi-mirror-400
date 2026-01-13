import math

import pytest

torch = pytest.importorskip("torch")
from torch import nn

from zeroproof.inference import (
    InferenceConfig,
    SCMInferenceWrapper,
    script_module,
    strict_inference,
    strict_inference_jax,
)

try:  # pragma: no cover - optional dependency
    import jax.numpy as jnp
except Exception:  # pragma: no cover - optional dependency
    jnp = None


class TupleModel(nn.Module):
    def forward(self, x):  # pragma: no cover - simple wiring
        return x + 1, x


def test_training_mode_passthrough():
    model = SCMInferenceWrapper(TupleModel())
    model.train()
    numer, denom = model(torch.tensor([1.0]))
    assert numer.tolist() == [2.0]
    assert denom.tolist() == [1.0]


def test_inference_bottom_and_gap_masks():
    config = InferenceConfig(tau_infer=1e-4, tau_train=1e-3)
    model = SCMInferenceWrapper(TupleModel(), config=config)
    model.eval()

    numer = torch.tensor([1.0, 1.0, 1.0])
    denom = torch.tensor([1e-5, 5e-4, 1.0])
    decoded, bottom_mask, gap_mask = model((numer, denom))

    assert math.isnan(decoded[0])
    assert decoded[1].item() == pytest.approx(2.0)
    assert decoded[2].item() == pytest.approx(2.0)

    assert bottom_mask.tolist() == [True, False, False]
    assert gap_mask.tolist() == [False, True, False]


def test_strict_inference_respects_nan_inputs():
    numer = torch.tensor([float("nan"), 1.0])
    denom = torch.tensor([1.0, 0.5])
    decoded, bottom_mask, gap_mask = strict_inference(numer, denom)

    assert math.isnan(decoded[0])
    assert not math.isnan(decoded[1])
    assert bottom_mask.tolist() == [True, False]
    assert not gap_mask.any()


def test_script_module_preserves_inference_path():
    model = SCMInferenceWrapper(TupleModel())
    scripted = script_module(model)
    scripted.eval()
    decoded, bottom_mask, gap_mask = scripted(torch.tensor([1.0]))

    assert decoded.item() == pytest.approx(2.0)
    assert bottom_mask.item() is False
    assert gap_mask.item() is False


@pytest.mark.skipif(jnp is None, reason="JAX not installed")
def test_strict_inference_jax_parity():
    numer = jnp.array([1.0, jnp.nan])
    denom = jnp.array([1e-6, 0.0])
    decoded, bottom_mask, gap_mask = strict_inference_jax(numer, denom)

    assert math.isnan(decoded[1])
    assert bool(bottom_mask[1]) is True
    assert bool(gap_mask[0]) is False
