from __future__ import annotations
import os, time
from .base import BaseProvider

class RaplProvider(BaseProvider):
    name = "RAPL"

    def __init__(self):
        self._paths = []
        base = "/sys/class/powercap"
        if os.path.isdir(base):
            for root, dirs, files in os.walk(base):
                if "energy_uj" in files:
                    self._paths.append(os.path.join(root, "energy_uj"))
        self._last = None
        self._last_t = None

    def _read_energy_j(self) -> float:
        total_uj = 0
        for p in self._paths:
            try:
                with open(p, "r") as f:
                    total_uj += int(f.read().strip())
            except Exception:
                pass
        return total_uj / 1_000_000.0

    def read_watts(self) -> float:
        now = time.time()
        e = self._read_energy_j()
        if self._last is None:
            self._last = e; self._last_t = now
            return 0.0
        de = e - self._last
        dt = max(1e-6, now - self._last_t)
        self._last, self._last_t = e, now
        return max(0.0, de / dt)