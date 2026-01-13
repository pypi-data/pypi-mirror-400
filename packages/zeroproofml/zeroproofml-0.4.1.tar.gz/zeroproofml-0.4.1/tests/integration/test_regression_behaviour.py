import math

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import assume, given
from hypothesis import strategies as st

from zeroproof.scm.ops import scm_div, scm_log, scm_mul, scm_sqrt
from zeroproof.scm.value import scm_real

finite_nonzero = st.floats(allow_nan=False, allow_infinity=False, width=64).filter(
    lambda v: abs(v) > 1e-6
)
finite_positive = st.floats(
    min_value=1e-6, max_value=1e6, allow_infinity=False, allow_nan=False, width=64
)


@given(x=finite_nonzero, y=finite_nonzero)
def test_division_matches_real_arithmetic_on_regular_inputs(x: float, y: float) -> None:
    expected = x / y
    assume(math.isfinite(expected))
    result = scm_div(scm_real(x), scm_real(y))

    assert not result.is_bottom
    assert math.isfinite(result.value)
    assert math.isclose(result.value, expected, rel_tol=1e-9, abs_tol=1e-9)


@given(x=finite_nonzero, y=finite_nonzero)
def test_multiplication_matches_real_arithmetic_on_regular_inputs(x: float, y: float) -> None:
    result = scm_mul(scm_real(x), scm_real(y))

    assert not result.is_bottom
    assert math.isclose(result.value, x * y, rel_tol=1e-9, abs_tol=1e-9)


@given(x=finite_positive)
def test_log_and_sqrt_match_real_on_positive_inputs(x: float) -> None:
    log_result = scm_log(scm_real(x))
    sqrt_result = scm_sqrt(scm_real(x))

    assert not log_result.is_bottom
    assert not sqrt_result.is_bottom

    assert math.isclose(log_result.value, math.log(x), rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(sqrt_result.value, math.sqrt(x), rel_tol=1e-9, abs_tol=1e-9)
