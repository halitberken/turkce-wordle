"""Tüm ajanların ortak arayüzü."""

from abc import ABC, abstractmethod
from typing import Sequence

from ..feedback import History


class Agent(ABC):
    """Bir Wordle ajanı.

    Her turda oyun geçmişini ve hâlâ gizli kelime olabilecek adayları alır, bir sonraki
    tahmini döndürür. Aday listesini oyun döngüsü (simulate.py) günceller; böylece
    filtreleme yöntemi (Hafta 8) ajanlara dokunmadan değiştirilebilir.
    """

    name = "ajan"

    def reset(self) -> None:
        """Yeni bir oyun başlamadan önce çağrılır."""

    @abstractmethod
    def choose_guess(self, history: History, candidates: Sequence[str]) -> str:
        """Bir sonraki tahmini döndürür. `candidates` hiçbir zaman boş değildir."""
