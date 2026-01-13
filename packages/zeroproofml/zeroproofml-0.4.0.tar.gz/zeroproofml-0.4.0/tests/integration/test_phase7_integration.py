import math

import pytest

torch = pytest.importorskip("torch")

from zeroproof.inference.mode import InferenceConfig, SCMInferenceWrapper
from zeroproof.training.trainer import SCMTrainer, TrainingConfig


class _TwoRInverseKinematics(torch.nn.Module):
    """Minimal 2R IK surrogate emitting projective tuples.

    The model returns numerator proportional to task-space delta and a
    denominator equal to ``sin(theta2)``, mirroring the det(J) structure
    of a planar 2R arm where singularities occur when ``theta2 ≈ 0``.
    """

    def forward(
        self, theta2: torch.Tensor, delta: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        numerator = delta
        denominator = torch.sin(theta2)
        return numerator, denominator


class _ComplexJacobianModel(torch.nn.Module):
    """Emit complex-valued tuples to mimic 6R Jacobian entries."""

    def forward(self, inputs: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        numerator = inputs.to(torch.complex64) * (1 + 1j)
        # Use a quadratic form that vanishes at the origin to trigger ⊥.
        denominator = torch.complex(inputs[:, 0] ** 2, inputs[:, 1] ** 2)
        return numerator, denominator


class _NaNModel(torch.nn.Module):
    """Returns NaN outputs to force low coverage for early-stop checks."""

    def __init__(self) -> None:
        super().__init__()
        self.dummy = torch.nn.Parameter(torch.tensor(0.0))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return torch.full_like(inputs, float("nan"))


def _nan_safe_mse(pred: torch.Tensor, target: tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
    finite = torch.nan_to_num(pred)
    # Loss is indifferent to the projective target; we only need gradients.
    return torch.mean(finite**2)


@pytest.mark.parametrize("theta_values", [torch.tensor([-1.0, -0.1, 0.0, 0.1, 1.0])])
def test_2r_inverse_kinematics_bottom_mask(theta_values: torch.Tensor) -> None:
    model = SCMInferenceWrapper(
        _TwoRInverseKinematics(), config=InferenceConfig(tau_infer=5e-2, tau_train=1e-1)
    )
    model.eval()

    delta = torch.ones_like(theta_values)
    output, bottom_mask, gap_mask = model(theta_values, delta)

    expected_bottom = torch.isclose(torch.sin(theta_values).abs(), torch.tensor(0.0), atol=5e-2)
    assert torch.equal(bottom_mask, expected_bottom)

    finite_region = ~bottom_mask
    assert torch.allclose(
        output[finite_region], delta[finite_region] / torch.sin(theta_values[finite_region])
    )

    # Gap region should capture values between τ_infer and τ_train.
    assert torch.equal(
        gap_mask,
        (torch.abs(torch.sin(theta_values)) >= 5e-2) & (torch.abs(torch.sin(theta_values)) < 1e-1),
    )


@pytest.mark.parametrize(
    "inputs",
    [torch.tensor([[0.0, 0.0], [0.1, -0.2], [0.5, 0.5]], dtype=torch.float32)],
)
def test_6r_complex_jacobian_inference(inputs: torch.Tensor) -> None:
    wrapper = SCMInferenceWrapper(
        _ComplexJacobianModel(), config=InferenceConfig(tau_infer=1e-3, tau_train=1e-2)
    )
    wrapper.eval()

    output, bottom_mask, gap_mask = wrapper(inputs)

    # Origin should map to ⊥, non-zero entries should decode to the complex ratio.
    assert bottom_mask[0]
    assert torch.isnan(output[0].real).all()
    assert torch.all(~bottom_mask[1:])

    denom = torch.complex(inputs[1:, 0] ** 2, inputs[1:, 1] ** 2).unsqueeze(-1)
    expected = (inputs[1:].to(torch.complex64) * (1 + 1j)) / denom
    assert torch.allclose(output[1:], expected)

    # Points with small |Q| fall into the gap region when above τ_infer.
    denom_mag = torch.abs(torch.complex(inputs[:, 0] ** 2, inputs[:, 1] ** 2))
    assert torch.equal(gap_mask, (denom_mag >= 1e-3) & (denom_mag < 1e-2))


@pytest.mark.parametrize("patience", [1])
def test_coverage_convergence_triggers_early_stop(patience: int) -> None:
    model = _NaNModel()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    data = [(torch.zeros(4, 1), torch.zeros(4, 1))]
    trainer = SCMTrainer(
        model,
        optimizer,
        loss_fn=_nan_safe_mse,
        train_loader=data,
        config=TrainingConfig(max_epochs=3, coverage_threshold=0.5, coverage_patience=patience),
    )

    logs = trainer.fit()

    # Coverage remains 0 → early stop after ``patience`` epochs.
    assert len(logs) == patience * len(data)
    assert all(entry["coverage"] == 0.0 for entry in logs)
