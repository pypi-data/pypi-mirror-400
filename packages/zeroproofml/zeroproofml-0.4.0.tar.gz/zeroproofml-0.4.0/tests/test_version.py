from zeroproof import __version__
from zeroproof.scm.value import scm_bottom


def test_version_is_v0_4_series():
    assert __version__.startswith("0.4.")


def test_bottom_repr():
    assert "⊥" in repr(scm_bottom())
