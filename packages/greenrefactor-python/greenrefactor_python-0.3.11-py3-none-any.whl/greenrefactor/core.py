from __future__ import annotations
import os, math, time, contextlib
from typing import Optional, Type

# Base + providers
class BaseProvider:
    name: str = "Base"
    def warmup(self) -> None: return
    def read_watts(self) -> float: raise NotImplementedError

# Psutil provider (always available as fallback)
try:
    import psutil, contextlib, importlib
except Exception:
    psutil = None

class PsutilProvider(BaseProvider):
    name = "Psutil"
    def __init__(self) -> None:
        self.idle = float(os.getenv("CARBON_CPU_IDLE_W", "10.0"))
        # Dynamic max power based on CPU core count: ~12.5W per core
        # 4 cores: 60W, 8 cores: 110W, 16 cores: 210W, 32 cores: 410W, 64 cores: 810W
        cpu_count = max(1, os.cpu_count() or 1)
        default_full = 10.0 + (cpu_count * 12.5)
        self.full = float(os.getenv("CARBON_CPU_FULL_W", str(default_full)))
        self._ema_w = None  # EMA smoothing for power readings
        self._ema_alpha = 0.4  # Lower alpha = more smoothing (was 0.6, now 0.4 for Docker stability)
        # For Docker: track host CPU via /proc/stat
        self._host_cpu_prev = None
        self._host_cpu_time_prev = None
        if psutil: psutil.cpu_percent(interval=None)
    def warmup(self) -> None:
        if psutil: psutil.cpu_percent(interval=None)
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
        if not psutil: return self.idle
        
        # Try to read host CPU first (for Docker with --pid=host)
        host_util = self._read_host_cpu_percent()
        if host_util is not None:
            # Use host CPU utilization
            w_raw = self.idle + (self.full - self.idle) * host_util
        else:
            # Use per-core CPU measurement for better accuracy
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            if per_core:
                # Use average across all cores for conservative measurement
                util = sum(per_core) / len(per_core) / 100.0
            else:
                util = psutil.cpu_percent(interval=0.1) / 100.0
            util = max(0.0, min(1.0, util))  # Clamp to [0, 1]
            w_raw = self.idle + (self.full - self.idle) * util
        
        # Apply EMA smoothing with lower alpha for stability (especially important in Docker)
        if self._ema_w is None:
            self._ema_w = w_raw
        else:
            self._ema_w = self._ema_alpha * w_raw + (1 - self._ema_alpha) * self._ema_w
        return self._ema_w

# Optional providers
RaplProvider = None
PowerMetricsProvider = None
NvmlProvider = None
with contextlib.suppress(Exception):
    from .providers.rapl_provider import RaplProvider      # type: ignore
try:
    from .providers.powermetrics_provider import PowerMetricsProvider  # type: ignore
except Exception as e:
    print(f"ERROR: Failed to import PowerMetricsProvider: {e}")
    PowerMetricsProvider = None
with contextlib.suppress(Exception):
    from .providers.nvml_provider import NvmlProvider      # type: ignore
with contextlib.suppress(Exception):
    from .providers.remote_provider import RemoteProvider  # type: ignore

def _good_power_samples(p: BaseProvider, n: int = 5, dt: float = 0.2) -> bool:
    ok = False
    for _ in range(n):
        try:
            w = float(p.read_watts())
            if math.isfinite(w) and w > 0.01: ok = True
        except Exception:
            pass
        time.sleep(dt)
    return ok

def choose_provider(enable_gpu: bool = True) -> BaseProvider:
    """Order: RAPL → powermetrics → (opt) NVML → Psutil"""
    forced = os.getenv("CARBON_PROVIDER", "").strip().lower()

    ordered: list[Type[BaseProvider]] = []
    
    # Check for Remote Provider first
    remote_url = os.getenv("CARBON_REMOTE_URL", "")
    if remote_url and RemoteProvider:
        # Initialize RemoteProvider with Psutil as fallback
        # This allows dynamic switching: if remote is down, it uses Psutil.
        psutil_fallback = PsutilProvider()
        rp = RemoteProvider(remote_url, fallback_provider=psutil_fallback)
        print(f"[carbon] provider = Remote (Dynamic Fallback to Psutil)", flush=True)
        return rp

    if RaplProvider:           ordered.append(RaplProvider)             # Linux RAPL
    if PowerMetricsProvider:   ordered.append(PowerMetricsProvider)     # macOS powermetrics
    if enable_gpu and NvmlProvider: ordered.append(NvmlProvider)        # NVIDIA NVML
    ordered.append(PsutilProvider)                                      # fallback

    # Forced
    if forced:
        for cls in ordered:
            key = cls.__name__.replace("Provider", "").lower()
            if key == forced:
                cand = cls()
                print(f"[carbon] provider(forced) = {cand.name}", flush=True)
                return cand
        print(f"[carbon] WARN unknown CARBON_PROVIDER={forced}", flush=True)

    # Auto probe
    for cls in ordered:
        try:
            cand = cls()  # type: ignore
            print(f"[carbon] Probing provider: {cand.name}", flush=True)
            cand.warmup()
            if _good_power_samples(cand):
                print(f"[carbon] provider = {cand.name}", flush=True)
                return cand
            else:
                print(f"[carbon] Provider {cand.name} failed 'good samples' check (returned 0 or invalid).", flush=True)
        except Exception as e:
            print(f"[carbon] Provider {cls.__name__} failed init/warmup: {e}", flush=True)
            continue

    print("[carbon] provider = Psutil (fallback)", flush=True)
    return PsutilProvider()