import math

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

pytestmark = pytest.mark.property

from zeroproof.autodiff import projective
from zeroproof.scm import (
    WeakSignState,
    scm_add,
    scm_cos,
    scm_div,
    scm_exp,
    scm_log,
    scm_mul,
    scm_neg,
    scm_pow,
    scm_sin,
    scm_sqrt,
    scm_sub,
    scm_tan,
)
from zeroproof.scm.sign import weak_sign
from zeroproof.scm.value import SCMValue, scm_bottom, scm_real

finite_floats = st.floats(allow_nan=False, allow_infinity=False, width=64)
bdd_floats = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False, width=64
)
unit_angles = st.floats(
    min_value=-math.pi, max_value=math.pi, allow_nan=False, allow_infinity=False, width=64
)
bottom_or_real = st.one_of(bdd_floats.map(scm_real), st.just(scm_bottom()))
near_zero_noise = st.lists(
    st.floats(min_value=-5e-7, max_value=5e-7, allow_nan=False, allow_infinity=False, width=64),
    min_size=1,
    max_size=8,
)


def _nonzero_floats(min_abs: float = 1e-12):
    return finite_floats.filter(lambda x: abs(x) >= min_abs)


def _require_torch():
    return pytest.importorskip("torch")


@given(x=finite_floats)
def test_scm_absorptivity(x: float) -> None:
    value = scm_real(x)
    bottom = scm_bottom()

    assert (value + bottom).is_bottom
    assert (value * bottom).is_bottom
    assert (value / scm_real(0.0)).is_bottom


@given(a=bdd_floats, b=bdd_floats, c=bdd_floats)
def test_addition_commutes_and_associates(a: float, b: float, c: float) -> None:
    first = scm_add(scm_real(a), scm_real(b))
    second = scm_add(scm_real(b), scm_real(a))

    assert math.isclose(first.value, second.value, rel_tol=1e-9, abs_tol=1e-9)

    left = scm_add(scm_real(a), scm_add(scm_real(b), scm_real(c)))
    right = scm_add(scm_add(scm_real(a), scm_real(b)), scm_real(c))

    assert math.isclose(left.value, right.value, rel_tol=1e-9, abs_tol=1e-9)


@given(a=bdd_floats, b=bdd_floats, c=bdd_floats)
def test_multiplication_commutes_and_associates(a: float, b: float, c: float) -> None:
    first = scm_mul(scm_real(a), scm_real(b))
    second = scm_mul(scm_real(b), scm_real(a))

    assert math.isclose(first.value, second.value, rel_tol=1e-9, abs_tol=1e-9)

    left = scm_mul(scm_real(a), scm_mul(scm_real(b), scm_real(c)))
    right = scm_mul(scm_mul(scm_real(a), scm_real(b)), scm_real(c))

    assert math.isclose(left.value, right.value, rel_tol=1e-9, abs_tol=1e-9)


@given(x=_nonzero_floats())
def test_weak_sign_has_unit_magnitude(x: float) -> None:
    sign = weak_sign(scm_real(x))

    assert not sign.is_bottom
    assert math.isclose(abs(sign.value), 1.0, rel_tol=1e-12, abs_tol=1e-12)


@given(angle=unit_angles)
def test_unit_circle_sign_projection_stable(angle: float) -> None:
    point = SCMValue(math.cos(angle) + 1j * math.sin(angle))
    sign = weak_sign(point)

    assert not sign.is_bottom
    assert math.isclose(abs(sign.value), 1.0, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(sign.value.real, math.cos(angle), rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(sign.value.imag, math.sin(angle), rel_tol=1e-9, abs_tol=1e-9)


@given(
    numerator=finite_floats,
    denominator=finite_floats,
    scale=_nonzero_floats(),
)
def test_projective_invariance(numerator: float, denominator: float, scale: float) -> None:
    sample = projective.ProjectiveSample(numerator, denominator)
    if denominator != 0:
        scaled_n = numerator * scale
        scaled_d = denominator * scale
        assume(math.isfinite(scaled_n) and math.isfinite(scaled_d))
        scaled = projective.ProjectiveSample(scaled_n, scaled_d)
    else:
        scaled = projective.ProjectiveSample(numerator * scale, denominator * scale)

    decoded = projective.decode(sample)
    decoded_scaled = projective.decode(scaled)

    if denominator == 0:
        assert decoded.is_bottom
        assert decoded_scaled.is_bottom
    else:
        assert math.isclose(decoded.value, decoded_scaled.value, rel_tol=1e-12, abs_tol=1e-12)


@given(
    P=_nonzero_floats(),
    Q=_nonzero_floats(),
    Yn=_nonzero_floats(),
    Yd=_nonzero_floats(),
)
def test_sign_loss_symmetry(P: float, Q: float, Yn: float, Yd: float) -> None:
    torch = _require_torch()
    from zeroproof.losses.sign import sign_consistency_loss

    pred = torch.tensor([P, Q], dtype=torch.float64)
    target = torch.tensor([Yn, Yd], dtype=torch.float64)

    loss = sign_consistency_loss(pred[0:1], pred[1:2], target[0:1], target[1:2])
    loss_flipped = sign_consistency_loss(-pred[0:1], -pred[1:2], -target[0:1], -target[1:2])

    assert torch.isclose(loss, loss_flipped, rtol=1e-12, atol=1e-12)


@given(x=bottom_or_real, y=bottom_or_real)
def test_bottom_absorbs_binary_ops(x: SCMValue, y: SCMValue) -> None:
    bottom = scm_bottom()

    for op in (scm_add, scm_sub, scm_mul, scm_div):
        assert op(bottom, x).is_bottom
        assert op(x, bottom).is_bottom
        assert op(bottom, y).is_bottom


def test_bottom_absorbs_unary_ops() -> None:
    bottom = scm_bottom()

    for op in (scm_neg, scm_log, scm_exp, scm_sqrt, scm_sin, scm_cos, scm_tan):
        assert op(bottom).is_bottom


@given(exponent=finite_floats)
def test_bottom_absorbs_power(exponent: float) -> None:
    assert scm_pow(scm_bottom(), exponent).is_bottom


def _assert_equal_scm(lhs: SCMValue, rhs: SCMValue) -> None:
    if lhs.is_bottom or rhs.is_bottom:
        assert lhs.is_bottom == rhs.is_bottom
    else:
        assert math.isclose(lhs.value, rhs.value, rel_tol=1e-9, abs_tol=1e-9)


@given(a=bottom_or_real, b=bottom_or_real)
def test_addition_commutes_with_bottom(a: SCMValue, b: SCMValue) -> None:
    _assert_equal_scm(scm_add(a, b), scm_add(b, a))


@given(a=bottom_or_real, b=bottom_or_real)
def test_multiplication_commutes_with_bottom(a: SCMValue, b: SCMValue) -> None:
    _assert_equal_scm(scm_mul(a, b), scm_mul(b, a))


@given(a=bottom_or_real, b=bottom_or_real, c=bottom_or_real)
def test_addition_associates_with_bottom(a: SCMValue, b: SCMValue, c: SCMValue) -> None:
    left = scm_add(a, scm_add(b, c))
    right = scm_add(scm_add(a, b), c)

    _assert_equal_scm(left, right)


@given(a=bottom_or_real, b=bottom_or_real, c=bottom_or_real)
def test_multiplication_associates_with_bottom(a: SCMValue, b: SCMValue, c: SCMValue) -> None:
    left = scm_mul(a, scm_mul(b, c))
    right = scm_mul(scm_mul(a, b), c)

    _assert_equal_scm(left, right)


@given(anchor=_nonzero_floats(1e-3), jitters=near_zero_noise)
def test_history_sign_stable_near_zero(anchor: float, jitters: list[float]) -> None:
    state = WeakSignState(epsilon=1e-6, hysteresis=0.5)
    baseline = weak_sign(scm_real(anchor), state)

    for jitter in jitters:
        locked = weak_sign(scm_real(jitter), state)
        assert not locked.is_bottom
        assert locked.value == baseline.value
