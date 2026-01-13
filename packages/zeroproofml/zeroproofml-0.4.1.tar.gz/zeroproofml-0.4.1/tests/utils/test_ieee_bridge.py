import math

from zeroproof.scm.value import scm_bottom, scm_real
from zeroproof.utils.ieee_bridge import batch_from_ieee, batch_to_ieee, from_ieee, to_ieee


def test_scalar_conversion_roundtrip():
    value = from_ieee(1.5)
    assert value == scm_real(1.5)
    assert to_ieee(value) == 1.5


def test_bottom_conversion_for_specials():
    bottom_from_nan = from_ieee(float("nan"))
    bottom_from_inf = from_ieee(float("inf"))

    assert bottom_from_nan.is_bottom
    assert bottom_from_inf.is_bottom
    assert math.isnan(to_ieee(bottom_from_nan))
    assert math.isnan(to_ieee(bottom_from_inf))


def test_batch_helpers_and_bool_rejection():
    batch = batch_from_ieee([0.0, float("inf"), -2.0])
    assert [v.is_bottom for v in batch] == [False, True, False]
    assert batch_to_ieee(batch)[0] == 0.0

    try:
        from_ieee(True)
    except TypeError:
        pass
    else:  # pragma: no cover - defensive
        assert False, "bool input should raise"
