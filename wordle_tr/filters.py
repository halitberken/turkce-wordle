"""Hafta 8: Aday filtreleme yöntemleri.

Aşağıdaki fonksiyonların hepsi aynı imzaya sahiptir, (adaylar, tahmin, desen) -> kalan
adaylar, ve simulate.play_game(filter_fn=...) ile birbirinin yerine kullanılabilir:
  - filter_by_feedback:    her aday için geri bildirimi yeniden hesaplar (referans)
  - filter_by_constraints: gözlemi kısıtlara çevirip adayları kontrol eder
  - PatternTable.filter_words: önceden hesaplanmış tablodan okur (en hızlı)
CSPSolver ise listeyi taramak yerine sözlük ağacında arama yapar; tüm geçmişin
kısıtlarıyla sıfırdan çalıştığı için ayrı bir arayüzü vardır (scripts/benchmark_filters.py).
"""

from typing import Iterable

from .constraints import Constraints
from .feedback import filter_candidates as filter_by_feedback


def filter_by_constraints(candidates: Iterable[str], guess: str, pattern: int) -> list[str]:
    constraints = Constraints.from_history([(guess, pattern)])
    return [word for word in candidates if constraints.is_satisfied(word)]


__all__ = ["filter_by_constraints", "filter_by_feedback"]
