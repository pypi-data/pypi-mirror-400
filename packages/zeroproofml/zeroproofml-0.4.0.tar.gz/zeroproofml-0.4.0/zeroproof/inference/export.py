# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Export helpers for SCM inference graphs."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

__all__ = ["script_module", "export_onnx_model"]


def script_module(model: nn.Module) -> torch.jit.ScriptModule:
    """Script a model for TorchScript deployment.

    The wrapper simply delegates to :func:`torch.jit.script` after forcing
    evaluation mode so that :class:`~zeroproof.inference.mode.SCMInferenceWrapper`
    instances emit strict SCM outputs.
    """

    model.eval()
    return torch.jit.script(model)


def export_onnx_model(
    model: nn.Module,
    example_inputs: tuple[Any, ...],
    output_path: str,
    *,
    opset: int = 17,
    dynamic_axes: dict[str, dict[int, str]] | None = None,
) -> None:
    """Export a model to ONNX in inference mode.

    Parameters
    ----------
    model:
        The model to export. Should already encode strict SCM behavior
        (e.g., via :class:`~zeroproof.inference.mode.SCMInferenceWrapper`).
    example_inputs:
        Example inputs used for tracing shapes.
    output_path:
        Destination filepath for the ONNX graph.
    opset:
        ONNX opset version. Defaults to 17 to match current PyTorch
        defaults while remaining compatible with most runtimes.
    dynamic_axes:
        Optional dynamic axes mapping passed to :func:`torch.onnx.export`.
    """

    model.eval()
    torch.onnx.export(
        model,
        example_inputs,
        output_path,
        opset_version=opset,
        training=torch.onnx.TrainingMode.EVAL,
        dynamic_axes=dynamic_axes,
    )
