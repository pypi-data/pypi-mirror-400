# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""SCM training loop with projective lifting and gap mitigation."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

import torch
from torch import Tensor, nn
from torch.amp import GradScaler, autocast

from .gap import perturbed_threshold
from .targets import lift_targets

__all__ = ["TrainingConfig", "SCMTrainer"]

Metrics = dict[str, float | Tensor]
Batch = tuple[Tensor, Tensor]


@dataclass
class TrainingConfig:
    """Configuration container for :class:`SCMTrainer`."""

    learning_rate: float = 1e-3
    max_epochs: int = 1
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = False
    amp_dtype: torch.dtype = torch.float16
    tau_train_min: float = 1e-4
    tau_train_max: float = 1e-4
    coverage_threshold: float = 0.95
    coverage_patience: int = 3
    log_hook: Optional[Callable[[Metrics], None]] = None
    device: Optional[torch.device] = None


class SCMTrainer:
    """Trainer implementing the v0.4 loop with optional projective lifting."""

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        loss_fn: Callable[[Tensor, tuple[Tensor, Tensor]], Tensor],
        train_loader: Iterable[Batch],
        *,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        config: TrainingConfig | None = None,
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.train_loader = train_loader
        self.scheduler = scheduler
        self.config = config or TrainingConfig()
        self.device = self.config.device or torch.device("cpu")
        self.model.to(self.device)
        scaler_device = "cuda" if self.device.type == "cuda" else "cpu"
        self.scaler = GradScaler(
            scaler_device, enabled=(self.config.mixed_precision and scaler_device == "cuda")
        )
        self._coverage_bad_epochs = 0
        self.last_thresholds: list[float] = []
        self._loss_accepts_kwargs = False
        self._loss_accepts_tau = False
        self._loss_accepts_inputs = False
        self._loss_accepts_targets = False
        self._introspect_loss_fn()

    def _introspect_loss_fn(self) -> None:
        try:
            sig = inspect.signature(self.loss_fn)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            self._loss_accepts_kwargs = True
            self._loss_accepts_tau = True
            self._loss_accepts_inputs = True
            self._loss_accepts_targets = True
            return

        params = sig.parameters
        self._loss_accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
        )
        self._loss_accepts_tau = self._loss_accepts_kwargs or ("tau" in params)
        self._loss_accepts_inputs = self._loss_accepts_kwargs or ("inputs" in params)
        self._loss_accepts_targets = self._loss_accepts_kwargs or ("targets" in params)

    def _maybe_log(self, metrics: Metrics) -> None:
        if self.config.log_hook:
            self.config.log_hook(metrics)

    def _compute_coverage(self, outputs: Tensor | tuple[Tensor, Tensor]) -> float:
        # Treat NaN as ⊥ for coverage estimation on decoded SCM tensors. For projective
        # tuples, use the denominator threshold of the current batch to estimate how
        # often the head is in the singular region.
        bottom_mask: Tensor | None = None

        if isinstance(outputs, Tensor):
            bottom_mask = torch.isnan(outputs)
        elif isinstance(outputs, (tuple, list)) and len(outputs) >= 2:
            denom = outputs[1]
            if isinstance(denom, Tensor):
                tau = (
                    self.last_thresholds[-1] if self.last_thresholds else self.config.tau_train_min
                )
                bottom_mask = torch.isnan(denom) | (torch.abs(denom) < float(tau))

        if bottom_mask is None:
            return 1.0

        # Reduce elementwise bottom to per-sample bottom for vector outputs.
        if bottom_mask.dim() > 1:
            bottom_mask = bottom_mask.any(dim=-1)

        covered = 1.0 - bottom_mask.float().mean().item()
        return float(covered)

    def train_step(self, batch: Batch) -> Metrics:
        inputs, targets = batch
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        y_n, y_d = lift_targets(targets)

        tau = perturbed_threshold(self.config.tau_train_min, self.config.tau_train_max)
        self.last_thresholds.append(tau)

        amp_dtype = self.config.amp_dtype
        if self.device.type != "cuda" and amp_dtype == torch.float16:
            amp_dtype = torch.bfloat16
        with autocast(
            device_type=self.device.type, enabled=self.config.mixed_precision, dtype=amp_dtype
        ):
            outputs = self.model(inputs)
            kwargs: dict[str, object] = {}
            if self._loss_accepts_tau:
                kwargs["tau"] = tau
            if self._loss_accepts_inputs:
                kwargs["inputs"] = inputs
            if self._loss_accepts_targets:
                kwargs["targets"] = targets
            loss = self.loss_fn(outputs, (y_n, y_d), **kwargs)

        loss = loss / self.config.gradient_accumulation_steps
        if loss.requires_grad:
            self.scaler.scale(loss).backward()

        return {"loss": float(loss.detach().item()), "coverage": self._compute_coverage(outputs)}

    def _step_optimizer(self) -> None:
        self.scaler.step(self.optimizer)
        self.scaler.update()
        self.optimizer.zero_grad(set_to_none=True)
        if self.scheduler:
            self.scheduler.step()

    def fit(self) -> list[Metrics]:
        logs: list[Metrics] = []
        steps_since_update = 0

        for _ in range(self.config.max_epochs):
            for batch in self.train_loader:
                metrics = self.train_step(batch)
                steps_since_update += 1
                if steps_since_update >= self.config.gradient_accumulation_steps:
                    self._step_optimizer()
                    steps_since_update = 0

                logs.append(metrics)
                self._maybe_log(logs[-1])

            if self._early_stop(logs):
                break

        return logs

    def _early_stop(self, logs: list[Metrics]) -> bool:
        if not logs:
            return False
        coverage = logs[-1].get("coverage")
        if coverage is None:
            return False
        if coverage < self.config.coverage_threshold:
            self._coverage_bad_epochs += 1
        else:
            self._coverage_bad_epochs = 0
        return self._coverage_bad_epochs >= self.config.coverage_patience

    def save_checkpoint(self, path: str) -> None:
        torch.save(
            {
                "model": self.model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "scaler": self.scaler.state_dict(),
            },
            path,
        )

    def load_checkpoint(self, path: str) -> None:
        state = torch.load(path, map_location=self.device)
        self.model.load_state_dict(state["model"])
        self.optimizer.load_state_dict(state["optimizer"])
        if "scaler" in state:
            self.scaler.load_state_dict(state["scaler"])
