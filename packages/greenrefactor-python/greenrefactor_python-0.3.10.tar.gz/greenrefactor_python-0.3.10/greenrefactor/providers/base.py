from __future__ import annotations
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Tüm güç ölçüm sağlayıcıları için ortak arayüz.
    """
    name: str = "Base"

    def warmup(self) -> None:
        """İlk okumayı stabilize etmek için opsiyonel ısındırma."""
        return

    @abstractmethod
    def read_watts(self) -> float:
        """Anlık toplam güç (Watt) döndürür."""
        raise NotImplementedError