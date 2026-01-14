from __future__ import annotations
import os
import time
import json
import urllib.request
from .base import BaseProvider

class RemoteProvider(BaseProvider):
    name = "Remote"

    def __init__(self, url: str, fallback_provider: BaseProvider = None):
        self.url = url
        self._last_watts = 0.0
        self.fallback = fallback_provider
        self._using_fallback = False

    def warmup(self) -> None:
        # Try once, but don't block or fail
        self.read_watts()

    def read_watts(self) -> float:
        try:
            with urllib.request.urlopen(self.url, timeout=0.5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    self._last_watts = float(data.get("watts", 0.0))
                    self._using_fallback = False
                    return self._last_watts
        except Exception:
            # Connection failed, use fallback if available
            pass
        
        self._using_fallback = True
        if self.fallback:
            return self.fallback.read_watts()
        return self._last_watts

    @property
    def is_using_fallback(self) -> bool:
        return self._using_fallback
