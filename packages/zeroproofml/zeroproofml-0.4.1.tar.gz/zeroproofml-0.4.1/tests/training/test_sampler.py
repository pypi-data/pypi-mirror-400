import pytest

torch = pytest.importorskip("torch")
from torch.utils.data import Dataset

from zeroproof.training import (
    AdaptiveSampler,
    AdaptiveSamplerConfig,
    sampling_weights,
    singularity_prob,
)


class DummyDataset(Dataset):
    def __init__(self, values: torch.Tensor) -> None:
        self.values = values

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, idx: int):  # pragma: no cover - trivial
        return self.values[idx]


def test_singularity_prob_matches_spec():
    q = torch.tensor([0.0, 1e-4, 1e-3])
    tau = 1e-4
    beta = 0.1
    probs = singularity_prob(q, tau, beta)
    expected = torch.sigmoid((tau - torch.abs(q)) / beta)
    assert torch.allclose(probs, expected)


def test_sampling_weights_floor_and_bottom_mask():
    probs = torch.tensor([0.0, 0.5, 1.0])
    bottom_mask = torch.tensor([0.0, 1.0, 0.0])
    weights = sampling_weights(probs, bottom_mask, alpha=2.0, s_min=0.75)
    assert torch.all(weights >= 0.75)
    deviation = torch.abs(probs - bottom_mask)
    expected = torch.clamp(1 + 2.0 * deviation, min=0.75)
    assert torch.allclose(weights, expected)


def test_adaptive_sampler_updates_weights_and_builds_loader():
    dataset = DummyDataset(torch.arange(4.0))
    sampler = AdaptiveSampler(dataset, AdaptiveSamplerConfig(batch_size=2, tau_train=1e-3))
    q_values = torch.tensor([0.0, 1e-3, 1e-2, 1e-1])
    sampler.update(q_values)
    assert sampler.weights.shape == q_values.shape
    loader = sampler.dataloader()
    batch = next(iter(loader))
    assert len(batch) <= 2
