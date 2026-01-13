import pytest

from zeroproof.scm.value import SCMValue, scm_bottom, scm_complex, scm_real


def test_factories_produce_expected_values():
    real = scm_real(1.5)
    assert real.value == 1.5
    assert not real.is_bottom

    complex_val = scm_complex(1 + 2j)
    assert complex_val.value == 1 + 2j
    assert not complex_val.is_bottom

    bottom = scm_bottom()
    assert bottom.is_bottom
    assert bottom.value is None


def test_repr_shows_bottom_symbol():
    assert "⊥" in repr(scm_bottom())
    assert "1.0" in repr(scm_real(1.0))


def test_addition_and_multiplication_absorb_bottom():
    x = scm_real(2.0)
    y = scm_real(3.0)
    bottom = scm_bottom()

    assert (x + y).value == 5.0
    assert (x + bottom).is_bottom
    assert (bottom + y).is_bottom

    assert (x * y).value == 6.0
    assert (x * bottom).is_bottom
    assert (bottom * y).is_bottom


def test_division_absorbs_zero_and_bottom():
    x = scm_real(4.0)
    zero = scm_real(0.0)
    bottom = scm_bottom()

    assert (x / scm_real(2.0)).value == 2.0
    assert (x / zero).is_bottom
    assert (x / bottom).is_bottom
    assert (bottom / x).is_bottom


def test_negation_and_subtraction():
    x = scm_real(5.0)
    assert (-x).value == -5.0

    y = scm_real(2.0)
    assert (x - y).value == 3.0
    assert (y - x).value == -3.0


def test_division_by_zero_with_complex_numbers():
    z = scm_complex(1 + 1j)
    zero = scm_complex(0 + 0j)
    result = z / zero
    assert result.is_bottom


def test_numeric_coercion_disallows_boolean():
    with pytest.raises(TypeError):
        _ = scm_real(1.0) + True  # type: ignore[arg-type]
