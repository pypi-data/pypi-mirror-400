from __future__ import annotations
import os
import time
import psutil
from .base import BaseProvider

class PsutilProvider(BaseProvider):
    """
    Platformdan bağımsız, CPU kullanımına göre basit güç tahmini.
    NVIDIA varsa NVML ile GPU watt'ını ekler (opsiyonel).
    """
    name = "Psutil"

    def __init__(self) -> None:
        self.cpu_idle_w = float(os.getenv("CARBON_CPU_IDLE_W", "10.0"))
        # Dynamic max power based on CPU core count: ~12.5W per core
        cpu_count = max(1, psutil.cpu_count() or 1)
        default_full = 10.0 + (cpu_count * 12.5)
        self.cpu_full_w = float(os.getenv("CARBON_CPU_FULL_W", str(default_full)))
        self._ema_w = None  # EMA smoothing for power readings
        self._ema_alpha = 0.4  # Lower alpha = more smoothing (was 0.6, now 0.4 for Docker stability)
        # For Docker: track host CPU via /proc/stat
        self._host_cpu_prev = None
        self._host_cpu_time_prev = None

        self._nvml = None
        if os.getenv("CARBON_ENABLE_GPU", "1") == "1":
            try:
                import pynvml
                pynvml.nvmlInit()
                self._nvml = pynvml
            except Exception:
                self._nvml = None

        # ilk çağrıda spike olmaması için
        psutil.cpu_percent(interval=None)

    def warmup(self) -> None:
        psutil.cpu_percent(interval=None)
        # Initialize host CPU reading if in Docker
        self._read_host_cpu_percent()

    def _read_host_cpu_percent(self) -> float:
        """Read host CPU usage from /proc/stat (works in Docker with --pid=host)."""
        try:
            with open("/proc/stat", "r") as f:
                line = f.readline()  # First line is total CPU
                if not line.startswith("cpu "):
                    return None
                fields = line.split()
                # user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice
                user = int(fields[1]) + int(fields[2])  # user + nice
                system = int(fields[3])
                idle = int(fields[4]) + int(fields[5])  # idle + iowait
                total = user + system + idle
                
                now = time.time()
                if self._host_cpu_prev is not None:
                    dt = now - self._host_cpu_time_prev
                    if dt > 0:
                        idle_diff = idle - self._host_cpu_prev[2]
                        total_diff = total - self._host_cpu_prev[3]
                        if total_diff > 0:
                            util = 1.0 - (idle_diff / total_diff)
                            return max(0.0, min(1.0, util))
                
                self._host_cpu_prev = (user, system, idle, total)
                self._host_cpu_time_prev = now
                return None
        except Exception:
            return None

    def read_watts(self) -> float:
        # Try to read host CPU first (for Docker with --pid=host)
        host_util = self._read_host_cpu_percent()
        if host_util is not None:
            # Use host CPU utilization (more accurate in Docker)
            cpu_w_raw = self.cpu_idle_w + (self.cpu_full_w - self.cpu_idle_w) * host_util
        else:
            # Use per-core CPU measurement for better accuracy
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            if per_core:
                # Use average across all cores for conservative measurement
                util = sum(per_core) / len(per_core) / 100.0
            else:
                util = psutil.cpu_percent(interval=0.1) / 100.0
            util = max(0.0, min(1.0, util))
            cpu_w_raw = self.cpu_idle_w + (self.cpu_full_w - self.cpu_idle_w) * util

        gpu_w = 0.0
        if self._nvml:
            try:
                cnt = self._nvml.nvmlDeviceGetCount()
                for i in range(cnt):
                    h = self._nvml.nvmlDeviceGetHandleByIndex(i)
                    gpu_w += self._nvml.nvmlDeviceGetPowerUsage(h) / 1000.0
            except Exception:
                pass

        w_raw = cpu_w_raw + gpu_w
        # Apply EMA smoothing for stability (especially important in Docker/macOS)
        if self._ema_w is None:
            self._ema_w = w_raw
        else:
            self._ema_w = self._ema_alpha * w_raw + (1 - self._ema_alpha) * self._ema_w
        return float(self._ema_w)