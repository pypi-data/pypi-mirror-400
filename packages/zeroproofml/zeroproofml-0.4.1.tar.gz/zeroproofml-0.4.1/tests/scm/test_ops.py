import cmath
import math

from zeroproof.scm import (
    SCMValue,
    scm_add,
    scm_bottom,
    scm_cos,
    scm_div,
    scm_exp,
    scm_inv,
    scm_log,
    scm_mul,
    scm_neg,
    scm_pow,
    scm_real,
    scm_sin,
    scm_sqrt,
    scm_sub,
    scm_tan,
)


def test_basic_arithmetic_absorbs_bottom():
    x = scm_real(2.0)
    y = scm_real(3.0)
    bottom = scm_bottom()

    assert scm_add(x, y).value == 5.0
    assert scm_add(x, bottom).is_bottom
    assert scm_mul(x, y).value == 6.0
    assert scm_mul(bottom, y).is_bottom


def test_division_and_inverse():
    x = scm_real(4.0)
    zero = scm_real(0.0)

    assert scm_div(x, scm_real(2.0)).value == 2.0
    assert scm_div(x, zero).is_bottom
    assert scm_div(scm_bottom(), x).is_bottom

    assert scm_inv(x).value == 0.25
    assert scm_inv(zero).is_bottom


def test_pow_and_negation_rules():
    zero = scm_real(0.0)
    assert scm_pow(zero, -1).is_bottom
    assert scm_neg(scm_real(5.0)).value == -5.0


def test_transcendentals_with_domain_checks():
    assert scm_log(scm_real(math.e)).value == 1.0
    assert scm_log(scm_real(-1.0)).is_bottom
    assert scm_log(scm_real(0.0)).is_bottom

    assert scm_exp(scm_real(1.0)).value == math.e

    assert scm_sqrt(scm_real(9.0)).value == 3.0
    assert scm_sqrt(scm_real(-1.0)).is_bottom

    bottom = scm_bottom()
    assert scm_sin(bottom).is_bottom
    assert scm_cos(bottom).is_bottom
    assert scm_tan(bottom).is_bottom


def test_complex_paths():
    z = SCMValue(1 + 1j)
    assert scm_log(z).value == cmath.log(1 + 1j)
    assert scm_sqrt(z).value == cmath.sqrt(1 + 1j)

    zero_complex = SCMValue(0 + 0j)
    assert scm_log(zero_complex).is_bottom
