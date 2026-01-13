"""
Compatibility shim: allow `import zeroproofml as zp`.

This package re-exports the public API from `zeroproof` and aliases
its common subpackages so `import zeroproofml.training` etc. work.

Rationale: the PyPI distribution is named `zeroproofml`, while the
code package historically used the `zeroproof` import path. Keeping
both paths available avoids a breaking rename.

For v0.4 the underlying implementation is the new Signed Common Meadow
(SCM) stack. The former transreal codebase has been archived under
``legacy/zeroproof_v0_3`` and is intentionally not importable.
"""

from __future__ import annotations

import importlib as _importlib
import sys as _sys

# Import the real implementation
_zp = _importlib.import_module("zeroproof")

# Re-export top-level public API lazily
__all__ = getattr(_zp, "__all__", [])


def __getattr__(name):  # PEP 562: delegate attribute access to `zeroproof`
    return getattr(_zp, name)


# Mirror common subpackages so `import zeroproofml.<mod>` resolves.
# Keep this list aligned with the v0.4 SCM-first package layout.
for _sub in (
    "scm",
    "autodiff",
    "layers",
    "losses",
    "training",
    "inference",
    "metrics",
    "utils",
):
    try:
        _sys.modules[f"{__name__}.{_sub}"] = _importlib.import_module(f"zeroproof.{_sub}")
    except ModuleNotFoundError:
        # Optional modules may be absent in minimal installs; ignore.
        pass

# Convenience metadata
try:
    __version__ = _zp.__version__  # type: ignore[attr-defined]
except Exception:
    __version__ = "0.4.0"
