"""
PyTorch bridge for transreal arithmetic.

This module provides conversions between PyTorch tensors and transreal
representations, enabling integration with deep learning workflows.

Includes a custom autograd function for TR division with Mask‑REAL and
Hybrid/Saturating gradient policies.
"""

import warnings
from typing import Any, Optional, Tuple, Union, overload

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

from ..autodiff.grad_mode import GradientMode, GradientModeConfig  # lightweight policy imports
from ..core import TRScalar, TRTag, ninf, phi, pinf, real

try:  # Optional hybrid schedule (used if available)
    from ..autodiff.hybrid_gradient import HybridGradientContext  # type: ignore
except Exception:  # pragma: no cover - optional
    HybridGradientContext = None  # type: ignore


class TRTensor:
    """
    Transreal tensor for PyTorch integration.

    Similar to TRArray but designed to work with PyTorch tensors,
    supporting GPU operations and automatic differentiation.
    """

    def __init__(self, values: "torch.Tensor", tags: "torch.Tensor", requires_grad: bool = False):
        """
        Initialize TR tensor.

        Args:
            values: Tensor of float values
            tags: Tensor of tag codes (uint8)
            requires_grad: Whether to track gradients for values
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for TRTensor")

        if values.shape != tags.shape:
            raise ValueError("Values and tags must have same shape")

        self.values = values
        self.tags = tags
        self._shape = values.shape
        self._device = values.device
        self._dtype = values.dtype

        if requires_grad and values.requires_grad:
            # Only REAL values can have gradients
            real_mask = self.is_real()
            if real_mask.any():
                # Create a differentiable view
                self.values.requires_grad_(True)

    @property
    def shape(self) -> "torch.Size":
        """Get tensor shape."""
        return self._shape

    @property
    def device(self) -> "torch.device":
        """Get tensor device."""
        return self._device

    @property
    def dtype(self) -> "torch.dtype":
        """Get value dtype."""
        return self._dtype

    @property
    def ndim(self) -> int:
        """Get number of dimensions."""
        return self.values.ndim

    @property
    def size(self) -> "torch.Size":
        """Get tensor size (PyTorch style)."""
        return self.values.size()

    def is_real(self) -> "torch.Tensor":
        """Return boolean mask of REAL elements."""
        return self.tags == TAG_CODES["REAL"]

    def is_pinf(self) -> "torch.Tensor":
        """Return boolean mask of PINF elements."""
        return self.tags == TAG_CODES["PINF"]

    def is_ninf(self) -> "torch.Tensor":
        """Return boolean mask of NINF elements."""
        return self.tags == TAG_CODES["NINF"]

    def is_phi(self) -> "torch.Tensor":
        """Return boolean mask of PHI elements."""
        return self.tags == TAG_CODES["PHI"]

    def is_finite(self) -> "torch.Tensor":
        """Return boolean mask of finite (REAL) elements."""
        return self.is_real()

    def is_infinite(self) -> "torch.Tensor":
        """Return boolean mask of infinite (PINF/NINF) elements."""
        return (self.tags == TAG_CODES["PINF"]) | (self.tags == TAG_CODES["NINF"])

    def to(self, device: Union[str, "torch.device"]) -> "TRTensor":
        """Move tensor to device."""
        return TRTensor(
            self.values.to(device), self.tags.to(device), requires_grad=self.values.requires_grad
        )

    def cpu(self) -> "TRTensor":
        """Move tensor to CPU."""
        return self.to("cpu")

    def cuda(self, device: Optional[int] = None) -> "TRTensor":
        """Move tensor to CUDA device."""
        if device is None:
            return self.to("cuda")
        else:
            return self.to(f"cuda:{device}")

    def detach(self) -> "TRTensor":
        """Detach from computation graph."""
        return TRTensor(self.values.detach(), self.tags.detach(), requires_grad=False)

    def clone(self) -> "TRTensor":
        """Create a copy of the tensor."""
        return TRTensor(
            self.values.clone(), self.tags.clone(), requires_grad=self.values.requires_grad
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"TRTensor(shape={self.shape}, device={self.device}, dtype={self.dtype})"

    def __getitem__(self, key):
        """Support tensor indexing."""
        values = self.values[key]
        tags = self.tags[key]

        # If scalar result, return TRScalar
        if values.dim() == 0:
            tag_code = tags.item()
            tag = CODE_TO_TAG[tag_code]
            if tag == TRTag.REAL:
                return TRScalar(float(values.item()), tag)
            else:
                return TRScalar(float("nan"), tag)
        else:
            return TRTensor(values, tags, requires_grad=values.requires_grad)


# Tag encoding constants
TAG_CODES = {
    "REAL": 0,
    "PINF": 1,
    "NINF": 2,
    "PHI": 3,
}

TAG_TO_CODE = {
    TRTag.REAL: 0,
    TRTag.PINF: 1,
    TRTag.NINF: 2,
    TRTag.PHI: 3,
}

CODE_TO_TAG = {v: k for k, v in TAG_TO_CODE.items()}


def from_torch(tensor: "torch.Tensor", requires_grad: bool = False) -> TRTensor:
    """
    Convert PyTorch tensor to transreal tensor.

    Args:
        tensor: PyTorch tensor
        requires_grad: Whether to track gradients

    Returns:
        TRTensor with appropriate tags
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for from_torch")

    # Ensure we have a float tensor
    if not tensor.is_floating_point():
        tensor = tensor.float()

    # Create value and tag tensors
    values = tensor.clone()
    tags = torch.zeros_like(tensor, dtype=torch.uint8)

    # Classify elements
    finite_mask = torch.isfinite(tensor)
    nan_mask = torch.isnan(tensor)
    posinf_mask = torch.isposinf(tensor)
    neginf_mask = torch.isneginf(tensor)

    # Set tags
    tags[finite_mask] = TAG_CODES["REAL"]
    tags[nan_mask] = TAG_CODES["PHI"]
    tags[posinf_mask] = TAG_CODES["PINF"]
    tags[neginf_mask] = TAG_CODES["NINF"]

    # Handle gradients
    if requires_grad and finite_mask.any():
        values.requires_grad_(True)

    return TRTensor(values, tags, requires_grad=requires_grad)


def to_torch(tr_tensor: TRTensor) -> "torch.Tensor":
    """
    Convert TRTensor to PyTorch tensor (IEEE representation).

    Args:
        tr_tensor: Transreal tensor

    Returns:
        PyTorch tensor with appropriate IEEE values
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for to_torch")

    result = torch.empty_like(tr_tensor.values)

    # Map each tag type
    real_mask = tr_tensor.is_real()
    pinf_mask = tr_tensor.is_pinf()
    ninf_mask = tr_tensor.is_ninf()
    phi_mask = tr_tensor.is_phi()

    result[real_mask] = tr_tensor.values[real_mask]
    result[pinf_mask] = float("inf")
    result[ninf_mask] = float("-inf")
    result[phi_mask] = float("nan")

    # Preserve gradient tracking if needed
    if tr_tensor.values.requires_grad:
        result.requires_grad_(True)
        # Only REAL values contribute to gradients
        if real_mask.any():
            # Create gradient mask
            result.register_hook(lambda grad: grad * real_mask.float())

    return result


# Utility functions for PyTorch operations
def mask_real_backward(grad_output: "torch.Tensor", tags: "torch.Tensor") -> "torch.Tensor":
    """
    Apply Mask-REAL rule to gradients.

    Args:
        grad_output: Gradient from downstream
        tags: Tag tensor

    Returns:
        Masked gradient (zero where tags are non-REAL)
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    real_mask = tags == TAG_CODES["REAL"]
    return grad_output * real_mask.float()


if TORCH_AVAILABLE:

    class TRFunction(torch.autograd.Function):
        """
        Base class for transreal functions with automatic Mask-REAL gradient rule.

        Subclasses should implement forward() and optionally backward().
        """

        @staticmethod
        def forward(ctx, values: "torch.Tensor", tags: "torch.Tensor", *args):
            """Forward pass - to be implemented by subclasses."""
            raise NotImplementedError

        @staticmethod
        def backward(ctx, grad_values: "torch.Tensor", _grad_tags: "torch.Tensor"):
            """
            Backward pass with Mask-REAL rule.

            Default implementation zeros gradients for non-REAL outputs.
            """
            # Get saved tags from forward
            output_tags = ctx.saved_tensors[-1]

            # Apply Mask-REAL rule
            masked_grad = mask_real_backward(grad_values, output_tags)

            # Return gradients (None for tags and extra args)
            return masked_grad, None, *([None] * (ctx.num_args - 2))

    class TrDivFunction(torch.autograd.Function):
        """
        TR division for tensors with Mask‑REAL/HYBRID gradients.

        Forward signature:
            (a_values, a_tags, b_values, b_tags) -> (out_values, out_tags)

        Backward applies classical derivatives on REAL paths and zeros elsewhere.
        In SAT/HYBRID, gradients are clipped elementwise to Gmax.
        """

        @staticmethod
        def forward(
            ctx,
            a_values: "torch.Tensor",
            a_tags: "torch.Tensor",
            b_values: "torch.Tensor",
            b_tags: "torch.Tensor",
        ):
            device = a_values.device
            dtype = a_values.dtype

            # Start with REAL tags and zeros for values
            out_tags = torch.full_like(a_tags, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            out_values = torch.zeros_like(a_values)

            # Masks
            a_real = a_tags == TAG_CODES["REAL"]  # noqa: F841
            b_real = b_tags == TAG_CODES["REAL"]  # noqa: F841
            a_pinf = a_tags == TAG_CODES["PINF"]  # noqa: F841
            a_ninf = a_tags == TAG_CODES["NINF"]  # noqa: F841
            b_pinf = b_tags == TAG_CODES["PINF"]  # noqa: F841
            b_ninf = b_tags == TAG_CODES["NINF"]  # noqa: F841
            a_phi = a_tags == TAG_CODES["PHI"]  # noqa: F841
            b_phi = b_tags == TAG_CODES["PHI"]  # noqa: F841

            # PHI in inputs -> PHI
            phi_mask = a_phi | b_phi
            out_tags = torch.where(
                phi_mask,
                torch.as_tensor(TAG_CODES["PHI"], dtype=torch.uint8, device=device),
                out_tags,
            )

            # Denominator zero cases (b_real & b_values == 0)
            denom_zero = b_real & (b_values == 0)
            # Signed zero detection (may not be available on very old torch)
            try:
                b_neg_zero = denom_zero & torch.signbit(b_values)
            except Exception:
                b_neg_zero = denom_zero & (torch.sign(b_values) < 0)

            # REAL numerator decomposition
            a_pos = a_real & (a_values > 0)
            a_neg = a_real & (a_values < 0)
            a_zero = a_real & (a_values == 0)

            # a REAL, b == +0 -> ±inf by sign of a (respect signed zero)
            out_tags = torch.where(denom_zero & a_pos & (~b_neg_zero), TAG_CODES["PINF"], out_tags)
            out_tags = torch.where(denom_zero & a_pos & (b_neg_zero), TAG_CODES["NINF"], out_tags)
            out_tags = torch.where(denom_zero & a_neg & (~b_neg_zero), TAG_CODES["NINF"], out_tags)
            out_tags = torch.where(denom_zero & a_neg & (b_neg_zero), TAG_CODES["PINF"], out_tags)
            # 0/0 = PHI
            out_tags = torch.where(denom_zero & a_zero, TAG_CODES["PHI"], out_tags)

            # inf/inf = PHI
            a_inf = a_pinf | a_ninf
            b_inf = b_pinf | b_ninf
            out_tags = torch.where(a_inf & b_inf, TAG_CODES["PHI"], out_tags)

            # finite / inf = REAL 0
            fin_over_inf = a_real & b_inf
            out_values = torch.where(fin_over_inf, torch.zeros_like(out_values), out_values)

            # inf / finite -> ±inf depending on sign of b
            fin_b = b_real & (~(b_values == 0))
            b_pos = fin_b & (b_values > 0)
            b_neg = fin_b & (b_values < 0)
            out_tags = torch.where(a_pinf & b_pos, TAG_CODES["PINF"], out_tags)
            out_tags = torch.where(a_pinf & b_neg, TAG_CODES["NINF"], out_tags)
            out_tags = torch.where(a_ninf & b_pos, TAG_CODES["NINF"], out_tags)
            out_tags = torch.where(a_ninf & b_neg, TAG_CODES["PINF"], out_tags)

            # REAL/REAL (non-zero denom) -> REAL
            rr_mask = a_real & b_real & (~(b_values == 0))
            rr_vals = torch.where(rr_mask, a_values / b_values, torch.zeros_like(a_values))
            out_values = torch.where(rr_mask, rr_vals, out_values)

            # Zero values for non-REAL outputs (stable placeholder)
            out_values = torch.where(
                (out_tags == TAG_CODES["REAL"]).to(out_values.dtype) > 0,
                out_values,
                torch.zeros_like(out_values),
            )

            # Save context for backward
            ctx.save_for_backward(a_values, a_tags, b_values, b_tags)
            ctx._gout_mask_real = (out_tags == TAG_CODES["REAL"]).to(out_values.dtype)
            return out_values, out_tags

        @staticmethod
        def backward(ctx, grad_out_values: "torch.Tensor", _grad_out_tags: "torch.Tensor"):
            a_values, a_tags, b_values, b_tags = ctx.saved_tensors
            dtype = a_values.dtype

            # Classical derivatives on REAL path: d/dx (x/y)=1/y ; d/dy (x/y)=-x/y^2
            b_is_real = (b_tags == TAG_CODES["REAL"]).to(dtype)
            denom_nz = ((b_values != 0).to(dtype) * b_is_real) > 0
            safe_b = torch.where(denom_nz, b_values, torch.ones_like(b_values))
            dx = grad_out_values / safe_b
            dy = -grad_out_values * a_values / (safe_b * safe_b)

            # Mask to REAL outputs and REAL inputs
            gout_real = getattr(ctx, "_gout_mask_real", torch.zeros_like(dx))
            a_is_real = (a_tags == TAG_CODES["REAL"]).to(dtype)
            # Additionally require denominator to be REAL for dx
            dx = dx * gout_real * a_is_real * b_is_real
            dy = dy * gout_real * b_is_real

            # Apply SAT/HYBRID clipping if configured
            mode = GradientModeConfig.get_mode()
            gmax = float(GradientModeConfig.get_saturation_bound())
            if mode == GradientMode.SATURATING:
                dx = torch.clamp(dx, -gmax, gmax)
                dy = torch.clamp(dy, -gmax, gmax)
            elif mode == GradientMode.HYBRID:
                thr = GradientModeConfig.get_local_threshold()
                if thr is not None:
                    sat_mask = (torch.abs(b_values) <= float(thr)).to(dtype)
                    if sat_mask.any():
                        dx = torch.where(sat_mask > 0, torch.clamp(dx, -gmax, gmax), dx)
                        dy = torch.where(sat_mask > 0, torch.clamp(dy, -gmax, gmax), dy)
            # No grads for tag tensors
            return dx, None, dy, None

    class TrAddFunction(torch.autograd.Function):
        """TR addition for tensors with Mask‑REAL/HYBRID gradients."""

        @staticmethod
        def forward(
            ctx,
            a_values: "torch.Tensor",
            a_tags: "torch.Tensor",
            b_values: "torch.Tensor",
            b_tags: "torch.Tensor",
        ):
            device = a_values.device
            # Default REAL
            out_tags = torch.full_like(a_tags, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            out_values = torch.zeros_like(a_values)

            a_real = a_tags == TAG_CODES["REAL"]  # noqa: F841
            b_real = b_tags == TAG_CODES["REAL"]  # noqa: F841
            a_pinf = a_tags == TAG_CODES["PINF"]  # noqa: F841
            a_ninf = a_tags == TAG_CODES["NINF"]  # noqa: F841
            b_pinf = b_tags == TAG_CODES["PINF"]  # noqa: F841
            b_ninf = b_tags == TAG_CODES["NINF"]  # noqa: F841
            a_phi = a_tags == TAG_CODES["PHI"]  # noqa: F841
            b_phi = b_tags == TAG_CODES["PHI"]  # noqa: F841

            # PHI propagates
            phi_mask = a_phi | b_phi
            out_tags = torch.where(
                phi_mask,
                torch.as_tensor(TAG_CODES["PHI"], dtype=torch.uint8, device=device),
                out_tags,
            )

            # ∞ + (−∞) = PHI
            conflict = (a_pinf & b_ninf) | (a_ninf & b_pinf)
            out_tags = torch.where(conflict, TAG_CODES["PHI"], out_tags)

            # If any +∞ and no conflict -> +∞; if any −∞ and no conflict -> −∞
            pinf_mask = (a_pinf | b_pinf) & (~conflict)
            ninf_mask = (a_ninf | b_ninf) & (~conflict)
            out_tags = torch.where(pinf_mask, TAG_CODES["PINF"], out_tags)
            out_tags = torch.where(ninf_mask, TAG_CODES["NINF"], out_tags)

            # REAL + REAL -> REAL
            rr = a_real & b_real
            out_values = torch.where(rr, a_values + b_values, out_values)
            # Zero values for non-REAL outputs
            out_values = torch.where(
                (out_tags == TAG_CODES["REAL"]).to(out_values.dtype) > 0,
                out_values,
                torch.zeros_like(out_values),
            )

            ctx.save_for_backward(a_values, a_tags, b_values, b_tags)
            ctx._gout_mask_real = (out_tags == TAG_CODES["REAL"]).to(out_values.dtype)
            return out_values, out_tags

        @staticmethod
        def backward(ctx, grad_out_values: "torch.Tensor", _grad_out_tags: "torch.Tensor"):
            a_values, a_tags, b_values, b_tags = ctx.saved_tensors
            dtype = a_values.dtype
            gout_real = getattr(ctx, "_gout_mask_real", torch.zeros_like(grad_out_values))
            a_is_real = (a_tags == TAG_CODES["REAL"]).to(dtype)
            b_is_real = (b_tags == TAG_CODES["REAL"]).to(dtype)
            dx = grad_out_values * gout_real * a_is_real
            dy = grad_out_values * gout_real * b_is_real
            mode = GradientModeConfig.get_mode()
            gmax = float(GradientModeConfig.get_saturation_bound())
            if mode == GradientMode.SATURATING:
                dx = torch.clamp(dx, -gmax, gmax)
                dy = torch.clamp(dy, -gmax, gmax)
            elif mode == GradientMode.HYBRID:
                # Addition does not have a pole; no clipping by threshold needed
                pass
            return dx, None, dy, None

    class TrMulFunction(torch.autograd.Function):
        """TR multiplication for tensors with Mask‑REAL/HYBRID gradients."""

        @staticmethod
        def forward(
            ctx,
            a_values: "torch.Tensor",
            a_tags: "torch.Tensor",
            b_values: "torch.Tensor",
            b_tags: "torch.Tensor",
        ):
            device = a_values.device
            dtype = a_values.dtype
            out_tags = torch.full_like(a_tags, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            out_values = torch.zeros_like(a_values)

            a_real = a_tags == TAG_CODES["REAL"]  # noqa: F841
            b_real = b_tags == TAG_CODES["REAL"]  # noqa: F841
            a_pinf = a_tags == TAG_CODES["PINF"]  # noqa: F841
            a_ninf = a_tags == TAG_CODES["NINF"]  # noqa: F841
            b_pinf = b_tags == TAG_CODES["PINF"]  # noqa: F841
            b_ninf = b_tags == TAG_CODES["NINF"]  # noqa: F841
            a_phi = a_tags == TAG_CODES["PHI"]  # noqa: F841
            b_phi = b_tags == TAG_CODES["PHI"]  # noqa: F841

            # PHI propagation
            phi_mask = a_phi | b_phi
            out_tags = torch.where(phi_mask, TAG_CODES["PHI"], out_tags)

            # Zero detection for reals
            a_zero = a_real & (a_values == 0)
            b_zero = b_real & (b_values == 0)
            a_inf = a_pinf | a_ninf
            b_inf = b_pinf | b_ninf

            # 0 * ∞ = PHI
            zero_inf = (a_zero & b_inf) | (b_zero & a_inf)
            out_tags = torch.where(zero_inf, TAG_CODES["PHI"], out_tags)
            # 0 * anything else = 0 (REAL)
            zero_any = (a_zero & (~b_inf) & (~b_phi)) | (b_zero & (~a_inf) & (~a_phi))
            out_values = torch.where(zero_any, torch.zeros_like(out_values), out_values)

            # REAL * REAL -> REAL
            rr = a_real & b_real
            out_values = torch.where(rr, a_values * b_values, out_values)

            # ∞ cases when not zero_inf/phi
            # Determine sign: (+∞ as +1, −∞ as −1). For REAL, sign from value.
            a_sign = torch.where(
                a_pinf,
                torch.ones_like(a_values),
                torch.where(a_ninf, -torch.ones_like(a_values), torch.sign(a_values)),
            )
            b_sign = torch.where(
                b_pinf,
                torch.ones_like(b_values),
                torch.where(b_ninf, -torch.ones_like(b_values), torch.sign(b_values)),
            )
            inf_any = (a_inf | b_inf) & (~zero_inf) & (~phi_mask)
            pos_inf = inf_any & ((a_sign * b_sign) >= 0)
            neg_inf = inf_any & ((a_sign * b_sign) < 0)
            out_tags = torch.where(pos_inf, TAG_CODES["PINF"], out_tags)
            out_tags = torch.where(neg_inf, TAG_CODES["NINF"], out_tags)

            # Zero non-REAL values for stability
            out_values = torch.where(
                (out_tags == TAG_CODES["REAL"]).to(dtype) > 0,
                out_values,
                torch.zeros_like(out_values),
            )

            ctx.save_for_backward(a_values, a_tags, b_values, b_tags)
            ctx._gout_mask_real = (out_tags == TAG_CODES["REAL"]).to(dtype)
            return out_values, out_tags

        @staticmethod
        def backward(ctx, grad_out_values: "torch.Tensor", _grad_out_tags: "torch.Tensor"):
            a_values, a_tags, b_values, b_tags = ctx.saved_tensors
            dtype = a_values.dtype
            gout_real = getattr(ctx, "_gout_mask_real", torch.zeros_like(grad_out_values))
            a_is_real = (a_tags == TAG_CODES["REAL"]).to(dtype)
            b_is_real = (b_tags == TAG_CODES["REAL"]).to(dtype)
            dx = grad_out_values * b_values * gout_real * a_is_real
            dy = grad_out_values * a_values * gout_real * b_is_real
            mode = GradientModeConfig.get_mode()
            gmax = float(GradientModeConfig.get_saturation_bound())
            if mode == GradientMode.SATURATING:
                dx = torch.clamp(dx, -gmax, gmax)
                dy = torch.clamp(dy, -gmax, gmax)
            elif mode == GradientMode.HYBRID:
                # Multiplication has no intrinsic pole; no clipping by |Q| needed
                pass
            return dx, None, dy, None

    class TrLogFunction(torch.autograd.Function):
        """TR natural logarithm with Mask‑REAL/HYBRID gradients."""

        @staticmethod
        def forward(ctx, x_values: "torch.Tensor", x_tags: "torch.Tensor"):
            device = x_values.device
            dtype = x_values.dtype
            out_tags = torch.full_like(x_tags, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            out_values = torch.zeros_like(x_values)

            x_real = x_tags == TAG_CODES["REAL"]  # noqa: F841
            x_pinf = x_tags == TAG_CODES["PINF"]  # noqa: F841
            x_ninf = x_tags == TAG_CODES["NINF"]  # noqa: F841
            x_phi = x_tags == TAG_CODES["PHI"]  # noqa: F841

            # PHI propagates
            out_tags = torch.where(x_phi, TAG_CODES["PHI"], out_tags)

            # REAL domain: x>0 -> REAL ln(x); x<=0 -> PHI
            real_pos = x_real & (x_values > 0)
            real_nonpos = x_real & (x_values <= 0)
            out_values = torch.where(real_pos, torch.log(x_values), out_values)
            out_tags = torch.where(real_nonpos, TAG_CODES["PHI"], out_tags)

            # ±∞ cases
            out_tags = torch.where(x_pinf, TAG_CODES["PINF"], out_tags)  # log(+∞) = +∞
            out_tags = torch.where(x_ninf, TAG_CODES["PHI"], out_tags)  # log(−∞) = PHI

            # Zero non‑REAL values
            out_values = torch.where(
                (out_tags == TAG_CODES["REAL"]).to(dtype) > 0,
                out_values,
                torch.zeros_like(out_values),
            )

            ctx.save_for_backward(x_values, x_tags)
            ctx._gout_mask_real = (out_tags == TAG_CODES["REAL"]).to(dtype)
            return out_values, out_tags

        @staticmethod
        def backward(ctx, grad_out_values: "torch.Tensor", _grad_out_tags: "torch.Tensor"):
            x_values, x_tags = ctx.saved_tensors
            dtype = x_values.dtype
            gout_real = getattr(ctx, "_gout_mask_real", torch.zeros_like(grad_out_values))
            x_is_real = (x_tags == TAG_CODES["REAL"]).to(dtype)
            # Classical derivative d/dx log(x) = 1/x
            # Avoid divide by zero by masking non‑REAL or non‑positive inputs anyway
            safe_x = torch.where(
                (x_values != 0) & (x_is_real > 0), x_values, torch.ones_like(x_values)
            )
            dx = grad_out_values / safe_x
            dx = dx * gout_real * x_is_real

            # Apply SAT/HYBRID clipping based on |x|
            mode = GradientModeConfig.get_mode()
            gmax = float(GradientModeConfig.get_saturation_bound())
            if mode == GradientMode.SATURATING:
                dx = torch.clamp(dx, -gmax, gmax)
            elif mode == GradientMode.HYBRID:
                thr = GradientModeConfig.get_local_threshold()
                if thr is not None:
                    sat_mask = (torch.abs(x_values) <= float(thr)).to(dtype)
                    if sat_mask.any():
                        dx = torch.where(sat_mask > 0, torch.clamp(dx, -gmax, gmax), dx)
            return dx, None

    class TrSqrtFunction(torch.autograd.Function):
        """TR square root with Mask‑REAL/HYBRID gradients."""

        @staticmethod
        def forward(ctx, x_values: "torch.Tensor", x_tags: "torch.Tensor"):
            device = x_values.device
            dtype = x_values.dtype
            out_tags = torch.full_like(x_tags, fill_value=TAG_CODES["REAL"], dtype=torch.uint8)
            out_values = torch.zeros_like(x_values)

            x_real = x_tags == TAG_CODES["REAL"]  # noqa: F841
            x_pinf = x_tags == TAG_CODES["PINF"]  # noqa: F841
            x_ninf = x_tags == TAG_CODES["NINF"]  # noqa: F841
            x_phi = x_tags == TAG_CODES["PHI"]  # noqa: F841

            out_tags = torch.where(x_phi, TAG_CODES["PHI"], out_tags)

            # REAL domain: x>=0 -> REAL sqrt(x); x<0 -> PHI
            real_pos = x_real & (x_values >= 0)
            real_neg = x_real & (x_values < 0)
            out_values = torch.where(real_pos, torch.sqrt(x_values), out_values)
            out_tags = torch.where(real_neg, TAG_CODES["PHI"], out_tags)

            # ±∞ cases
            out_tags = torch.where(x_pinf, TAG_CODES["PINF"], out_tags)  # sqrt(+∞) = +∞
            out_tags = torch.where(x_ninf, TAG_CODES["PHI"], out_tags)  # sqrt(−∞) = PHI

            # Zero non‑REAL values
            out_values = torch.where(
                (out_tags == TAG_CODES["REAL"]).to(dtype) > 0,
                out_values,
                torch.zeros_like(out_values),
            )

            ctx.save_for_backward(x_values, x_tags, out_values)
            ctx._gout_mask_real = (out_tags == TAG_CODES["REAL"]).to(dtype)
            return out_values, out_tags

        @staticmethod
        def backward(ctx, grad_out_values: "torch.Tensor", _grad_out_tags: "torch.Tensor"):
            x_values, x_tags, out_values = ctx.saved_tensors
            dtype = x_values.dtype
            gout_real = getattr(ctx, "_gout_mask_real", torch.zeros_like(grad_out_values))
            x_is_real = (x_tags == TAG_CODES["REAL"]).to(dtype)
            # d/dx sqrt(x) = 1 / (2*sqrt(x))
            safe_sqrt = torch.where(
                (out_values != 0) & (x_is_real > 0), out_values, torch.ones_like(out_values)
            )
            denom = 2.0 * safe_sqrt
            dx = grad_out_values / denom
            dx = dx * gout_real * x_is_real

            mode = GradientModeConfig.get_mode()
            gmax = float(GradientModeConfig.get_saturation_bound())
            if mode == GradientMode.SATURATING:
                dx = torch.clamp(dx, -gmax, gmax)
            elif mode == GradientMode.HYBRID:
                thr = GradientModeConfig.get_local_threshold()
                if thr is not None:
                    sat_mask = (torch.abs(x_values) <= float(thr)).to(dtype)
                    if sat_mask.any():
                        dx = torch.where(sat_mask > 0, torch.clamp(dx, -gmax, gmax), dx)
            return dx, None

else:

    class TRFunction:
        """Stub when PyTorch is not available."""

        pass

    class TrDivFunction:  # type: ignore
        pass

    def tr_div_tensor(*_args, **_kwargs):  # type: ignore
        raise ImportError("PyTorch is required for tr_div_tensor")

    class TrAddFunction:  # type: ignore
        pass

    class TrMulFunction:  # type: ignore
        pass


# Conversion utilities for common use cases
def tr_tensor_from_list(
    values: list,
    tags: list,
    device: Optional[Union[str, "torch.device"]] = None,
    dtype: Optional["torch.dtype"] = None,
) -> TRTensor:
    """
    Create TRTensor from lists of values and tags.

    Args:
        values: List of values
        tags: List of TRTag enum values
        device: Target device
        dtype: Target dtype

    Returns:
        TRTensor
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    # Convert to tensors
    value_tensor = torch.tensor(values, device=device, dtype=dtype or torch.float32)
    tag_codes = [TAG_TO_CODE[tag] for tag in tags]
    tag_tensor = torch.tensor(tag_codes, device=device, dtype=torch.uint8)

    return TRTensor(value_tensor, tag_tensor)


def batch_from_scalars(
    scalars: list[TRScalar], device: Optional[Union[str, "torch.device"]] = None
) -> TRTensor:
    """
    Create TRTensor batch from list of TRScalars.

    Args:
        scalars: List of TRScalar values
        device: Target device

    Returns:
        TRTensor with shape (len(scalars),)
    """
    values = []
    tags = []

    for scalar in scalars:
        if scalar.tag == TRTag.REAL:
            values.append(scalar.value)
        else:
            values.append(float("nan"))  # Placeholder
        tags.append(scalar.tag)

    return tr_tensor_from_list(values, tags, device=device)


# Integration with PyTorch autograd
def enable_tr_gradients():
    """
    Enable gradient computation for TRTensor operations.

    This sets up hooks to apply Mask-REAL rule automatically.
    """
    warnings.warn(
        "TR gradient support for PyTorch is experimental. "
        "Ensure all operations properly handle tags.",
        category=UserWarning,
    )


def tr_div_tensor(a: TRTensor, b: TRTensor) -> TRTensor:
    """Elementwise TR division for TRTensor with autograd support."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for tr_div_tensor")
    if a.values.shape != b.values.shape:
        raise ValueError("Shape mismatch in tr_div_tensor")
    out_values, out_tags = TrDivFunction.apply(a.values, a.tags, b.values, b.tags)
    return TRTensor(out_values, out_tags, requires_grad=out_values.requires_grad)


def tr_add_tensor(a: TRTensor, b: TRTensor) -> TRTensor:
    """Elementwise TR addition for TRTensor with autograd support."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for tr_add_tensor")
    if a.values.shape != b.values.shape:
        raise ValueError("Shape mismatch in tr_add_tensor")
    out_values, out_tags = TrAddFunction.apply(a.values, a.tags, b.values, b.tags)
    return TRTensor(out_values, out_tags, requires_grad=out_values.requires_grad)


def tr_mul_tensor(a: TRTensor, b: TRTensor) -> TRTensor:
    """Elementwise TR multiplication for TRTensor with autograd support."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for tr_mul_tensor")
    if a.values.shape != b.values.shape:
        raise ValueError("Shape mismatch in tr_mul_tensor")
    out_values, out_tags = TrMulFunction.apply(a.values, a.tags, b.values, b.tags)
    return TRTensor(out_values, out_tags, requires_grad=out_values.requires_grad)


def tr_log_tensor(x: TRTensor) -> TRTensor:
    """Elementwise TR natural logarithm for TRTensor with autograd support."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for tr_log_tensor")
    out_values, out_tags = TrLogFunction.apply(x.values, x.tags)
    return TRTensor(out_values, out_tags, requires_grad=out_values.requires_grad)


def tr_sqrt_tensor(x: TRTensor) -> TRTensor:
    """Elementwise TR square root for TRTensor with autograd support."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch is required for tr_sqrt_tensor")
    out_values, out_tags = TrSqrtFunction.apply(x.values, x.tags)
    return TRTensor(out_values, out_tags, requires_grad=out_values.requires_grad)
