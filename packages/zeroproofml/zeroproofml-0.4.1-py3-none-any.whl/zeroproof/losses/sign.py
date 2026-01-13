# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Sign consistency loss."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from torch import Tensor


def sign_consistency_loss(
    P: Tensor,
    Q: Tensor,
    Y_n: Tensor,
    Y_d: Tensor,
    gamma: float = 1e-9,
    mask_singular: Tensor | None = None,
) -> Tensor:
    """Encourage predicted tuples to align with target orientation."""

    import torch

    if torch.is_complex(P) or torch.is_complex(Q) or torch.is_complex(Y_n) or torch.is_complex(Y_d):
        dot = (P * torch.conj(Y_n)) + (Q * torch.conj(Y_d))
        norm_pred = torch.sqrt((P * torch.conj(P)).real + (Q * torch.conj(Q)).real + gamma)
        norm_target = torch.sqrt(
            (Y_n * torch.conj(Y_n)).real + (Y_d * torch.conj(Y_d)).real + gamma
        )
        cosine = dot.real / (norm_pred * norm_target)
        loss = 1 - cosine
    else:
        pred_scale = torch.maximum(P.abs(), Q.abs())
        target_scale = torch.maximum(Y_n.abs(), Y_d.abs())

        pred_scale = torch.where(pred_scale == 0, torch.ones_like(pred_scale), pred_scale)
        target_scale = torch.where(target_scale == 0, torch.ones_like(target_scale), target_scale)

        pred_norm = pred_scale * torch.sqrt(
            (P / pred_scale).pow(2) + (Q / pred_scale).pow(2) + gamma / pred_scale.pow(2)
        )
        target_norm = target_scale * torch.sqrt(
            (Y_n / target_scale).pow(2) + (Y_d / target_scale).pow(2) + gamma / target_scale.pow(2)
        )

        pred_unit_p = P / pred_norm
        pred_unit_q = Q / pred_norm
        target_unit_p = Y_n / target_norm
        target_unit_q = Y_d / target_norm

        cosine = pred_unit_p * target_unit_p + pred_unit_q * target_unit_q
        cosine = torch.clamp(cosine, -1.0, 1.0)
        loss = 1 - cosine

    if mask_singular is not None:
        loss = loss * mask_singular
    return loss.mean()
