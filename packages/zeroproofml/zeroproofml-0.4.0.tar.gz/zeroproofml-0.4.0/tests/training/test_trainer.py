import os

import pytest

torch = pytest.importorskip("torch")
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from zeroproof.training import SCMTrainer, TrainingConfig


class SimpleModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Linear(1, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # pragma: no cover - thin wrapper
        return self.net(x)


def projective_mse(
    pred: torch.Tensor, target_tuple: tuple[torch.Tensor, torch.Tensor]
) -> torch.Tensor:
    numer, denom = target_tuple
    decoded = numer / torch.clamp_min(denom, 1e-6)
    return torch.mean((pred - decoded) ** 2)


def build_loader() -> DataLoader:
    x = torch.linspace(-1, 1, 8).unsqueeze(-1)
    y = 2 * x
    dataset = TensorDataset(x, y)
    return DataLoader(dataset, batch_size=4)


def test_trainer_runs_single_epoch_and_logs_thresholds(tmp_path):
    model = SimpleModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    config = TrainingConfig(
        max_epochs=2, tau_train_min=1e-4, tau_train_max=5e-4, coverage_threshold=0.0
    )
    trainer = SCMTrainer(model, optimizer, projective_mse, build_loader(), config=config)

    logs = trainer.fit()

    assert logs, "trainer should produce logs"
    assert trainer.last_thresholds, "threshold perturbations should be recorded"
    assert all(config.tau_train_min <= t <= config.tau_train_max for t in trainer.last_thresholds)


def test_checkpoint_roundtrip(tmp_path):
    model = SimpleModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    config = TrainingConfig(max_epochs=1, coverage_threshold=0.0)
    trainer = SCMTrainer(model, optimizer, projective_mse, build_loader(), config=config)
    trainer.fit()

    ckpt_path = os.path.join(tmp_path, "ckpt.pt")
    trainer.save_checkpoint(ckpt_path)

    reloaded_model = SimpleModel()
    reloaded_opt = torch.optim.SGD(reloaded_model.parameters(), lr=0.1)
    reloaded_trainer = SCMTrainer(
        reloaded_model, reloaded_opt, projective_mse, build_loader(), config=config
    )
    reloaded_trainer.load_checkpoint(ckpt_path)

    for p_original, p_loaded in zip(model.parameters(), reloaded_model.parameters()):
        assert torch.allclose(p_original, p_loaded)


def test_trainer_supports_projective_tuple_outputs(tmp_path):
    class TupleModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Linear(1, 2)

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            y = self.net(x)
            P = y
            Q = torch.ones_like(y)
            return P, Q

    def tuple_loss(
        outputs: tuple[torch.Tensor, torch.Tensor],
        target_tuple: tuple[torch.Tensor, torch.Tensor],
        *,
        tau: float | None = None,
    ) -> torch.Tensor:
        P, Q = outputs
        numer, denom = target_tuple
        decoded_target = numer / torch.clamp_min(denom, 1e-6)
        tau = 1e-4 if tau is None else float(tau)
        decoded_pred = P / torch.clamp_min(Q.abs(), tau)
        return torch.mean((decoded_pred - decoded_target) ** 2)

    model = TupleModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    config = TrainingConfig(max_epochs=1, tau_train_min=1e-4, tau_train_max=1e-4, coverage_threshold=0.0)
    trainer = SCMTrainer(model, optimizer, tuple_loss, build_loader(), config=config)
    logs = trainer.fit()
    assert logs


def test_trainer_passes_inputs_and_targets_to_loss_fn():
    class TupleModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Linear(1, 2)

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            y = self.net(x)
            P = y
            Q = torch.ones_like(y)
            return P, Q

    def loss_with_context(
        outputs: tuple[torch.Tensor, torch.Tensor],
        target_tuple: tuple[torch.Tensor, torch.Tensor],
        *,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        tau: float,
    ) -> torch.Tensor:
        assert inputs.shape == targets.shape
        assert inputs.dim() == 2
        assert isinstance(tau, float)
        P, Q = outputs
        decoded_pred = P / torch.clamp_min(Q.abs(), tau)
        numer, denom = target_tuple
        decoded_target = numer / torch.clamp_min(denom, 1e-6)
        return torch.mean((decoded_pred - decoded_target) ** 2)

    model = TupleModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    config = TrainingConfig(max_epochs=1, tau_train_min=1e-4, tau_train_max=1e-4, coverage_threshold=0.0)
    trainer = SCMTrainer(model, optimizer, loss_with_context, build_loader(), config=config)
    logs = trainer.fit()
    assert logs
