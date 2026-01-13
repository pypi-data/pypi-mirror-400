"""Regression checks for throughput and memory overhead in SCM inference."""

from __future__ import annotations

import time

import pytest

torch = pytest.importorskip("torch")

from zeroproof.inference.mode import InferenceConfig, strict_inference


def _python_baseline(
    numerator: torch.Tensor, denominator: torch.Tensor, tau: float
) -> torch.Tensor:
    """Naive elementwise inference used as a performance floor."""

    flat_output = []
    for num, denom in zip(numerator.view(-1), denominator.view(-1)):
        if torch.isnan(num) or torch.isnan(denom) or abs(denom.item()) < tau:
            flat_output.append(float("nan"))
        else:
            flat_output.append((num / denom).item())
    return torch.tensor(flat_output, device=numerator.device).view_as(numerator)


def test_strict_inference_beats_python_baseline() -> None:
    cfg = InferenceConfig(tau_infer=1e-3)
    numerator = torch.randn(128, 128)
    denominator = torch.randn_like(numerator)
    denominator[0, 0] = 0.0  # ensure ⊥ is exercised

    start = time.perf_counter()
    decoded, bottom_mask, gap_mask = strict_inference(numerator, denominator, config=cfg)
    optimized_duration = time.perf_counter() - start

    start = time.perf_counter()
    baseline = _python_baseline(numerator, denominator, cfg.tau_infer)
    baseline_duration = time.perf_counter() - start

    # Vectorized path should dominate the naive Python loop.
    assert optimized_duration < baseline_duration

    assert torch.isnan(decoded[0, 0])
    assert torch.isnan(baseline[0, 0])
    assert bottom_mask.any()
    assert not gap_mask.any()


def test_projective_tuple_memory_overhead() -> None:
    numerator = torch.randn(64, 64)
    denominator = torch.randn_like(numerator)

    output, bottom_mask, gap_mask = strict_inference(numerator, denominator)

    tuple_bytes = (
        numerator.element_size() * numerator.numel()
        + denominator.element_size() * denominator.numel()
    )
    output_bytes = output.element_size() * output.numel()

    # Two float tensors double the storage relative to a decoded scalar tensor.
    assert output_bytes > 0
    ratio = tuple_bytes / output_bytes
    assert 1.95 <= ratio <= 2.05

    # Masks track ⊥ without changing the storage expectation.
    assert bottom_mask.shape == numerator.shape
    assert gap_mask.shape == numerator.shape
