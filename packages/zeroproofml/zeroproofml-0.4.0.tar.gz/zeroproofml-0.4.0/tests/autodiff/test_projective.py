import pytest

from zeroproof.autodiff.projective import (
    ProjectiveSample,
    decode,
    encode,
    projectively_equal,
    renormalize,
)
from zeroproof.scm.value import scm_bottom, scm_real


def test_encode_decode_roundtrip():
    value = scm_real(2.5)
    encoded = encode(value)
    assert encoded == ProjectiveSample(2.5, 1.0)
    decoded = decode(encoded)
    assert decoded.value == 2.5 and not decoded.is_bottom


def test_bottom_maps_to_infinity():
    bottom = scm_bottom()
    encoded = encode(bottom)
    assert encoded.denominator == 0.0
    decoded = decode(encoded)
    assert decoded.is_bottom


def test_projective_equality():
    a = ProjectiveSample(2.0, 1.0)
    b = ProjectiveSample(4.0, 2.0)
    c = ProjectiveSample(1.0, 0.0)
    assert projectively_equal(a, b)
    assert not projectively_equal(a, c)


def test_detached_renormalization_respects_stop_gradient_hook():
    calls: list[float] = []

    def stop_grad(x: float) -> float:
        calls.append(x)
        return x

    n, d = renormalize(3.0, 4.0, gamma=0.0, stop_gradient=stop_grad)
    assert calls  # ensure stop_grad was invoked
    assert abs((n**2 + d**2) - 1.0) < 1e-8


def test_renormalize_detaches_torch_norm_by_default():
    torch = pytest.importorskip("torch")

    numerator = torch.tensor(3.0, requires_grad=True)
    denominator = torch.tensor(4.0, requires_grad=True)

    n_detached, d_detached = renormalize(numerator, denominator, gamma=0.0)
    loss_detached = n_detached + d_detached
    loss_detached.backward()
    grads_detached = (numerator.grad.clone(), denominator.grad.clone())

    numerator.grad = None
    denominator.grad = None

    scale = torch.sqrt(numerator**2 + denominator**2) + 0.0
    n_attached = numerator / scale
    d_attached = denominator / scale
    (n_attached + d_attached).backward()
    grads_attached = (numerator.grad.clone(), denominator.grad.clone())

    numerator.grad = None
    denominator.grad = None

    scale_manual = torch.sqrt(numerator**2 + denominator**2).detach()
    n_manual = numerator / scale_manual
    d_manual = denominator / scale_manual
    (n_manual + d_manual).backward()
    grads_manual = (numerator.grad.clone(), denominator.grad.clone())

    assert torch.allclose(grads_detached[0], grads_manual[0])
    assert torch.allclose(grads_detached[1], grads_manual[1])
    assert not torch.allclose(grads_detached[0], grads_attached[0])
    assert not torch.allclose(grads_detached[1], grads_attached[1])
