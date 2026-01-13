"""
PyTorch TR‑Norm and TR‑LayerNorm (no epsilon).

Normalizes using only REAL entries (masking out non‑REAL), with gradients
gated to REAL outputs. No ε is introduced; divisions by zero produce
infinities/NaNs as per IEEE, which is acceptable under TR semantics.
"""

from __future__ import annotations

from typing import Optional

try:
    import torch
    from torch import nn

    TORCH_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    torch = None  # type: ignore
    nn = object  # type: ignore
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    from ..bridge.torch_bridge import TAG_CODES, TRTensor, from_torch


def _masked_sum(
    values: "torch.Tensor", mask: "torch.Tensor", dim: int, deterministic: bool = False
) -> "torch.Tensor":
    """Compute sum(values*mask) along dim; optional pairwise tree for determinism."""
    w = values * mask
    if not deterministic:
        return w.sum(dim=dim)

    # Pairwise tree reduction along given dim
    # Move dim to last, reshape to 2D [..., N], then reduce
    perm = list(range(values.dim()))
    perm[dim], perm[-1] = perm[-1], perm[dim]
    w2 = w.permute(perm)
    shape = w2.shape
    last = shape[-1]
    out = w2
    while last > 1:
        even = last // 2
        odd = last - even * 2
        left = out[..., : 2 * even]
        left = left.reshape(*shape[:-1], even, 2).sum(dim=-1)
        if odd:
            out = torch.cat([left, out[..., -1:].clone()], dim=-1)
            last = even + 1
        else:
            out = left
            last = even
    # Restore original dims and squeeze last size-1 dim
    inv = list(range(len(perm)))
    inv[perm[-1]] = len(perm) - 1
    for i in range(len(perm) - 1):
        inv[perm[i]] = i
    out = out.permute(inv).squeeze(dim)
    return out


if TORCH_AVAILABLE:

    class TorchTRLayerNorm(nn.Module):
        """
        Per-sample layer normalization over the last dimension without ε.

        - Computes mean/variance using only REAL entries (mask tags == REAL).
        - Output tags are the input tags; gradients are zeroed for non‑REAL outputs.
        - Optional affine (gamma, beta) over last dimension.
        """

        def __init__(
            self, normalized_shape: int, affine: bool = False, deterministic_reduction: bool = False
        ):
            super().__init__()
            if normalized_shape <= 0:
                raise ValueError("normalized_shape must be positive")
            self.normalized_shape = int(normalized_shape)
            self.affine = bool(affine)
            self.deterministic_reduction = bool(deterministic_reduction)
            if self.affine:
                self.gamma = nn.Parameter(torch.ones(self.normalized_shape, dtype=torch.float64))
                self.beta = nn.Parameter(torch.zeros(self.normalized_shape, dtype=torch.float64))
            else:
                self.register_parameter("gamma", None)
                self.register_parameter("beta", None)

        def forward(self, x: "torch.Tensor") -> TRTensor:  # type: ignore[override]
            X = from_torch(x, requires_grad=x.requires_grad)
            v, t = X.values, X.tags
            real = (t == TAG_CODES["REAL"]).to(v.dtype)
            # Reduce over last dim
            dim = -1
            count = real.sum(dim=dim, keepdim=True).clamp_min(1.0)
            mean = (
                _masked_sum(v, real, dim=dim, deterministic=self.deterministic_reduction).unsqueeze(
                    dim
                )
                / count
            )
            # Variance over REAL entries
            diff = (v - mean) * real
            var = (
                _masked_sum(
                    diff * diff,
                    torch.ones_like(real),
                    dim=dim,
                    deterministic=self.deterministic_reduction,
                ).unsqueeze(dim)
                / count
            )
            # Normalize
            denom = torch.sqrt(var)
            y = (v - mean) / denom
            # Optional affine
            if self.affine:
                gamma = self.gamma.to(dtype=v.dtype, device=v.device).view(
                    *([1] * (v.dim() - 1)), -1
                )
                beta = self.beta.to(dtype=v.dtype, device=v.device).view(*([1] * (v.dim() - 1)), -1)
                y = y * gamma + beta
            # Gate gradients for non‑REAL outputs
            y = y * real
            return TRTensor(y, t, requires_grad=y.requires_grad)

        def forward_values(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.forward(x).values

    class TorchTRNorm(nn.Module):
        """
        Batch-style normalization across batch dimension per feature (no ε).

        - Input shape: [batch, features]
        - Stats per feature computed over REAL entries in the batch.
        - Output tags equal input tags; grads gated to REAL outputs.
        """

        def __init__(self, num_features: int, deterministic_reduction: bool = False):
            super().__init__()
            if num_features <= 0:
                raise ValueError("num_features must be positive")
            self.num_features = int(num_features)
            self.deterministic_reduction = bool(deterministic_reduction)

        def forward(self, x: "torch.Tensor") -> TRTensor:  # type: ignore[override]
            if x.dim() != 2 or x.shape[1] != self.num_features:
                raise ValueError("TorchTRNorm expects input of shape [batch, features]")
            X = from_torch(x, requires_grad=x.requires_grad)
            v, t = X.values, X.tags  # [B, F]
            real = (t == TAG_CODES["REAL"]).to(v.dtype)
            # Reduce over batch (dim=0)
            count = real.sum(dim=0, keepdim=True).clamp_min(1.0)  # [1, F]
            mean = (
                _masked_sum(v, real, dim=0, deterministic=self.deterministic_reduction).unsqueeze(0)
                / count
            )
            diff = (v - mean) * real
            var = (
                _masked_sum(
                    diff * diff,
                    torch.ones_like(real),
                    dim=0,
                    deterministic=self.deterministic_reduction,
                ).unsqueeze(0)
                / count
            )
            denom = torch.sqrt(var)
            y = (v - mean) / denom
            # Gate gradients for non‑REAL outputs
            y = y * real
            return TRTensor(y, t, requires_grad=y.requires_grad)

        def forward_values(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.forward(x).values
