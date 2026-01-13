import math

from zeroproof.scm import WeakSignState, scm_bottom, scm_real, weak_sign
from zeroproof.scm.value import SCMValue


def test_basic_sign_behaviour():
    assert weak_sign(scm_bottom()).is_bottom

    assert weak_sign(scm_real(0.0)).value == 0
    assert weak_sign(scm_real(5.0)).value == 1
    assert weak_sign(scm_real(-2.0)).value == -1

    complex_sign = weak_sign(scm_real(3.0) + scm_real(4.0) * 1j)
    assert math.isclose(abs(complex_sign.value), 1.0)


def test_history_lock_and_release():
    state = WeakSignState(epsilon=0.1, hysteresis=0.5)

    first = weak_sign(scm_real(2.0), state)
    assert first.value == 1
    assert state.last_sign == 1

    locked = weak_sign(scm_real(0.05), state)
    assert locked.value == 1

    still_locked = weak_sign(scm_real(-0.12), state)
    assert still_locked.value == 1

    flipped = weak_sign(scm_real(-0.2), state)
    assert flipped.value == -1
    assert state.last_sign == -1


def test_stateless_zero_does_not_update_history():
    state = WeakSignState()
    zero_sign = weak_sign(scm_real(0.0), state)
    assert zero_sign.value == 0
    assert state.last_sign is None


def test_unit_circle_projection_stable():
    angles = [0.0, math.pi / 4, math.pi / 2, math.pi, -math.pi / 2]
    for angle in angles:
        z = SCMValue(math.cos(angle) + 1j * math.sin(angle))
        sign = weak_sign(z)
        assert not sign.is_bottom
        assert math.isclose(abs(sign.value), 1.0)
