import pytest

pytest.importorskip("torch")

from zeroproof.training import perturbed_threshold


def test_perturbed_threshold_in_range():
    tau_min, tau_max = 1e-4, 2e-4
    for _ in range(5):
        tau = perturbed_threshold(tau_min, tau_max)
        assert tau_min <= tau <= tau_max


def test_perturbed_threshold_raises_on_invalid_bounds():
    with pytest.raises(ValueError):
        perturbed_threshold(0.2, 0.1)
