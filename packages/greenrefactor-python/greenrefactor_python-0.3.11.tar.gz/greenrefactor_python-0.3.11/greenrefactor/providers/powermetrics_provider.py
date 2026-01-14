from __future__ import annotations
import subprocess, sys, re
from typing import Iterable
from .base import BaseProvider

_CPU_RE = re.compile(r"CPU Power:\s*([0-9.]+)\s*(m?W)", re.IGNORECASE)
_GPU_RE = re.compile(r"GPU Power:\s*([0-9.]+)\s*(m?W)", re.IGNORECASE)
_PROC_RE = re.compile(r"pid\s+(\d+).*?([0-9.]+)\s*mW", re.IGNORECASE)

def _run_powermetrics(args: list[str], timeout: float = 3.0) -> str:
    cmd = ["powermetrics", "-i", "100", "-n", "1"] + args
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            return ""
    return out or ""

class PowerMetricsProvider(BaseProvider):
    """System-level powermetrics provider."""
    name = "PowerMetrics"

    def available(self) -> bool:
        return sys.platform == "darwin"

    def read_watts(self) -> float:
        # 'smc' sampler is not reliable for power on all Macs.
        # Explicitly ask for cpu_power to keep output small and fast.
        # Increase timeout for high load scenarios.
        raw = _run_powermetrics(["--samplers", "cpu_power"], timeout=3.0) 
        if not raw:
            return 0.0
        
        total = 0.0
        
        # Parse CPU
        cpu_match = _CPU_RE.search(raw)
        if cpu_match:
            val = float(cpu_match.group(1))
            unit = cpu_match.group(2).lower()
            if unit == "mw": val /= 1000.0
            total += val
            
        # Parse GPU
        gpu_match = _GPU_RE.search(raw)
        if gpu_match:
            val = float(gpu_match.group(1))
            unit = gpu_match.group(2).lower()
            if unit == "mw": val /= 1000.0
            total += val
        
        return total

def read_process_power_map(pids: Iterable[int]) -> dict[int, float]:
    """Return instant power (W) for the provided process IDs."""
    if sys.platform != "darwin":
        return {}
    pid_set = {int(pid) for pid in pids if isinstance(pid, int)}
    if not pid_set:
        return {}
    args = ["--samplers", "tasks", "--show-process-energy"]
    raw = _run_powermetrics(args, timeout=2.0)
    if not raw:
        return {}
    result: dict[int, float] = {}
    for match in _PROC_RE.finditer(raw):
        pid = int(match.group(1))
        if pid not in pid_set:
            continue
        mw = float(match.group(2))
        result[pid] = mw / 1000.0  # mW → W
    return result