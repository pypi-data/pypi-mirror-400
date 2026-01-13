# Copyright (c) 2025 ZeroProof Team
# SPDX-License-Identifier: MIT

"""Arithmetic primitives for Signed Common Meadows.

This module exposes totalised arithmetic operations with proper
propagation of the absorptive bottom element. The helpers mirror the
semantics described in ``concept.tex`` and are thin wrappers around the
:class:`~zeroproof.scm.value.SCMValue` container.
"""

from __future__ import annotations

import cmath
import math
from typing import Any, Callable

from .value import SCMValue, _coerce, scm_bottom

Numeric = float | complex


def _get_backend(name: str) -> Any:
    """Resolve a vectorized backend by name."""

    if name == "numpy":
        import numpy as np

        return np
    if name == "torch":
        import torch

        return torch
    if name == "jax":
        import jax.numpy as jnp

        return jnp
    raise ValueError(f"Unsupported backend: {name!r}")


def _mask_like(x: Any, backend: Any) -> Any:
    return backend.zeros_like(x, dtype=getattr(backend, "bool", bool))


def _to_backend_array(value: Any, template: Any, backend: Any) -> Any:
    if hasattr(backend, "asarray"):
        return backend.asarray(value)
    if hasattr(backend, "as_tensor"):
        dtype = getattr(template, "dtype", None)
        return backend.as_tensor(value, dtype=dtype)
    return value


def _vectorized_binary_op(
    values_x: Any,
    mask_x: Any,
    values_y: Any,
    mask_y: Any,
    backend: Any,
    op: Callable[[Any, Any], Any],
) -> tuple[Any, Any]:
    mask_x = mask_x if mask_x is not None else _mask_like(values_x, backend)
    mask_y = mask_y if mask_y is not None else _mask_like(values_y, backend)

    bottom_mask = backend.logical_or(mask_x, mask_y)
    result = op(values_x, values_y)
    return backend.where(bottom_mask, backend.zeros_like(result), result), bottom_mask


def _vectorized_div(
    values_x: Any, mask_x: Any, values_y: Any, mask_y: Any, backend: Any
) -> tuple[Any, Any]:
    mask_x = mask_x if mask_x is not None else _mask_like(values_x, backend)
    mask_y = mask_y if mask_y is not None else _mask_like(values_y, backend)

    zero_mask = values_y == 0
    bottom_mask = backend.logical_or(backend.logical_or(mask_x, mask_y), zero_mask)
    safe_denominator = backend.where(bottom_mask, backend.ones_like(values_y), values_y)
    result = backend.divide(values_x, safe_denominator)
    return backend.where(bottom_mask, backend.zeros_like(result), result), bottom_mask


def _vectorized_inv(values: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    zero_mask = values == 0
    bottom_mask = backend.logical_or(mask, zero_mask)
    safe_values = backend.where(bottom_mask, backend.ones_like(values), values)
    result = backend.reciprocal(safe_values)
    return backend.where(bottom_mask, backend.zeros_like(result), result), bottom_mask


def _vectorized_neg(values: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    result = backend.negative(values)
    return backend.where(mask, backend.zeros_like(result), result), mask


def _vectorized_pow(values: Any, exponent: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    exp_value = _to_backend_array(exponent, values, backend)

    neg_exp_mask = backend.less(exp_value, 0)
    zero_and_negative = backend.logical_and(values == 0, neg_exp_mask)
    bottom_mask = backend.logical_or(mask, zero_and_negative)
    pow_fn = getattr(backend, "power", None)
    if pow_fn is None:
        pow_fn = getattr(backend, "pow", None)
    if pow_fn is None:
        result = values**exp_value
    else:
        result = pow_fn(values, exp_value)
    return backend.where(bottom_mask, backend.zeros_like(result), result), bottom_mask


def _vectorized_log(values: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    is_complex = getattr(backend, "iscomplexobj", None)
    complex_input = False if is_complex is None else bool(is_complex(values))

    zero_or_negative = values == 0
    if not complex_input:
        zero_or_negative = backend.logical_or(zero_or_negative, backend.less(values, 0))

    bottom_mask = backend.logical_or(mask, zero_or_negative)
    log_fn = getattr(backend, "log", None)
    safe_values = backend.where(bottom_mask, backend.ones_like(values), values)
    result = log_fn(safe_values) if log_fn is not None else backend.log(safe_values)
    return backend.where(bottom_mask, backend.zeros_like(result), result), bottom_mask


def _vectorized_exp(values: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    result = backend.exp(values)
    return backend.where(mask, backend.zeros_like(result), result), mask


def _vectorized_sqrt(values: Any, mask: Any, backend: Any) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    is_complex = getattr(backend, "iscomplexobj", None)
    complex_input = False if is_complex is None else bool(is_complex(values))

    domain_violation = (values == 0) if complex_input else backend.less(values, 0)
    bottom_mask = backend.logical_or(mask, domain_violation if not complex_input else mask)

    sqrt_fn = getattr(backend, "sqrt", None)

    if complex_input:
        safe_values = backend.where(mask, backend.ones_like(values), values)
        raw = sqrt_fn(safe_values) if sqrt_fn is not None else backend.sqrt(safe_values)
        return backend.where(mask, backend.zeros_like(raw), raw), mask

    safe_values = backend.where(domain_violation, backend.ones_like(values), values)
    raw = sqrt_fn(safe_values) if sqrt_fn is not None else backend.sqrt(safe_values)
    return backend.where(bottom_mask, backend.zeros_like(raw), raw), bottom_mask


def _vectorized_trig(values: Any, mask: Any, backend: Any, fn_name: str) -> tuple[Any, Any]:
    mask = mask if mask is not None else _mask_like(values, backend)
    trig_fn = getattr(backend, fn_name)
    result = trig_fn(values)
    return backend.where(mask, backend.zeros_like(result), result), mask


def _binary_op(
    x: SCMValue | float | int | complex,
    y: SCMValue | float | int | complex,
    op: Callable[[Numeric, Numeric], Numeric],
) -> SCMValue:
    """Apply a binary operation with ⊥ absorption."""

    x_val = _coerce(x)
    y_val = _coerce(y)
    if x_val.is_bottom or y_val.is_bottom:
        return scm_bottom()
    return SCMValue(op(x_val.payload, y_val.payload))


def scm_add(x: SCMValue | float | int | complex, y: SCMValue | float | int | complex) -> SCMValue:
    return _binary_op(x, y, lambda a, b: a + b)


def scm_sub(x: SCMValue | float | int | complex, y: SCMValue | float | int | complex) -> SCMValue:
    return _binary_op(x, y, lambda a, b: a - b)


def scm_mul(x: SCMValue | float | int | complex, y: SCMValue | float | int | complex) -> SCMValue:
    return _binary_op(x, y, lambda a, b: a * b)


def scm_div(x: SCMValue | float | int | complex, y: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    y_val = _coerce(y)
    if x_val.is_bottom or y_val.is_bottom:
        return scm_bottom()
    if y_val.payload == 0:
        return scm_bottom()
    return SCMValue(x_val.payload / y_val.payload)


def scm_inv(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom or x_val.payload == 0:
        return scm_bottom()
    return SCMValue(1 / x_val.payload)


def scm_neg(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    return SCMValue(-x_val.payload)


def scm_pow(x: SCMValue | float | int | complex, exponent: float) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    if x_val.payload == 0 and exponent < 0:
        return scm_bottom()
    return SCMValue(x_val.payload**exponent)


def scm_log(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()

    payload = x_val.payload
    if isinstance(payload, complex):
        if payload == 0:
            return scm_bottom()
        return SCMValue(cmath.log(payload))

    real_payload = float(payload)
    if real_payload <= 0:
        return scm_bottom()
    return SCMValue(math.log(real_payload))


def scm_exp(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    payload = x_val.payload
    if isinstance(payload, complex):
        return SCMValue(cmath.exp(payload))
    return SCMValue(math.exp(payload))


def scm_sqrt(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    payload = x_val.payload
    if isinstance(payload, complex):
        if payload == 0:
            return SCMValue(0.0)
        return SCMValue(cmath.sqrt(payload))
    real_payload = float(payload)
    if real_payload < 0:
        return scm_bottom()
    return SCMValue(math.sqrt(real_payload))


def scm_sin(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    payload = x_val.payload
    if isinstance(payload, complex):
        return SCMValue(cmath.sin(payload))
    return SCMValue(math.sin(payload))


def scm_cos(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    payload = x_val.payload
    if isinstance(payload, complex):
        return SCMValue(cmath.cos(payload))
    return SCMValue(math.cos(payload))


def scm_tan(x: SCMValue | float | int | complex) -> SCMValue:
    x_val = _coerce(x)
    if x_val.is_bottom:
        return scm_bottom()
    payload = x_val.payload
    if isinstance(payload, complex):
        return SCMValue(cmath.tan(payload))
    return SCMValue(math.tan(payload))


# ---------------------------------------------------------------------------
# Vectorized entry points
# ---------------------------------------------------------------------------


def _binary_factory(backend_name: str, op_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, y: Any, mask_x: Any = None, mask_y: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        op = getattr(backend, op_name)
        return _vectorized_binary_op(x, mask_x, y, mask_y, backend, op)

    fn.__name__ = f"scm_{op_name}_{backend_name}"
    fn.__doc__ = f"Vectorized {op_name} with ⊥ absorption for {backend_name}."
    return fn


def _div_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, y: Any, mask_x: Any = None, mask_y: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_div(x, mask_x, y, mask_y, backend)

    fn.__name__ = f"scm_div_{backend_name}"
    fn.__doc__ = f"Vectorized division with ⊥ absorption for {backend_name}."
    return fn


def _inv_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_inv(x, mask, backend)

    fn.__name__ = f"scm_inv_{backend_name}"
    fn.__doc__ = f"Vectorized reciprocal with ⊥ absorption for {backend_name}."
    return fn


def _neg_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_neg(x, mask, backend)

    fn.__name__ = f"scm_neg_{backend_name}"
    fn.__doc__ = f"Vectorized negation with ⊥ absorption for {backend_name}."
    return fn


def _pow_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, exponent: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_pow(x, exponent, mask, backend)

    fn.__name__ = f"scm_pow_{backend_name}"
    fn.__doc__ = f"Vectorized power with ⊥ absorption for {backend_name}."
    return fn


def _log_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_log(x, mask, backend)

    fn.__name__ = f"scm_log_{backend_name}"
    fn.__doc__ = f"Vectorized log with domain checks for {backend_name}."
    return fn


def _exp_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_exp(x, mask, backend)

    fn.__name__ = f"scm_exp_{backend_name}"
    fn.__doc__ = f"Vectorized exp with ⊥ absorption for {backend_name}."
    return fn


def _sqrt_factory(backend_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_sqrt(x, mask, backend)

    fn.__name__ = f"scm_sqrt_{backend_name}"
    fn.__doc__ = f"Vectorized sqrt with domain checks for {backend_name}."
    return fn


def _trig_factory(backend_name: str, fn_name: str) -> Callable[..., tuple[Any, Any]]:
    def fn(x: Any, mask: Any = None) -> tuple[Any, Any]:
        backend = _get_backend(backend_name)
        return _vectorized_trig(x, mask, backend, fn_name)

    fn.__name__ = f"scm_{fn_name}_{backend_name}"
    fn.__doc__ = f"Vectorized {fn_name} with ⊥ absorption for {backend_name}."
    return fn


scm_add_numpy = _binary_factory("numpy", "add")
scm_sub_numpy = _binary_factory("numpy", "subtract")
scm_mul_numpy = _binary_factory("numpy", "multiply")
scm_div_numpy = _div_factory("numpy")
scm_inv_numpy = _inv_factory("numpy")
scm_neg_numpy = _neg_factory("numpy")
scm_pow_numpy = _pow_factory("numpy")
scm_log_numpy = _log_factory("numpy")
scm_exp_numpy = _exp_factory("numpy")
scm_sqrt_numpy = _sqrt_factory("numpy")
scm_sin_numpy = _trig_factory("numpy", "sin")
scm_cos_numpy = _trig_factory("numpy", "cos")
scm_tan_numpy = _trig_factory("numpy", "tan")

scm_add_torch = _binary_factory("torch", "add")
scm_sub_torch = _binary_factory("torch", "subtract")
scm_mul_torch = _binary_factory("torch", "multiply")
scm_div_torch = _div_factory("torch")
scm_inv_torch = _inv_factory("torch")
scm_neg_torch = _neg_factory("torch")
scm_pow_torch = _pow_factory("torch")
scm_log_torch = _log_factory("torch")
scm_exp_torch = _exp_factory("torch")
scm_sqrt_torch = _sqrt_factory("torch")
scm_sin_torch = _trig_factory("torch", "sin")
scm_cos_torch = _trig_factory("torch", "cos")
scm_tan_torch = _trig_factory("torch", "tan")

scm_add_jax = _binary_factory("jax", "add")
scm_sub_jax = _binary_factory("jax", "subtract")
scm_mul_jax = _binary_factory("jax", "multiply")
scm_div_jax = _div_factory("jax")
scm_inv_jax = _inv_factory("jax")
scm_neg_jax = _neg_factory("jax")
scm_pow_jax = _pow_factory("jax")
scm_log_jax = _log_factory("jax")
scm_exp_jax = _exp_factory("jax")
scm_sqrt_jax = _sqrt_factory("jax")
scm_sin_jax = _trig_factory("jax", "sin")
scm_cos_jax = _trig_factory("jax", "cos")
scm_tan_jax = _trig_factory("jax", "tan")
