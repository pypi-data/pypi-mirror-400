import math

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import given
from hypothesis import strategies as st

pytestmark = pytest.mark.property

from zeroproof.scm.fracterm import Fracterm
from zeroproof.scm.value import scm_real

finite_nonzero = st.floats(allow_nan=False, allow_infinity=False, width=64).filter(
    lambda x: abs(x) > 1e-6
)


@given(x=finite_nonzero, y=finite_nonzero)
def test_flattened_fraction_matches_composed_expression(x: float, y: float) -> None:
    """Flattening should preserve evaluation semantics for composite expressions."""

    ft_x = Fracterm.from_variable("x")
    ft_y = Fracterm.from_variable("y")
    expr = (ft_x * ft_y + Fracterm.from_constant(2.0)) / ft_y

    numerator, denominator = expr.flatten()
    flattened = Fracterm(numerator, denominator)

    evaluated = flattened.evaluate({"x": scm_real(x), "y": scm_real(y)})
    expected = scm_real((x * y + 2.0) / y)

    assert not evaluated.is_bottom
    assert math.isclose(evaluated.value, expected.value, rel_tol=1e-9, abs_tol=1e-9)


@given(x=finite_nonzero, y=finite_nonzero, z=finite_nonzero)
def test_bergstra_tucker_division_identity(x: float, y: float, z: float) -> None:
    """(x/y)/(z/y) simplifies to x/z under the Bergstra–Tucker cancellative rule."""

    ft_x = Fracterm.from_variable("x")
    ft_y = Fracterm.from_variable("y")
    ft_z = Fracterm.from_variable("z")

    expr = (ft_x / ft_y) / (ft_z / ft_y)
    num, den = expr.flatten(symbolic="bergstra_tucker")
    flattened = Fracterm(num, den)

    evaluated = flattened.evaluate({"x": scm_real(x), "y": scm_real(y), "z": scm_real(z)})
    expected = scm_real(x / z)

    assert not evaluated.is_bottom
    assert math.isclose(evaluated.value, expected.value, rel_tol=1e-9, abs_tol=1e-9)


@given(x=finite_nonzero, y=finite_nonzero)
def test_bergstra_tucker_self_ratio_identity(x: float, y: float) -> None:
    """(x/y)/(x/y) collapses to 1 with symbolic simplification."""

    ft_x = Fracterm.from_variable("x")
    ft_y = Fracterm.from_variable("y")

    expr = (ft_x / ft_y) / (ft_x / ft_y)
    num, den = expr.flatten(symbolic="bergstra_tucker")
    flattened = Fracterm(num, den)

    evaluated = flattened.evaluate({"x": scm_real(x), "y": scm_real(y)})
    expected = scm_real(1.0)

    assert not evaluated.is_bottom
    assert math.isclose(evaluated.value, expected.value, rel_tol=1e-9, abs_tol=1e-9)
