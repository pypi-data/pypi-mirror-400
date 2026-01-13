import pytest

from zeroproof.scm.fracterm import Fracterm, Polynomial
from zeroproof.scm.value import SCMValue, scm_bottom, scm_real


def test_variable_and_constant_construction():
    x = Fracterm.from_variable("x")
    assert x.numerator.terms == {(("x", 1),): 1.0}
    assert x.denominator.terms == {(): 1.0}
    assert x.degrees == (1, 0)

    const = Fracterm.from_constant(3.0)
    assert const.numerator.terms == {(): 3.0}
    assert const.denominator.terms == {(): 1.0}
    assert const.degrees == (0, 0)


def test_flatten_and_arithmetic_composition():
    x = Fracterm.from_variable("x")
    expr = (x + Fracterm.from_constant(1.0)) * x

    num, den = expr.flatten()
    assert den.terms == {(): 1.0}
    # (x + 1) * x = x^2 + x
    assert num.degree == 2
    assert num.terms[(("x", 2),)] == 1.0
    assert num.terms[(("x", 1),)] == 1.0


def test_depth_tracking_and_degree_profile():
    x = Fracterm.from_variable("x")
    expr = x
    for _ in range(4):
        expr = expr * x

    assert expr.depth == 5
    assert expr.degrees == (5, 0)
    assert expr.degree_profile()[-1] == expr.degrees

    num, den = expr.flatten(max_depth=5)
    assert num.degree == 5
    assert den.degree == 0


def test_flatten_enforces_depth_limit():
    x = Fracterm.from_variable("x")
    expr = x
    for _ in range(5):
        expr = expr * x

    assert expr.depth == 6
    with pytest.raises(ValueError):
        expr.flatten(max_depth=5)


def test_evaluation_respects_bottom_and_division_by_zero():
    x = Fracterm.from_variable("x")
    inv_x = Fracterm(Polynomial.constant(1.0), Polynomial.variable("x"))

    finite = (x * inv_x).evaluate({"x": scm_real(2.0)})
    assert isinstance(finite, SCMValue)
    assert finite.value == 1.0

    singular = (x * inv_x).evaluate({"x": scm_real(0.0)})
    assert singular.is_bottom

    bottom_input = x.evaluate({"x": scm_bottom()})
    assert bottom_input.is_bottom


def test_division_by_zero_fraction_propagates_bottom():
    numerator = Fracterm.from_constant(1.0)
    zero_divisor = Fracterm.from_constant(0.0)

    result = (numerator / zero_divisor).evaluate({})

    assert result.is_bottom


def test_polynomial_missing_assignment_raises():
    x = Fracterm.from_variable("x")
    with pytest.raises(KeyError):
        _ = x.evaluate({})


def test_flattening_matches_common_meadow_add_identity():
    x_over_y = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))
    u_over_v = Fracterm(Polynomial.variable("u"), Polynomial.variable("v"))

    num, den = (x_over_y + u_over_v).flatten()

    expected_num = Polynomial.variable("x") * Polynomial.variable("v") + Polynomial.variable("u") * Polynomial.variable("y")
    expected_den = Polynomial.variable("y") * Polynomial.variable("v")

    assert num.terms == expected_num.terms
    assert den.terms == expected_den.terms


def test_flattening_matches_common_meadow_div_identity():
    x_over_y = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))
    u_over_v = Fracterm(Polynomial.variable("u"), Polynomial.variable("v"))

    num, den = (x_over_y / u_over_v).flatten()

    expected_num = Polynomial.variable("x") * Polynomial.variable("v")
    expected_den = Polynomial.variable("y") * Polynomial.variable("u")

    assert num.terms == expected_num.terms
    assert den.terms == expected_den.terms


def test_common_denominator_simplification():
    x_over_y = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))
    z_over_y = Fracterm(Polynomial.variable("z"), Polynomial.variable("y"))

    num, den = (x_over_y + z_over_y).flatten()

    assert den.terms == {(("y", 1),): 1.0}
    assert num.terms == {(("x", 1),): 1.0, (("z", 1),): 1.0}


def test_aggressive_flatten_cancels_singleton_factor():
    x = Polynomial.variable("x")
    fraction = Fracterm(x, x)

    num_safe, den_safe = fraction.flatten()
    # Non-aggressive flattening keeps the singularity intact.
    assert num_safe.terms == x.terms
    assert den_safe.terms == x.terms

    num_flat, den_flat = fraction.flatten(aggressive=True)
    assert num_flat.terms == {(): 1.0}
    assert den_flat.terms == {(): 1.0}


def test_aggressive_flatten_cancels_chain():
    x_over_y = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))
    y_over_z = Fracterm(Polynomial.variable("y"), Polynomial.variable("z"))

    num, den = (x_over_y * y_over_z).flatten(aggressive=True)

    assert num.terms == {(("x", 1),): 1.0}
    assert den.terms == {(("z", 1),): 1.0}


def test_aggressive_flatten_collapses_self_ratio():
    fraction = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))

    num, den = (fraction / fraction).flatten(aggressive=True)

    assert num.terms == {(): 1.0}
    assert den.terms == {(): 1.0}


def test_aggressive_flatten_cancels_numeric_gcd():
    two_x = Polynomial({(("x", 1),): 2.0})
    two = Polynomial.constant(2.0)

    fraction = Fracterm(two_x, two)
    num, den = fraction.flatten(aggressive=True)

    assert num.terms == {(("x", 1),): 1.0}
    assert den.terms == {(): 1.0}


def test_degree_bound_enforced():
    x = Fracterm.from_variable("x")
    high_power = x
    for _ in range(6):
        high_power = high_power * x

    with pytest.raises(ValueError):
        high_power.flatten(max_depth=None, max_degree=5)


def test_symbolic_simplifier_cancels_singleton_common_monomial():
    x_over_y = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))
    z_over_y = Fracterm(Polynomial.variable("z"), Polynomial.variable("y"))

    num, den = (x_over_y / z_over_y).flatten(symbolic="bergstra_tucker")

    assert num.terms == {(("x", 1),): 1.0}
    assert den.terms == {(("z", 1),): 1.0}


def test_unknown_symbolic_simplifier_raises():
    fraction = Fracterm(Polynomial.variable("x"), Polynomial.variable("y"))

    with pytest.raises(KeyError):
        fraction.flatten(symbolic="not_registered")
