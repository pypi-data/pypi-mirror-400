from __future__ import annotations
from typing import Iterable, Optional
from .base import BaseProvider

try:
    import pynvml
except Exception:  # pragma: no cover - NVML optional
    pynvml = None

class NvmlProvider(BaseProvider):
    name = "NVML"

    def __init__(self):
        self.nvml = None
        if pynvml is None:
            return
        try:
            pynvml.nvmlInit()
            self.nvml = pynvml
        except Exception:
            self.nvml = None

    def read_watts(self) -> float:
        if not self.nvml:
            return 0.0
        w = 0.0
        try:
            cnt = self.nvml.nvmlDeviceGetCount()
            for i in range(cnt):
                h = self.nvml.nvmlDeviceGetHandleByIndex(i)
                w += self.nvml.nvmlDeviceGetPowerUsage(h) / 1000.0
        except Exception:
            pass
        return w


def _nvml_handle():
    if pynvml is None:
        return None
    try:
        pynvml.nvmlInit()
        return pynvml
    except Exception:
        return None


def read_process_gpu_power(pids: Iterable[int]) -> dict[int, float]:
    """Return per-PID GPU power (W) using NVML accounting stats."""
    pid_set = {int(pid) for pid in pids if isinstance(pid, int)}
    if not pid_set:
        return {}
    nvml = _nvml_handle()
    if nvml is None:
        return {}

    result: dict[int, float] = {}
    try:
        device_count = nvml.nvmlDeviceGetCount()
    except Exception:
        return {}

    for idx in range(device_count):
        try:
            handle = nvml.nvmlDeviceGetHandleByIndex(idx)
            pids_on_device = nvml.nvmlDeviceGetAccountingPids(handle)
        except Exception:
            continue

        for pid in pids_on_device:
            if pid not in pid_set:
                continue
            try:
                stats = nvml.nvmlDeviceGetAccountingStats(handle, pid)
            except Exception:
                continue
            power = getattr(stats, "powerUsage", None)
            if power is None or power == nvml.NVML_VALUE_NOT_AVAILABLE:
                continue
            result[pid] = max(result.get(pid, 0.0), float(power) / 1000.0)

    return result