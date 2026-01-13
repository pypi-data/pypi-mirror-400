"""
NumPy bridge for transreal arithmetic.

This module provides efficient conversions between NumPy arrays
and transreal representations, supporting both scalar and tensor operations.
"""

import warnings
from typing import Any, Optional, Tuple, Union, overload

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from ..core import TRScalar, TRTag, ninf, phi, pinf, real


def _pack_bits(mask: "np.ndarray") -> "np.ndarray":
    """Pack a boolean mask into a uint8 array (bit-packed).

    The length of the returned array is ceil(len(mask)/8). Bits are stored LSB-first.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")
    mask = np.asarray(mask, dtype=bool).ravel()
    n = mask.size
    out = np.zeros((n + 7) // 8, dtype=np.uint8)
    for i, bit in enumerate(mask):
        if bit:
            out[i >> 3] |= 1 << (i & 7)
    return out


def _unpack_bits(packed: "np.ndarray", length: int) -> "np.ndarray":
    """Unpack a uint8 bit-packed array into a boolean array of given length."""
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")
    packed = np.asarray(packed, dtype=np.uint8)
    out = np.zeros(length, dtype=bool)
    for i in range(length):
        out[i] = (packed[i >> 3] >> (i & 7)) & 1
    return out


class TRArray:
    """
    Transreal array representation.

    Similar to NumPy's masked arrays but using TR tags instead of masks.
    Stores values and tags in separate arrays for efficiency.
    """

    def __init__(self, values: "np.ndarray", tags: "np.ndarray"):
        """
        Initialize TR array.

        Args:
            values: Array of float values (may contain NaN/inf for non-REAL)
            tags: Array of tag codes (uint8)
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for TRArray")

        if values.shape != tags.shape:
            raise ValueError("Values and tags must have same shape")

        self.values = values
        self.tags = tags
        self._shape = values.shape
        self._dtype = values.dtype

    @property
    def shape(self) -> Tuple[int, ...]:
        """Get array shape."""
        return self._shape

    @property
    def dtype(self) -> Any:
        """Get value dtype."""
        return self._dtype

    @property
    def ndim(self) -> int:
        """Get number of dimensions."""
        return self.values.ndim

    @property
    def size(self) -> int:
        """Get total number of elements."""
        return self.values.size

    def is_real(self) -> "np.ndarray":
        """Return boolean mask of REAL elements."""
        return self.tags == tag_to_code(TRTag.REAL)

    def is_pinf(self) -> "np.ndarray":
        """Return boolean mask of PINF elements."""
        return self.tags == tag_to_code(TRTag.PINF)

    def is_ninf(self) -> "np.ndarray":
        """Return boolean mask of NINF elements."""
        return self.tags == tag_to_code(TRTag.NINF)

    def is_phi(self) -> "np.ndarray":
        """Return boolean mask of PHI elements."""
        return self.tags == tag_to_code(TRTag.PHI)

    def is_finite(self) -> "np.ndarray":
        """Return boolean mask of finite (REAL) elements."""
        return self.is_real()

    def is_infinite(self) -> "np.ndarray":
        """Return boolean mask of infinite (PINF/NINF) elements."""
        return (self.tags == tag_to_code(TRTag.PINF)) | (self.tags == tag_to_code(TRTag.NINF))

    def __repr__(self) -> str:
        """String representation."""
        return f"TRArray(shape={self.shape}, dtype={self.dtype})"

    def __str__(self) -> str:
        """Human-readable string."""
        # Create a string representation similar to NumPy
        if self.size == 0:
            return "TRArray([])"

        # For small arrays, show all elements
        if self.size <= 10:
            elements = []
            flat_vals = self.values.flat
            flat_tags = self.tags.flat
            for val, tag_code in zip(flat_vals, flat_tags):
                tag = code_to_tag(tag_code)
                if tag == TRTag.REAL:
                    elements.append(str(val))
                else:
                    elements.append(tag.name)

            if self.ndim == 1:
                return f"TRArray([{', '.join(elements)}])"
            else:
                return f"TRArray(shape={self.shape}, elements=[{', '.join(elements[:5])}...])"
        else:
            return f"TRArray(shape={self.shape}, dtype={self.dtype})"

    def to_numpy(self) -> "np.ndarray":
        """Convert to NumPy array (IEEE representation)."""
        return to_numpy_array(self)

    def __getitem__(self, key):
        """Support array indexing."""
        values = self.values[key]
        tags = self.tags[key]

        # If scalar result, return TRScalar
        if np.isscalar(values):
            tag = code_to_tag(tags)
            if tag == TRTag.REAL:
                return TRScalar(float(values), tag)
            else:
                return TRScalar(float("nan"), tag)
        else:
            return TRArray(values, tags)


# -----------------------------
# Vectorized TR operations (NumPy)
# -----------------------------


def _ensure_tr_array(x: Union[TRArray, "np.ndarray", float, int]) -> TRArray:
    if isinstance(x, TRArray):
        return x
    if NUMPY_AVAILABLE and isinstance(x, np.ndarray):
        return from_numpy(x, return_array=True)  # type: ignore[return-value]
    # Scalars
    return from_numpy(float(x), return_array=True)  # type: ignore[return-value]


def tr_add_np(
    a: Union[TRArray, "np.ndarray", float, int], b: Union[TRArray, "np.ndarray", float, int]
) -> TRArray:
    """Elementwise transreal addition over TRArray.

    REAL+REAL -> REAL (numeric sum); PHI dominates; +∞ + −∞ -> PHI; infinities propagate otherwise.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for tr_add_np")
    A, B = _ensure_tr_array(a), _ensure_tr_array(b)
    if A.values.shape != B.values.shape:
        raise ValueError("Shape mismatch in tr_add_np")
    vA, tA = A.values, A.tags
    vB, tB = B.values, B.tags

    phi_mask = (tA == tag_to_code(TRTag.PHI)) | (tB == tag_to_code(TRTag.PHI))
    pinf_conf = (tA == tag_to_code(TRTag.PINF)) & (tB == tag_to_code(TRTag.NINF))
    ninf_conf = (tA == tag_to_code(TRTag.NINF)) & (tB == tag_to_code(TRTag.PINF))
    conflict = pinf_conf | ninf_conf

    # Default REAL
    out_tags = np.full_like(tA, tag_to_code(TRTag.REAL))
    out_tags[phi_mask | conflict] = tag_to_code(TRTag.PHI)
    # Propagate remaining infinities
    pinf_any = (tA == tag_to_code(TRTag.PINF)) | (tB == tag_to_code(TRTag.PINF))
    ninf_any = (tA == tag_to_code(TRTag.NINF)) | (tB == tag_to_code(TRTag.NINF))
    out_tags[np.logical_and(pinf_any, ~conflict & ~phi_mask)] = tag_to_code(TRTag.PINF)
    out_tags[np.logical_and(ninf_any, ~conflict & ~phi_mask)] = tag_to_code(TRTag.NINF)

    # REAL + REAL numeric sum
    rr = (tA == tag_to_code(TRTag.REAL)) & (tB == tag_to_code(TRTag.REAL))
    out_vals = np.zeros_like(vA, dtype=vA.dtype)
    out_vals[rr] = vA[rr] + vB[rr]
    # Zero non-REAL for stable payloads
    out_vals[out_tags != tag_to_code(TRTag.REAL)] = 0.0
    return TRArray(out_vals, out_tags)


def tr_mul_np(
    a: Union[TRArray, "np.ndarray", float, int], b: Union[TRArray, "np.ndarray", float, int]
) -> TRArray:
    """Elementwise transreal multiplication over TRArray.

    Handles 0×∞ = PHI; REAL×REAL numeric product; sign‑consistent ∞ propagation.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for tr_mul_np")
    A, B = _ensure_tr_array(a), _ensure_tr_array(b)
    if A.values.shape != B.values.shape:
        raise ValueError("Shape mismatch in tr_mul_np")
    vA, tA = A.values, A.tags
    vB, tB = B.values, B.tags

    out_tags = np.full_like(tA, tag_to_code(TRTag.REAL))
    out_vals = np.zeros_like(vA, dtype=vA.dtype)

    phi_mask = (tA == tag_to_code(TRTag.PHI)) | (tB == tag_to_code(TRTag.PHI))
    out_tags[phi_mask] = tag_to_code(TRTag.PHI)

    a_real = tA == tag_to_code(TRTag.REAL)
    b_real = tB == tag_to_code(TRTag.REAL)
    a_zero = a_real & (vA == 0)
    b_zero = b_real & (vB == 0)
    a_inf = (tA == tag_to_code(TRTag.PINF)) | (tA == tag_to_code(TRTag.NINF))
    b_inf = (tB == tag_to_code(TRTag.PINF)) | (tB == tag_to_code(TRTag.NINF))

    zero_inf = (a_zero & b_inf) | (b_zero & a_inf)
    out_tags[zero_inf] = tag_to_code(TRTag.PHI)

    # REAL×REAL
    rr = a_real & b_real
    out_vals[rr] = vA[rr] * vB[rr]

    # Infinity sign
    sign_a = np.where(
        tA == tag_to_code(TRTag.PINF),
        1.0,
        np.where(tA == tag_to_code(TRTag.NINF), -1.0, np.sign(vA)),
    )
    sign_b = np.where(
        tB == tag_to_code(TRTag.PINF),
        1.0,
        np.where(tB == tag_to_code(TRTag.NINF), -1.0, np.sign(vB)),
    )
    inf_any = (a_inf | b_inf) & (~zero_inf) & (~phi_mask)
    pos_inf = inf_any & ((sign_a * sign_b) >= 0)
    neg_inf = inf_any & ((sign_a * sign_b) < 0)
    out_tags[pos_inf] = tag_to_code(TRTag.PINF)
    out_tags[neg_inf] = tag_to_code(TRTag.NINF)

    out_vals[out_tags != tag_to_code(TRTag.REAL)] = 0.0
    return TRArray(out_vals, out_tags)


def tr_div_np(
    a: Union[TRArray, "np.ndarray", float, int], b: Union[TRArray, "np.ndarray", float, int]
) -> TRArray:
    """Elementwise transreal division over TRArray.

    Implements 0/0=PHI; finite/∞=0; inf/finite sign rules; denom==0 with signed zero handling.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for tr_div_np")
    A, B = _ensure_tr_array(a), _ensure_tr_array(b)
    if A.values.shape != B.values.shape:
        raise ValueError("Shape mismatch in tr_div_np")
    vA, tA = A.values, A.tags
    vB, tB = B.values, B.tags

    out_tags = np.full_like(tA, tag_to_code(TRTag.REAL))
    out_vals = np.zeros_like(vA, dtype=vA.dtype)

    phi_mask = (tA == tag_to_code(TRTag.PHI)) | (tB == tag_to_code(TRTag.PHI))
    out_tags[phi_mask] = tag_to_code(TRTag.PHI)

    a_real = tA == tag_to_code(TRTag.REAL)
    b_real = tB == tag_to_code(TRTag.REAL)
    # Denominator zero (handle signed zero via copysign check)
    denom_zero = b_real & (vB == 0)
    b_neg_zero = denom_zero & (np.copysign(1.0, vB) < 0)
    a_pos = a_real & (vA > 0)
    a_neg = a_real & (vA < 0)
    a_zero = a_real & (vA == 0)
    out_tags[denom_zero & a_pos & (~b_neg_zero)] = tag_to_code(TRTag.PINF)
    out_tags[denom_zero & a_pos & b_neg_zero] = tag_to_code(TRTag.NINF)
    out_tags[denom_zero & a_neg & (~b_neg_zero)] = tag_to_code(TRTag.NINF)
    out_tags[denom_zero & a_neg & b_neg_zero] = tag_to_code(TRTag.PINF)
    out_tags[denom_zero & a_zero] = tag_to_code(TRTag.PHI)

    # inf/inf = PHI
    a_inf = (tA == tag_to_code(TRTag.PINF)) | (tA == tag_to_code(TRTag.NINF))
    b_inf = (tB == tag_to_code(TRTag.PINF)) | (tB == tag_to_code(TRTag.NINF))
    both_inf = a_inf & b_inf
    out_tags[both_inf] = tag_to_code(TRTag.PHI)

    # finite/inf = 0 (REAL)
    fin_over_inf = a_real & b_inf
    out_vals[fin_over_inf] = 0.0

    # inf/finite -> sign by denominator
    fin_b = b_real & (vB != 0)
    b_pos = fin_b & (vB > 0)
    b_neg = fin_b & (vB < 0)
    out_tags[(tA == tag_to_code(TRTag.PINF)) & b_pos] = tag_to_code(TRTag.PINF)
    out_tags[(tA == tag_to_code(TRTag.PINF)) & b_neg] = tag_to_code(TRTag.NINF)
    out_tags[(tA == tag_to_code(TRTag.NINF)) & b_pos] = tag_to_code(TRTag.NINF)
    out_tags[(tA == tag_to_code(TRTag.NINF)) & b_neg] = tag_to_code(TRTag.PINF)

    # REAL/REAL non-zero denom
    rr = a_real & b_real & (vB != 0)
    out_vals[rr] = vA[rr] / vB[rr]

    out_vals[out_tags != tag_to_code(TRTag.REAL)] = 0.0
    return TRArray(out_vals, out_tags)


class TRArrayPacked:
    """
    Packed transreal array representation.

    Stores values in a float ndarray and tag masks as bit-packed arrays
    for REAL, PINF, and NINF. PHI is implied as the remainder.
    """

    def __init__(
        self,
        values: "np.ndarray",
        real_bits: "np.ndarray",
        pinf_bits: "np.ndarray",
        ninf_bits: "np.ndarray",
        shape: tuple[int, ...],
    ):
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for TRArrayPacked")
        self.values = values
        self._real_bits = real_bits
        self._pinf_bits = pinf_bits
        self._ninf_bits = ninf_bits
        self._shape = tuple(shape)
        self._size = int(np.prod(shape))
        self._dtype = values.dtype

    @property
    def shape(self) -> tuple[int, ...]:
        return self._shape

    @property
    def dtype(self):
        return self._dtype

    @property
    def ndim(self) -> int:
        return len(self._shape)

    @property
    def size(self) -> int:
        return self._size

    def _unpack_all(self) -> tuple["np.ndarray", "np.ndarray", "np.ndarray"]:
        n = self._size
        real = _unpack_bits(self._real_bits, n).reshape(self._shape)
        pinf = _unpack_bits(self._pinf_bits, n).reshape(self._shape)
        ninf = _unpack_bits(self._ninf_bits, n).reshape(self._shape)
        return real, pinf, ninf

    def is_real(self) -> "np.ndarray":
        return self._unpack_all()[0]

    def is_pinf(self) -> "np.ndarray":
        return self._unpack_all()[1]

    def is_ninf(self) -> "np.ndarray":
        return self._unpack_all()[2]

    def is_phi(self) -> "np.ndarray":
        real, pinf, ninf = self._unpack_all()
        return ~(real | pinf | ninf)

    def to_numpy(self) -> "np.ndarray":
        return to_numpy(self)

    def __getitem__(self, key):
        # Slice values and reconstruct bit masks for the slice
        values = self.values[key]
        # Unpack + slice then repack for simplicity
        real = self.is_real()[key]
        pinf = self.is_pinf()[key]
        ninf = self.is_ninf()[key]
        # Scalar result
        if np.isscalar(values) or (isinstance(values, np.ndarray) and values.shape == ()):  # type: ignore
            # Determine tag
            if real:
                return TRScalar(float(values), TRTag.REAL)
            elif pinf:
                return TRScalar(float("nan"), TRTag.PINF)
            elif ninf:
                return TRScalar(float("nan"), TRTag.NINF)
            else:
                return TRScalar(float("nan"), TRTag.PHI)
        # Pack masks
        real_bits = _pack_bits(real.ravel())
        pinf_bits = _pack_bits(pinf.ravel())
        ninf_bits = _pack_bits(ninf.ravel())
        shape = values.shape
        return TRArrayPacked(values, real_bits, pinf_bits, ninf_bits, shape)


# Tag encoding for efficient storage
def tag_to_code(tag: TRTag) -> int:
    """Convert TR tag to uint8 code."""
    return {
        TRTag.REAL: 0,
        TRTag.PINF: 1,
        TRTag.NINF: 2,
        TRTag.PHI: 3,
    }[tag]


def code_to_tag(code: int) -> TRTag:
    """Convert uint8 code to TR tag."""
    return [TRTag.REAL, TRTag.PINF, TRTag.NINF, TRTag.PHI][code]


@overload
def from_numpy(arr: "np.ndarray", *, return_array: bool = False) -> TRArray:
    ...


@overload
def from_numpy(arr: float, *, return_array: bool = False) -> TRScalar:
    ...


def from_numpy(
    arr: Union["np.ndarray", float], *, return_array: bool = False
) -> Union[TRArray, TRScalar]:
    """
    Convert NumPy array or scalar to transreal representation.

    Args:
        arr: NumPy array or scalar
        return_array: If True, always return TRArray even for scalars

    Returns:
        TRArray for arrays, TRScalar for scalars (unless return_array=True)
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for from_numpy")

    # Handle scalar case
    if np.isscalar(arr):
        scalar = from_ieee_scalar(float(arr))
        if return_array:
            values = np.array([scalar.value if scalar.tag == TRTag.REAL else float("nan")])
            tags = np.array([tag_to_code(scalar.tag)], dtype=np.uint8)
            return TRArray(values, tags)
        else:
            return scalar

    # Ensure we have a NumPy array
    arr = np.asarray(arr)

    # Create value and tag arrays
    values = np.empty_like(arr, dtype=np.float64)
    tags = np.empty(arr.shape, dtype=np.uint8)

    # Classify elements
    finite_mask = np.isfinite(arr)
    nan_mask = np.isnan(arr)
    posinf_mask = np.isposinf(arr)
    neginf_mask = np.isneginf(arr)

    # Set values and tags
    values[finite_mask] = arr[finite_mask]
    tags[finite_mask] = tag_to_code(TRTag.REAL)

    values[nan_mask] = np.nan
    tags[nan_mask] = tag_to_code(TRTag.PHI)

    values[posinf_mask] = np.inf
    tags[posinf_mask] = tag_to_code(TRTag.PINF)

    values[neginf_mask] = -np.inf
    tags[neginf_mask] = tag_to_code(TRTag.NINF)

    return TRArray(values, tags)


def from_numpy_packed(arr: Union["np.ndarray", float]) -> Union[TRArrayPacked, TRScalar]:
    """
    Convert NumPy array or scalar to a packed transreal representation.

    For scalars, returns TRScalar. For arrays, returns TRArrayPacked which stores
    tag masks as bit-packed arrays (is_real, is_pinf, is_ninf), implying PHI as the remainder.
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for from_numpy_packed")
    if np.isscalar(arr):
        return from_ieee_scalar(float(arr))
    arr = np.asarray(arr)
    # Classify tags from IEEE
    finite_mask = np.isfinite(arr)
    nan_mask = np.isnan(arr)
    pinf_mask = np.isposinf(arr)
    ninf_mask = np.isneginf(arr)
    real_mask = finite_mask & ~nan_mask
    # Pack masks
    real_bits = _pack_bits(real_mask)
    pinf_bits = _pack_bits(pinf_mask)
    ninf_bits = _pack_bits(ninf_mask)
    # Values: keep original floats (including specials)
    values = arr.astype(np.float64, copy=True)
    return TRArrayPacked(values, real_bits, pinf_bits, ninf_bits, tuple(arr.shape))


def to_numpy_array(tr_array: TRArray) -> "np.ndarray":
    """
    Convert TRArray to NumPy array (IEEE representation).

    Args:
        tr_array: Transreal array

    Returns:
        NumPy array with appropriate IEEE values
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required for to_numpy_array")

    result = np.empty_like(tr_array.values)

    # Map each tag type
    real_mask = tr_array.tags == tag_to_code(TRTag.REAL)
    pinf_mask = tr_array.tags == tag_to_code(TRTag.PINF)
    ninf_mask = tr_array.tags == tag_to_code(TRTag.NINF)
    phi_mask = tr_array.tags == tag_to_code(TRTag.PHI)

    result[real_mask] = tr_array.values[real_mask]
    result[pinf_mask] = np.inf
    result[ninf_mask] = -np.inf
    result[phi_mask] = np.nan

    return result


def to_numpy(tr_obj: Union[TRScalar, TRArray, TRArrayPacked]) -> Union[float, "np.ndarray"]:
    """
    Convert TR object to NumPy representation.

    Args:
        tr_obj: TRScalar or TRArray

    Returns:
        float for TRScalar, NumPy array for TRArray
    """
    if isinstance(tr_obj, TRScalar):
        return to_ieee_scalar(tr_obj)
    elif isinstance(tr_obj, TRArray):
        return to_numpy_array(tr_obj)
    elif isinstance(tr_obj, TRArrayPacked):
        # Reconstruct from bit masks
        real = tr_obj.is_real()
        pinf = tr_obj.is_pinf()
        ninf = tr_obj.is_ninf()
        phi_mask = tr_obj.is_phi()
        out = tr_obj.values.copy()
        out[pinf] = np.inf
        out[ninf] = -np.inf
        out[phi_mask] = np.nan
        # REAL positions keep their numeric values
        return out
    else:
        raise TypeError(f"Expected TRScalar or TRArray, got {type(tr_obj)}")


# Import scalar conversions from main bridge
def from_ieee_scalar(x: float) -> TRScalar:
    """Convert IEEE float to TRScalar."""
    import math

    if math.isnan(x):
        return phi()
    elif math.isinf(x):
        if x > 0:
            return pinf()
        else:
            return ninf()
    else:
        return real(x)


def to_ieee_scalar(tr: TRScalar) -> float:
    """Convert TRScalar to IEEE float."""
    if tr.tag == TRTag.REAL:
        return tr.value
    elif tr.tag == TRTag.PINF:
        return float("inf")
    elif tr.tag == TRTag.NINF:
        return float("-inf")
    else:  # PHI
        return float("nan")


# Vectorized operations for efficiency
def validate_array(arr: "np.ndarray", name: str = "array") -> None:
    """
    Validate that array contains only finite values or IEEE special values.

    Args:
        arr: Array to validate
        name: Name for error messages

    Raises:
        ValueError: If array contains unsupported values
    """
    if not NUMPY_AVAILABLE:
        return

    # Check for complex numbers
    if np.iscomplexobj(arr):
        raise ValueError(f"{name} must be real-valued, got complex")

    # Check for object arrays or other non-numeric types
    if not np.issubdtype(arr.dtype, np.number):
        raise ValueError(f"{name} must be numeric, got {arr.dtype}")


def check_finite(tr_array: TRArray, name: str = "array") -> None:
    """
    Check if all elements in TRArray are finite (REAL).

    Args:
        tr_array: Array to check
        name: Name for error messages

    Raises:
        ValueError: If array contains non-REAL values
    """
    if not tr_array.is_real().all():
        n_pinf = tr_array.is_pinf().sum()
        n_ninf = tr_array.is_ninf().sum()
        n_phi = tr_array.is_phi().sum()

        msg = f"{name} contains non-REAL values: "
        parts = []
        if n_pinf > 0:
            parts.append(f"{n_pinf} PINF")
        if n_ninf > 0:
            parts.append(f"{n_ninf} NINF")
        if n_phi > 0:
            parts.append(f"{n_phi} PHI")

        raise ValueError(msg + ", ".join(parts))


# Utility functions for common operations
def where_real(tr_array: TRArray) -> Tuple["np.ndarray", ...]:
    """
    Get indices of REAL elements.

    Args:
        tr_array: Transreal array

    Returns:
        Tuple of index arrays (same as np.where)
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")

    return np.where(tr_array.is_real())


def count_tags(tr_array: TRArray) -> dict[str, int]:
    """
    Count elements by tag type.

    Args:
        tr_array: Transreal array

    Returns:
        Dictionary mapping tag names to counts
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")

    return {
        "REAL": int(tr_array.is_real().sum()),
        "PINF": int(tr_array.is_pinf().sum()),
        "NINF": int(tr_array.is_ninf().sum()),
        "PHI": int(tr_array.is_phi().sum()),
    }


def real_values(tr_array: TRArray) -> "np.ndarray":
    """
    Extract REAL values from array.

    Args:
        tr_array: Transreal array

    Returns:
        1D array of REAL values
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")

    mask = tr_array.is_real()
    return tr_array.values[mask]


def clip_infinities(tr_array: TRArray, max_value: float = 1e308) -> TRArray:
    """
    Clip infinite values to large finite values.

    Useful for interfacing with libraries that don't handle infinities well.

    Args:
        tr_array: Transreal array
        max_value: Maximum absolute value to use

    Returns:
        New TRArray with clipped values
    """
    if not NUMPY_AVAILABLE:
        raise ImportError("NumPy is required")

    values = tr_array.values.copy()
    tags = tr_array.tags.copy()

    # Clip PINF to max_value
    pinf_mask = tr_array.is_pinf()
    values[pinf_mask] = max_value
    tags[pinf_mask] = tag_to_code(TRTag.REAL)

    # Clip NINF to -max_value
    ninf_mask = tr_array.is_ninf()
    values[ninf_mask] = -max_value
    tags[ninf_mask] = tag_to_code(TRTag.REAL)

    return TRArray(values, tags)
