from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


def _read_first_line(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.readline().strip()
    except Exception:
        return None


def _linux_cpu_model() -> Optional[str]:
    if os.name != "posix":
        return None
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    _, v = line.split(":", 1)
                    return v.strip()
    except Exception:
        return None
    return None


def _linux_mem_total_mb() -> Optional[float]:
    if os.name != "posix":
        return None
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        kb = float(parts[1])
                        return kb / 1024.0
    except Exception:
        return None
    return None


def peak_rss_mb() -> Optional[float]:
    """
    Best-effort peak resident set size (RSS) in MB for the current process.
    Linux returns ru_maxrss in KiB; macOS returns bytes.
    """
    try:
        import resource

        v = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if platform.system().lower() == "darwin":
            return v / (1024.0 * 1024.0)
        return v / 1024.0
    except Exception:
        return None


def torch_cuda_peak_mb() -> Optional[float]:
    try:
        import torch

        if not torch.cuda.is_available():
            return None
        return float(torch.cuda.max_memory_allocated()) / (1024.0 * 1024.0)
    except Exception:
        return None


@dataclass(frozen=True)
class SystemInfo:
    platform: str
    platform_release: str
    python_version: str
    cpu_model: Optional[str]
    cpu_count: Optional[int]
    mem_total_mb: Optional[float]


def collect_system_info() -> Dict[str, Any]:
    info = SystemInfo(
        platform=platform.system(),
        platform_release=platform.release(),
        python_version=platform.python_version(),
        cpu_model=_linux_cpu_model(),
        cpu_count=(os.cpu_count() if hasattr(os, "cpu_count") else None),
        mem_total_mb=_linux_mem_total_mb(),
    )
    return asdict(info)


def time_call(fn, *args, **kwargs):
    """
    Return (result, seconds_elapsed).
    """
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    t1 = time.perf_counter()
    return out, float(t1 - t0)
