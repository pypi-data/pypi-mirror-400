# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Strict SCM inference semantics and model wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, NamedTuple

import torch
import torch.nn as nn
from torch import Tensor

__all__ = [
    "InferenceConfig",
    "InferenceResult",
    "strict_inference",
    "strict_inference_jax",
    "SCMInferenceWrapper",
]


@dataclass
class InferenceConfig:
    """Configuration for SCM inference.

    Attributes
    ----------
    tau_infer:
        Fixed inference threshold ``τ_infer``. Any denominator with
        ``|Q| < τ_infer`` produces the absorptive ``⊥`` output.
    tau_train:
        Optional training threshold ``τ_train`` for gap-region detection.
        When provided, ``strict_inference`` reports a ``gap_mask`` for
        denominators satisfying ``τ_infer ≤ |Q| < τ_train``.
    """

    tau_infer: float = 1e-6
    tau_train: float | None = None


class InferenceResult(NamedTuple):
    """Decoded inference outputs and masks.

    The decoded tensor uses ``NaN`` to represent ``⊥`` payloads; the
    accompanying ``bottom_mask`` explicitly flags every bottom entry so
    downstream consumers do not need to rely on floating-point sentinel
    values. ``gap_mask`` is only populated when ``tau_train`` exceeds
    ``tau_infer``.
    """

    decoded: Any
    bottom_mask: Any
    gap_mask: Any


def strict_inference_jax(
    numerator: Any, denominator: Any, *, config: InferenceConfig | None = None
) -> InferenceResult:
    """Strict inference for JAX projective tuples."""

    import jax.numpy as jnp

    cfg = config or InferenceConfig()
    denom_abs = jnp.abs(denominator)
    numer_nan = jnp.isnan(numerator)
    denom_nan = jnp.isnan(denominator)

    while numer_nan.ndim > denom_nan.ndim:
        numer_nan = jnp.any(numer_nan, axis=-1)

    bottom_mask = numer_nan | denom_nan | (denom_abs < cfg.tau_infer)

    denom_b = denominator
    bottom_b = bottom_mask
    while denom_b.ndim < numerator.ndim:
        denom_b = jnp.expand_dims(denom_b, axis=-1)
        bottom_b = jnp.expand_dims(bottom_b, axis=-1)

    safe_denominator = jnp.where(bottom_b, jnp.ones_like(denom_b), denom_b)
    output = numerator / safe_denominator
    output = jnp.where(bottom_b, jnp.full_like(output, jnp.nan), output)

    gap_mask = jnp.zeros_like(bottom_mask, dtype=bool)
    if cfg.tau_train is not None and cfg.tau_train > cfg.tau_infer:
        gap_mask = (denom_abs >= cfg.tau_infer) & (denom_abs < cfg.tau_train)

    return InferenceResult(output, bottom_mask, gap_mask)


def strict_inference(
    numerator: Any, denominator: Any, *, config: InferenceConfig | None = None
) -> InferenceResult:
    """Apply strict SCM semantics to a projective tuple.

    Dispatches to the appropriate backend. Torch tensors retain previous
    behaviour; JAX arrays reuse the same semantics with native vectorised
    operations. The decoded output uses ``NaN`` to represent ``⊥`` when the
    denominator violates ``τ_infer`` or either input already carries a
    ``NaN`` payload. The returned ``bottom_mask`` mirrors the same support
    explicitly for consumers that prefer mask-based propagation.
    """

    if isinstance(numerator, Tensor) or isinstance(denominator, Tensor):
        cfg = config or InferenceConfig()
        denom_abs = torch.abs(denominator)
        numer_nan = torch.isnan(numerator)
        denom_nan = torch.isnan(denominator)

        while numer_nan.dim() > denom_nan.dim():
            numer_nan = numer_nan.any(dim=-1)

        bottom_mask = numer_nan | denom_nan | (denom_abs < cfg.tau_infer)

        denom_b = denominator
        bottom_b = bottom_mask
        while denom_b.dim() < numerator.dim():
            denom_b = denom_b.unsqueeze(-1)
            bottom_b = bottom_b.unsqueeze(-1)

        safe_denominator = torch.where(bottom_b, torch.ones_like(denom_b), denom_b)
        output = numerator / safe_denominator
        output = torch.where(bottom_b, torch.full_like(output, float("nan")), output)

        gap_mask = torch.zeros_like(bottom_mask, dtype=torch.bool)
        if cfg.tau_train is not None and cfg.tau_train > cfg.tau_infer:
            gap_mask = (denom_abs >= cfg.tau_infer) & (denom_abs < cfg.tau_train)

        return InferenceResult(output, bottom_mask, gap_mask)

    try:  # pragma: no cover - optional dependency
        import jax

        if isinstance(numerator, jax.Array) or isinstance(denominator, jax.Array):
            return strict_inference_jax(numerator, denominator, config=config)
    except Exception:
        pass

    raise TypeError("strict_inference expects torch.Tensor or jax.Array inputs")


class SCMInferenceWrapper(nn.Module):  # type: ignore[misc]
    """Wrap a model that outputs projective tuples ``(P, Q)``.

    * In training mode (``model.train(True)``), the wrapper forwards the
      raw tuple unmodified for loss computation.
    * In evaluation mode (``model.eval()``), strict SCM semantics are
      applied via :func:`strict_inference`, returning decoded outputs and
      masks.
    """

    def __init__(self, model: nn.Module, *, config: InferenceConfig | None = None) -> None:
        super().__init__()
        self.model = model
        cfg = config or InferenceConfig()
        # Store scriptable attributes (TorchScript cannot ingest arbitrary dataclasses).
        self.tau_infer: float = float(cfg.tau_infer)
        self.tau_train: float = float(cfg.tau_train) if cfg.tau_train is not None else 0.0
        self.use_gap: bool = cfg.tau_train is not None and cfg.tau_train > cfg.tau_infer

    def forward(self, x: Tensor, y: Tensor | None = None) -> Any:
        """Forward inputs through the wrapped model and apply strict SCM decoding in eval mode.

        The wrapper supports two calling conventions in eager mode:

        1) ``wrapper(inputs)`` or ``wrapper(inputs, aux)`` forwards to the wrapped model.
        2) ``wrapper((inputs, denom_for_mask))`` forwards ``inputs`` to the wrapped model but
           computes bottom/gap masks from the provided denominator tensor. This mirrors the
           "single check at output" contract where a head denominator can be surfaced
           separately for safety gating.
        """

        denom_for_mask: Tensor | None = None

        if torch.jit.is_scripting():
            outputs = self.model(x)
        else:
            if y is None and isinstance(x, (tuple, list)) and len(x) == 2:
                model_input, denom_for_mask = x
                outputs = self.model(model_input)
            else:
                outputs = self.model(x) if y is None else self.model(x, y)

        if self.training:
            return outputs

        numerator = outputs[0]
        denominator = outputs[1]

        denom_for_mask = denominator if denom_for_mask is None else denom_for_mask
        denom_abs = torch.abs(denom_for_mask)

        numer_nan = torch.isnan(numerator)
        while numer_nan.dim() > denom_for_mask.dim():
            numer_nan = numer_nan.any(dim=-1)

        denom_nan = torch.isnan(denom_for_mask)
        bottom_mask = numer_nan | denom_nan | (denom_abs < self.tau_infer)

        # Always avoid explicit divide-by-zero in the decoded payload, even when the
        # safety mask denominator is overridden.
        denom_abs_model = torch.abs(denominator)
        denom_nan_model = torch.isnan(denominator)
        denom_zero_model = denom_nan_model | (denom_abs_model < self.tau_infer)

        denominator_b = denominator
        denom_zero_b = denom_zero_model
        bottom_b = bottom_mask
        while denominator_b.dim() < numerator.dim():
            denominator_b = denominator_b.unsqueeze(-1)
            denom_zero_b = denom_zero_b.unsqueeze(-1)
            bottom_b = bottom_b.unsqueeze(-1)

        safe_denominator = torch.where(
            denom_zero_b | bottom_b, torch.ones_like(denominator_b), denominator_b
        )

        decoded = numerator / safe_denominator
        decoded = torch.where(bottom_b, torch.full_like(decoded, float("nan")), decoded)

        gap_mask = torch.zeros_like(bottom_mask, dtype=torch.bool)
        if self.use_gap:
            gap_mask = (denom_abs >= self.tau_infer) & (denom_abs < self.tau_train)

        if torch.jit.is_scripting():
            return decoded, bottom_mask, gap_mask

        return InferenceResult(decoded, bottom_mask, gap_mask)
