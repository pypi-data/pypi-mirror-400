import pytest

torch = pytest.importorskip("torch")

from zeroproof.layers import SCMRationalLayer


def test_end_to_end_training_on_synthetic_rational():
    torch.manual_seed(0)
    layer = SCMRationalLayer(1, 1)
    optimizer = torch.optim.Adam(layer.parameters(), lr=0.1)

    x = torch.linspace(-0.5, 0.5, 32).unsqueeze(-1)
    target = (2 * x + 1.0) / (x + 1.5)

    losses: list[float] = []
    for _ in range(120):
        optimizer.zero_grad()
        output, bottom_mask = layer(x)
        assert not bottom_mask.any()
        loss = torch.mean((output - target) ** 2)
        losses.append(loss.item())
        loss.backward()
        optimizer.step()

    assert losses[0] > 0
    assert losses[-1] < 0.1 * losses[0]
    assert losses[-1] < 1e-4
