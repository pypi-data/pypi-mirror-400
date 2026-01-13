"""
Lightweight logging adapters.

Exposes a unified TensorBoard writer wrapper when tensorboard is available.
"""

try:  # pragma: no cover - optional dependency wrapper
    from .tensorboard import ZPTBWriter  # type: ignore
except Exception:  # TensorBoard is optional
    ZPTBWriter = None  # type: ignore

__all__ = [
    "ZPTBWriter",
]
