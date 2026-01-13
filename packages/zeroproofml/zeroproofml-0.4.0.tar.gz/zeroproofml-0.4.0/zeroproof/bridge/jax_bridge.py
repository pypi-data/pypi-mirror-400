"""
JAX bridge for transreal arithmetic.

This module provides conversions between JAX arrays and transreal
representations, supporting functional transformations and JIT compilation.
"""

import warnings
from functools import partial
from typing import Any, NamedTuple, Optional, Tuple, Union

try:
    import jax
    import jax.numpy as jnp
    from jax import custom_vjp, lax

    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    jax = None
    jnp = None
    custom_vjp = None
    lax = None

from ..core import TRScalar, TRTag, ninf, phi, pinf, real


class TRJaxArray(NamedTuple):
    """
    Transreal array for JAX.

    Uses NamedTuple for immutability and JAX pytree registration.
    """

    values: Any  # jax.Array for values
    tags: Any  # jax.Array for tags (uint8)

    @property
    def shape(self):
        """Get array shape."""
        return self.values.shape

    @property
    def dtype(self):
        """Get value dtype."""
        return self.values.dtype

    @property
    def ndim(self):
        """Get number of dimensions."""
        return self.values.ndim

    def is_real(self):
        """Return boolean mask of REAL elements."""
        return self.tags == TAG_CODES["REAL"]

    def is_pinf(self):
        """Return boolean mask of PINF elements."""
        return self.tags == TAG_CODES["PINF"]

    def is_ninf(self):
        """Return boolean mask of NINF elements."""
        return self.tags == TAG_CODES["NINF"]

    def is_phi(self):
        """Return boolean mask of PHI elements."""
        return self.tags == TAG_CODES["PHI"]

    def is_finite(self):
        """Return boolean mask of finite (REAL) elements."""
        return self.is_real()

    def is_infinite(self):
        """Return boolean mask of infinite (PINF/NINF) elements."""
        return (self.tags == TAG_CODES["PINF"]) | (self.tags == TAG_CODES["NINF"])


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


# Register TRJaxArray as a JAX pytree
if JAX_AVAILABLE:
    from jax.tree_util import register_pytree_node

    def _tr_flatten(tr_array):
        """Flatten TRJaxArray for pytree."""
        return (tr_array.values, tr_array.tags), None

    def _tr_unflatten(_aux_data, children):
        """Unflatten TRJaxArray from pytree."""
        values, tags = children
        return TRJaxArray(values, tags)

    register_pytree_node(TRJaxArray, _tr_flatten, _tr_unflatten)


def from_jax(array: "jax.Array") -> TRJaxArray:
    """
    Convert JAX array to transreal array.

    Args:
        array: JAX array

    Returns:
        TRJaxArray with appropriate tags
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for from_jax")

    # Create value and tag arrays
    values = array
    tags = jnp.zeros_like(array, dtype=jnp.uint8)

    # Classify elements
    finite_mask = jnp.isfinite(array)
    nan_mask = jnp.isnan(array)
    posinf_mask = jnp.isposinf(array)
    neginf_mask = jnp.isneginf(array)

    # Set tags using JAX operations
    tags = jnp.where(finite_mask, TAG_CODES["REAL"], tags)
    tags = jnp.where(nan_mask, TAG_CODES["PHI"], tags)
    tags = jnp.where(posinf_mask, TAG_CODES["PINF"], tags)
    tags = jnp.where(neginf_mask, TAG_CODES["NINF"], tags)

    return TRJaxArray(values, tags)


def to_jax(tr_array: TRJaxArray) -> "jax.Array":
    """
    Convert TRJaxArray to JAX array (IEEE representation).

    Args:
        tr_array: Transreal array

    Returns:
        JAX array with appropriate IEEE values
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required for to_jax")

    # Map each tag type to IEEE values
    real_mask = tr_array.is_real()
    pinf_mask = tr_array.is_pinf()
    ninf_mask = tr_array.is_ninf()
    phi_mask = tr_array.is_phi()

    # Use JAX operations for conversion
    result = jnp.where(real_mask, tr_array.values, 0.0)
    result = jnp.where(pinf_mask, jnp.inf, result)
    result = jnp.where(ninf_mask, -jnp.inf, result)
    result = jnp.where(phi_mask, jnp.nan, result)

    return result


# Mask-REAL gradient rule for JAX
def mask_real_grad(grad_output: "jax.Array", tags: "jax.Array") -> "jax.Array":
    """
    Apply Mask-REAL rule to gradients.

    Args:
        grad_output: Gradient from downstream
        tags: Tag array

    Returns:
        Masked gradient (zero where tags are non-REAL)
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required")

    real_mask = tags == TAG_CODES["REAL"]
    return grad_output * real_mask.astype(grad_output.dtype)


if JAX_AVAILABLE:
    # Custom gradient rules for TR operations (only when JAX is available)
    # Avoid nondiff_argnums so backward signatures stay compatible across JAX versions.
    @custom_vjp
    def tr_op_with_grad(values: "jax.Array", tags: "jax.Array", op_fn):
        """
        Generic TR operation with automatic Mask-REAL gradient.
        """
        return op_fn(values, tags)

    def tr_op_fwd(values, tags, op_fn):
        """Forward pass for TR operation."""
        output_values, output_tags = op_fn(values, tags)
        return (output_values, output_tags), (output_tags,)

    def tr_op_bwd(residuals, grads):
        """Backward pass with Mask-REAL rule."""
        (output_tags,) = residuals
        grad_values, grad_tags = grads
        masked_grad = mask_real_grad(grad_values, output_tags)
        return (masked_grad, None, None)

    # Register the custom gradient
    tr_op_with_grad.defvjp(tr_op_fwd, tr_op_bwd)
else:
    # Stubs when JAX is unavailable
    def tr_op_with_grad(*args, **kwargs):
        raise ImportError("JAX is required for tr_op_with_grad")


###############################################
# JAX-compatible TR operations with custom_vjp #
###############################################


def _tags_eq(tag, code):
    return tag == jnp.asarray(code, dtype=jnp.uint8)


if JAX_AVAILABLE:
    # ---------- Addition ----------
    @custom_vjp
    def tr_add(
        a: TRJaxArray, b: TRJaxArray, delta: Optional[float] = None, gmax: Optional[float] = None
    ) -> TRJaxArray:
        a_val, a_tag = a.values, a.tags
        b_val, b_tag = b.values, b.tags
        phi_mask = _tags_eq(a_tag, TAG_CODES["PHI"]) | _tags_eq(b_tag, TAG_CODES["PHI"])
        inf_conflict = (_tags_eq(a_tag, TAG_CODES["PINF"]) & _tags_eq(b_tag, TAG_CODES["NINF"])) | (
            _tags_eq(a_tag, TAG_CODES["NINF"]) & _tags_eq(b_tag, TAG_CODES["PINF"])
        )
        out_val = a_val + b_val
        out_tag = jnp.where(
            phi_mask | inf_conflict,
            TAG_CODES["PHI"],
            jnp.where(
                _tags_eq(a_tag, TAG_CODES["PINF"]) | _tags_eq(b_tag, TAG_CODES["PINF"]),
                TAG_CODES["PINF"],
                jnp.where(
                    _tags_eq(a_tag, TAG_CODES["NINF"]) | _tags_eq(b_tag, TAG_CODES["NINF"]),
                    TAG_CODES["NINF"],
                    TAG_CODES["REAL"],
                ),
            ),
        )
        return TRJaxArray(out_val, out_tag)

    def _tr_add_fwd(a, b, delta, gmax):
        out = tr_add(a, b, delta, gmax)
        return out, (a, b, out, delta, gmax)

    def _tr_add_bwd(residuals, g):
        (a, b, out, delta, gmax) = residuals
        grad_val, grad_tag = g.values, g.tags
        # Mask-REAL: grads only for REAL outputs and REAL inputs
        mask_out = _tags_eq(out.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_a = _tags_eq(a.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_b = _tags_eq(b.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        dx = grad_val * mask_out * mask_a
        dy = grad_val * mask_out * mask_b
        # Saturation/Hybrid clipping (treat gmax/delta as JAX scalars)
        gmax_arr = (
            jnp.asarray(gmax) if gmax is not None else jnp.asarray(jnp.inf, dtype=grad_val.dtype)
        )
        do_clip = jnp.isfinite(gmax_arr)
        dx_clip = jnp.clip(dx, -gmax_arr, gmax_arr)
        dy_clip = jnp.clip(dy, -gmax_arr, gmax_arr)
        dx = jnp.where(do_clip, dx_clip, dx)
        dy = jnp.where(do_clip, dy_clip, dy)
        zero_tag = jnp.zeros_like(a.tags)
        return TRJaxArray(dx, zero_tag), TRJaxArray(dy, zero_tag), None, None

    tr_add.defvjp(_tr_add_fwd, _tr_add_bwd)

    # ---------- Multiplication ----------
    @custom_vjp
    def tr_mul(
        a: TRJaxArray, b: TRJaxArray, delta: Optional[float] = None, gmax: Optional[float] = None
    ) -> TRJaxArray:
        a_val, a_tag = a.values, a.tags
        b_val, b_tag = b.values, b.tags
        phi_mask = _tags_eq(a_tag, TAG_CODES["PHI"]) | _tags_eq(b_tag, TAG_CODES["PHI"])
        a_zero = _tags_eq(a_tag, TAG_CODES["REAL"]) & (a_val == 0)
        b_zero = _tags_eq(b_tag, TAG_CODES["REAL"]) & (b_val == 0)
        a_inf = _tags_eq(a_tag, TAG_CODES["PINF"]) | _tags_eq(a_tag, TAG_CODES["NINF"])
        b_inf = _tags_eq(b_tag, TAG_CODES["PINF"]) | _tags_eq(b_tag, TAG_CODES["NINF"])
        zero_inf = (a_zero & b_inf) | (b_zero & a_inf)
        out_val = a_val * b_val
        # Determine sign for infinity result
        sign_a = jnp.where(
            _tags_eq(a_tag, TAG_CODES["PINF"]),
            1.0,
            jnp.where(_tags_eq(a_tag, TAG_CODES["NINF"]), -1.0, jnp.sign(a_val)),
        )
        sign_b = jnp.where(
            _tags_eq(b_tag, TAG_CODES["PINF"]),
            1.0,
            jnp.where(_tags_eq(b_tag, TAG_CODES["NINF"]), -1.0, jnp.sign(b_val)),
        )
        inf_any = (a_inf | b_inf) & (~zero_inf) & (~phi_mask)
        pos_inf = inf_any & ((sign_a * sign_b) >= 0)
        neg_inf = inf_any & ((sign_a * sign_b) < 0)
        out_tag = jnp.where(
            phi_mask | zero_inf,
            TAG_CODES["PHI"],
            jnp.where(
                jnp.isfinite(out_val),
                TAG_CODES["REAL"],
                jnp.where(pos_inf, TAG_CODES["PINF"], TAG_CODES["NINF"]),
            ),
        )
        return TRJaxArray(out_val, out_tag)

    def _tr_mul_fwd(a, b, delta, gmax):
        out = tr_mul(a, b, delta, gmax)
        return out, (a, b, out, delta, gmax)

    def _tr_mul_bwd(residuals, g):
        (a, b, out, delta, gmax) = residuals
        grad_val, _ = g.values, g.tags
        mask_out = _tags_eq(out.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_a = _tags_eq(a.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_b = _tags_eq(b.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        dx = grad_val * b.values
        dy = grad_val * a.values
        # Mask after computing raw grads
        dx = dx * mask_out * mask_a
        dy = dy * mask_out * mask_b
        # Clipping with JAX scalars (no Python branching on tracers)
        gmax_arr = (
            jnp.asarray(gmax) if gmax is not None else jnp.asarray(jnp.inf, dtype=grad_val.dtype)
        )
        delta_arr = (
            jnp.asarray(delta) if delta is not None else jnp.asarray(0.0, dtype=grad_val.dtype)
        )
        do_clip = jnp.isfinite(gmax_arr)
        sat = ((jnp.abs(a.values) <= delta_arr) | (jnp.abs(b.values) <= delta_arr)).astype(
            grad_val.dtype
        )
        dx_clip = jnp.clip(dx, -gmax_arr, gmax_arr)
        dy_clip = jnp.clip(dy, -gmax_arr, gmax_arr)
        should_clip = do_clip & (sat > 0)
        dx = jnp.where(should_clip, dx_clip, jnp.where(do_clip, dx_clip, dx))
        dy = jnp.where(should_clip, dy_clip, jnp.where(do_clip, dy_clip, dy))
        zero_tag = jnp.zeros_like(a.tags)
        return TRJaxArray(dx, zero_tag), TRJaxArray(dy, zero_tag), None, None

    tr_mul.defvjp(_tr_mul_fwd, _tr_mul_bwd)

    # ---------- Division ----------
    @custom_vjp
    def tr_div(
        a: TRJaxArray, b: TRJaxArray, delta: Optional[float] = None, gmax: Optional[float] = None
    ) -> TRJaxArray:
        a_val, a_tag = a.values, a.tags
        b_val, b_tag = b.values, b.tags
        phi_mask = _tags_eq(a_tag, TAG_CODES["PHI"]) | _tags_eq(b_tag, TAG_CODES["PHI"])
        # b == 0 (REAL)
        denom_zero = _tags_eq(b_tag, TAG_CODES["REAL"]) & (b_val == 0)
        a_pos = _tags_eq(a_tag, TAG_CODES["REAL"]) & (a_val > 0)
        a_neg = _tags_eq(a_tag, TAG_CODES["REAL"]) & (a_val < 0)
        a_zero = _tags_eq(a_tag, TAG_CODES["REAL"]) & (a_val == 0)
        out_tag = jnp.where(phi_mask, TAG_CODES["PHI"], TAG_CODES["REAL"])
        # REAL numerator with zero denom
        out_tag = jnp.where(denom_zero & a_pos, TAG_CODES["PINF"], out_tag)
        out_tag = jnp.where(denom_zero & a_neg, TAG_CODES["NINF"], out_tag)
        out_tag = jnp.where(denom_zero & a_zero, TAG_CODES["PHI"], out_tag)
        # inf/inf = PHI
        a_inf = _tags_eq(a_tag, TAG_CODES["PINF"]) | _tags_eq(a_tag, TAG_CODES["NINF"])
        b_inf = _tags_eq(b_tag, TAG_CODES["PINF"]) | _tags_eq(b_tag, TAG_CODES["NINF"])
        out_tag = jnp.where(a_inf & b_inf, TAG_CODES["PHI"], out_tag)
        # finite / inf = 0 (REAL)
        fin_over_inf = _tags_eq(a_tag, TAG_CODES["REAL"]) & b_inf
        out_val = jnp.where(
            fin_over_inf,
            0.0,
            a_val / jnp.where(_tags_eq(b_tag, TAG_CODES["REAL"]) & (b_val != 0), b_val, 1.0),
        )
        # inf / finite → sign depends on b
        fin_b = _tags_eq(b_tag, TAG_CODES["REAL"]) & (b_val != 0)
        b_pos = fin_b & (b_val > 0)
        b_neg = fin_b & (b_val < 0)
        out_tag = jnp.where(_tags_eq(a_tag, TAG_CODES["PINF"]) & b_pos, TAG_CODES["PINF"], out_tag)
        out_tag = jnp.where(_tags_eq(a_tag, TAG_CODES["PINF"]) & b_neg, TAG_CODES["NINF"], out_tag)
        out_tag = jnp.where(_tags_eq(a_tag, TAG_CODES["NINF"]) & b_pos, TAG_CODES["NINF"], out_tag)
        out_tag = jnp.where(_tags_eq(a_tag, TAG_CODES["NINF"]) & b_neg, TAG_CODES["PINF"], out_tag)
        # Zero non-REAL payloads
        out_val = jnp.where(_tags_eq(out_tag, TAG_CODES["REAL"]), out_val, 0.0)
        return TRJaxArray(out_val, out_tag)

    def _tr_div_fwd(a, b, delta, gmax):
        out = tr_div(a, b, delta, gmax)
        return out, (a, b, out, delta, gmax)

    def _tr_div_bwd(residuals, g):
        a, b, out, delta, gmax = residuals
        grad_val = g.values
        mask_out = _tags_eq(out.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_a = _tags_eq(a.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_b = _tags_eq(b.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        # Only propagate gradient where denominator is REAL and non-zero
        b_real_nz = _tags_eq(b.tags, TAG_CODES["REAL"]) & (b.values != 0)
        b_real_nz_f = b_real_nz.astype(grad_val.dtype)
        denom = jnp.where(b_real_nz, b.values, 1.0)
        dx = (grad_val / denom) * b_real_nz_f
        dy = (-grad_val * a.values / (denom * denom)) * b_real_nz_f
        dx = dx * mask_out * mask_a
        dy = dy * mask_out * mask_b
        # Clipping using JAX scalars
        gmax_arr = (
            jnp.asarray(gmax) if gmax is not None else jnp.asarray(jnp.inf, dtype=grad_val.dtype)
        )
        delta_arr = (
            jnp.asarray(delta) if delta is not None else jnp.asarray(0.0, dtype=grad_val.dtype)
        )
        do_clip = jnp.isfinite(gmax_arr)
        sat = (jnp.abs(b.values) <= delta_arr).astype(grad_val.dtype)
        dx_clip = jnp.clip(dx, -gmax_arr, gmax_arr)
        dy_clip = jnp.clip(dy, -gmax_arr, gmax_arr)
        should_clip = do_clip & (sat > 0)
        dx = jnp.where(should_clip, dx_clip, jnp.where(do_clip, dx_clip, dx))
        dy = jnp.where(should_clip, dy_clip, jnp.where(do_clip, dy_clip, dy))
        zero_tag = jnp.zeros_like(a.tags)
        return TRJaxArray(dx, zero_tag), TRJaxArray(dy, zero_tag), None, None

    tr_div.defvjp(_tr_div_fwd, _tr_div_bwd)

    # ---------- Log ----------
    @custom_vjp
    def tr_log(
        x: TRJaxArray, delta: Optional[float] = None, gmax: Optional[float] = None
    ) -> TRJaxArray:
        x_val, x_tag = x.values, x.tags
        phi_mask = _tags_eq(x_tag, TAG_CODES["PHI"]) | _tags_eq(
            x_tag, TAG_CODES["NINF"]
        )  # log(-∞)=PHI
        real_pos = _tags_eq(x_tag, TAG_CODES["REAL"]) & (x_val > 0)
        out_val = jnp.where(real_pos, jnp.log(x_val), 0.0)
        out_tag = jnp.where(phi_mask, TAG_CODES["PHI"], TAG_CODES["REAL"])
        out_tag = jnp.where(
            _tags_eq(x_tag, TAG_CODES["PINF"]), TAG_CODES["PINF"], out_tag
        )  # log(+∞)=+∞
        out_tag = jnp.where(
            _tags_eq(x_tag, TAG_CODES["REAL"]) & (x_val <= 0), TAG_CODES["PHI"], out_tag
        )
        return TRJaxArray(out_val, out_tag)

    def _tr_log_fwd(x, delta, gmax):
        out = tr_log(x, delta, gmax)
        return out, (x, out, delta, gmax)

    def _tr_log_bwd(residuals, g):
        x, out, delta, gmax = residuals
        grad_val = g.values
        mask_out = _tags_eq(out.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_x = _tags_eq(x.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        safe_x = jnp.where((_tags_eq(x.tags, TAG_CODES["REAL"]) & (x.values != 0)), x.values, 1.0)
        dx = grad_val / safe_x
        dx = dx * mask_out * mask_x
        gmax_arr = (
            jnp.asarray(gmax) if gmax is not None else jnp.asarray(jnp.inf, dtype=grad_val.dtype)
        )
        delta_arr = (
            jnp.asarray(delta) if delta is not None else jnp.asarray(0.0, dtype=grad_val.dtype)
        )
        do_clip = jnp.isfinite(gmax_arr)
        sat = (jnp.abs(x.values) <= delta_arr).astype(grad_val.dtype)
        dx_clip = jnp.clip(dx, -gmax_arr, gmax_arr)
        should_clip = do_clip & (sat > 0)
        dx = jnp.where(should_clip, dx_clip, jnp.where(do_clip, dx_clip, dx))
        zero_tag = jnp.zeros_like(x.tags)
        return TRJaxArray(dx, zero_tag), None, None

    tr_log.defvjp(_tr_log_fwd, _tr_log_bwd)

    # ---------- Sqrt ----------
    @custom_vjp
    def tr_sqrt(
        x: TRJaxArray, delta: Optional[float] = None, gmax: Optional[float] = None
    ) -> TRJaxArray:
        x_val, x_tag = x.values, x.tags
        phi_mask = _tags_eq(x_tag, TAG_CODES["PHI"]) | _tags_eq(
            x_tag, TAG_CODES["NINF"]
        )  # sqrt(-∞)=PHI
        real_pos = _tags_eq(x_tag, TAG_CODES["REAL"]) & (x_val >= 0)
        out_val = jnp.where(real_pos, jnp.sqrt(x_val), 0.0)
        out_tag = jnp.where(phi_mask, TAG_CODES["PHI"], TAG_CODES["REAL"])
        out_tag = jnp.where(
            _tags_eq(x_tag, TAG_CODES["PINF"]), TAG_CODES["PINF"], out_tag
        )  # sqrt(+∞)=+∞
        out_tag = jnp.where(
            _tags_eq(x_tag, TAG_CODES["REAL"]) & (x_val < 0), TAG_CODES["PHI"], out_tag
        )
        return TRJaxArray(out_val, out_tag)

    def _tr_sqrt_fwd(x, delta, gmax):
        out = tr_sqrt(x, delta, gmax)
        return out, (x, out, delta, gmax)

    def _tr_sqrt_bwd(residuals, g):
        x, out, delta, gmax = residuals
        grad_val = g.values
        mask_out = _tags_eq(out.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        mask_x = _tags_eq(x.tags, TAG_CODES["REAL"]).astype(grad_val.dtype)
        safe_sqrt = jnp.where(
            (_tags_eq(x.tags, TAG_CODES["REAL"]) & (out.values != 0)), out.values, 1.0
        )
        dx = grad_val / (2.0 * safe_sqrt)
        dx = dx * mask_out * mask_x
        gmax_arr = (
            jnp.asarray(gmax) if gmax is not None else jnp.asarray(jnp.inf, dtype=grad_val.dtype)
        )
        delta_arr = (
            jnp.asarray(delta) if delta is not None else jnp.asarray(0.0, dtype=grad_val.dtype)
        )
        do_clip = jnp.isfinite(gmax_arr)
        sat = (jnp.abs(x.values) <= delta_arr).astype(grad_val.dtype)
        dx_clip = jnp.clip(dx, -gmax_arr, gmax_arr)
        should_clip = do_clip & (sat > 0)
        dx = jnp.where(should_clip, dx_clip, jnp.where(do_clip, dx_clip, dx))
        zero_tag = jnp.zeros_like(x.tags)
        return TRJaxArray(dx, zero_tag), None, None

    tr_sqrt.defvjp(_tr_sqrt_fwd, _tr_sqrt_bwd)

    # ---------- Deterministic reductions (pairwise/scan) ----------
    def _move_axis_to_front(x, axis: int):
        rank = x.ndim
        axis_norm = axis if axis >= 0 else axis + rank
        perm = (axis_norm,) + tuple(i for i in range(rank) if i != axis_norm)
        return jnp.transpose(x, perm), perm

    def _invert_permutation(perm):
        inv = [0] * len(perm)
        for i, p in enumerate(perm):
            inv[p] = i
        return tuple(inv)

    def tr_sum_jax(a: TRJaxArray, axis: int = -1, drop_null: bool = False) -> TRJaxArray:
        """
        Deterministic pairwise sum over axis using lax.associative_scan.

        STRICT semantics:
        - PHI present -> PHI
        - Both +∞ and −∞ present -> PHI
        - Else if any +∞ -> +∞; else if any −∞ -> −∞; else REAL sum of REAL entries

        drop_null=True ignores PHI entries in the aggregation.
        """
        vals0, tags0 = a.values, a.tags
        vals, perm = _move_axis_to_front(vals0, axis)
        tags, _ = _move_axis_to_front(tags0, axis)

        # Map element to aggregate state
        def elem_to_state(v, t):
            is_real = (t == TAG_CODES["REAL"]).astype(jnp.bool_)
            is_pinf = (t == TAG_CODES["PINF"]).astype(jnp.bool_)
            is_ninf = (t == TAG_CODES["NINF"]).astype(jnp.bool_)
            is_phi = (t == TAG_CODES["PHI"]).astype(jnp.bool_)
            if drop_null:
                # Ignore PHI in sum/count
                s = jnp.where(is_real, v, 0.0)
                c = is_real.astype(jnp.int32)
                p = is_pinf
                n = is_ninf
                ph = jnp.array(False)
            else:
                s = jnp.where(is_real, v, 0.0)
                c = is_real.astype(jnp.int32)
                p = is_pinf
                n = is_ninf
                ph = is_phi
            return (s, c, p, n, ph)

        # Combine two states (associative)
        def combine(a_state, b_state):
            a_s, a_c, a_p, a_n, a_ph = a_state
            b_s, b_c, b_p, b_n, b_ph = b_state
            return (a_s + b_s, a_c + b_c, a_p | b_p, a_n | b_n, a_ph | b_ph)

        # Initialize states for each element along scan dimension
        # Scan over first dimension to construct pairwise tree reduction
        s0, c0, p0, n0, ph0 = jax.vmap(elem_to_state)(vals, tags)
        agg_s, agg_c, agg_p, agg_n, agg_ph = lax.associative_scan(combine, (s0, c0, p0, n0, ph0))
        # Take final aggregate at end of scan dimension
        s = agg_s[-1]
        c = agg_c[-1]
        p = agg_p[-1]
        n = agg_n[-1]
        ph = agg_ph[-1]

        # Finalize tag and value
        both_inf = p & n
        any_inf = p | n
        out_tag = jnp.where(
            ph | both_inf,
            TAG_CODES["PHI"],
            jnp.where(p, TAG_CODES["PINF"], jnp.where(n, TAG_CODES["NINF"], TAG_CODES["REAL"])),
        )
        out_val = jnp.where(out_tag == TAG_CODES["REAL"], s, 0.0)
        # Restore original axis order without the reduced dimension
        inv = _invert_permutation(perm)
        out_val = jnp.transpose(out_val, inv[1:])  # remove front axis
        out_tag = jnp.transpose(out_tag, inv[1:])
        return TRJaxArray(out_val, out_tag)

    def tr_mean_jax(a: TRJaxArray, axis: int = -1, drop_null: bool = False) -> TRJaxArray:
        """Deterministic mean over axis with STRICT/drop_null behavior."""
        vals0, tags0 = a.values, a.tags
        vals, perm = _move_axis_to_front(vals0, axis)
        tags, _ = _move_axis_to_front(tags0, axis)

        def elem_to_state(v, t):
            is_real = (t == TAG_CODES["REAL"]).astype(jnp.bool_)
            is_pinf = (t == TAG_CODES["PINF"]).astype(jnp.bool_)
            is_ninf = (t == TAG_CODES["NINF"]).astype(jnp.bool_)
            is_phi = (t == TAG_CODES["PHI"]).astype(jnp.bool_)
            s = jnp.where(is_real, v, 0.0)
            c = is_real.astype(jnp.int32)
            if drop_null:
                ph = jnp.array(False)
            else:
                ph = is_phi
            return (s, c, is_pinf, is_ninf, ph)

        def combine(a_state, b_state):
            a_s, a_c, a_p, a_n, a_ph = a_state
            b_s, b_c, b_p, b_n, b_ph = b_state
            return (a_s + b_s, a_c + b_c, a_p | b_p, a_n | b_n, a_ph | b_ph)

        s0, c0, p0, n0, ph0 = jax.vmap(elem_to_state)(vals, tags)
        agg_s, agg_c, agg_p, agg_n, agg_ph = lax.associative_scan(combine, (s0, c0, p0, n0, ph0))
        s = agg_s[-1]
        c = agg_c[-1]
        p = agg_p[-1]
        n = agg_n[-1]
        ph = agg_ph[-1]

        both_inf = p & n
        any_inf = p | n
        out_tag = jnp.where(
            ph | both_inf,
            TAG_CODES["PHI"],
            jnp.where(p, TAG_CODES["PINF"], jnp.where(n, TAG_CODES["NINF"], TAG_CODES["REAL"])),
        )
        mean_val = jnp.where(c > 0, s / jnp.maximum(c, 1), 0.0)
        out_val = jnp.where(out_tag == TAG_CODES["REAL"], mean_val, 0.0)
        inv = _invert_permutation(perm)
        out_val = jnp.transpose(out_val, inv[1:])
        out_tag = jnp.transpose(out_tag, inv[1:])
        return TRJaxArray(out_val, out_tag)


# Utility functions for JAX
def vmap_tr_scalar_fn(fn, _in_axes=0, _out_axes=0):
    """
    Vectorize a function that operates on TRScalars.

    Args:
        fn: Function taking TRScalar inputs
        in_axes: Input axes for vmap
        out_axes: Output axes for vmap

    Returns:
        Vectorized function operating on TRJaxArrays
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required")

    def wrapped_fn(tr_array):
        # This is a placeholder - full implementation would properly
        # vectorize scalar TR operations for JAX
        raise NotImplementedError("Scalar TR function vectorization not yet implemented")

    return wrapped_fn


# Integration with JAX transformations
def make_jaxpr_with_tr(fn):
    """
    Create JAX intermediate representation for TR function.

    This helps with debugging and optimization.
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required")

    return jax.make_jaxpr(fn)


# Conversion utilities
def tr_scalar_to_jax(scalar: TRScalar, shape=()) -> TRJaxArray:
    """
    Convert TRScalar to TRJaxArray.

    Args:
        scalar: TRScalar value
        shape: Desired output shape (default: scalar)

    Returns:
        TRJaxArray
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required")

    if scalar.tag == TRTag.REAL:
        value = scalar.value
    elif scalar.tag == TRTag.PINF:
        value = jnp.inf
    elif scalar.tag == TRTag.NINF:
        value = -jnp.inf
    else:  # PHI
        value = jnp.nan

    values = jnp.full(shape, value)
    tags = jnp.full(shape, TAG_TO_CODE[scalar.tag], dtype=jnp.uint8)

    return TRJaxArray(values, tags)


def batch_from_scalars_jax(scalars: list[TRScalar]) -> TRJaxArray:
    """
    Create TRJaxArray batch from list of TRScalars.

    Args:
        scalars: List of TRScalar values

    Returns:
        TRJaxArray with shape (len(scalars),)
    """
    if not JAX_AVAILABLE:
        raise ImportError("JAX is required")

    values = []
    tags = []

    for scalar in scalars:
        if scalar.tag == TRTag.REAL:
            values.append(scalar.value)
        elif scalar.tag == TRTag.PINF:
            values.append(jnp.inf)
        elif scalar.tag == TRTag.NINF:
            values.append(-jnp.inf)
        else:  # PHI
            values.append(jnp.nan)
        tags.append(TAG_TO_CODE[scalar.tag])

    return TRJaxArray(jnp.array(values), jnp.array(tags, dtype=jnp.uint8))
