"""Hafta 7: Temel (baseline) ajanlar.

Asıl yöntemlerin (entropi, expectimax) ne kadar iyi olduğunu görmek için bu ajanlarla
karşılaştıracağız. İkisi de yalnızca geri bildirimle tutarlı adaylardan tahmin yapar.
"""

import random
from collections import Counter
from typing import Optional, Sequence

from ..feedback import History
from .base import Agent


class RandomAgent(Agent):
    """Geri bildirimle hâlâ tutarlı adaylardan rastgele birini tahmin eder."""

    name = "rastgele"

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def choose_guess(self, history: History, candidates: Sequence[str]) -> str:
        return self.rng.choice(candidates)


class LetterFrequencyAgent(Agent):
    """Kalan adaylarda en sık geçen harfleri içeren adayı tahmin eder.

    Bir kelimenin puanı, içindeki *farklı* harflerin kaç adayda geçtiğinin toplamıdır.
    Tekrarlanan harf bir kez sayılır; böylece ajan çok sayıda farklı ve yaygın harf
    deneyen kelimeleri seçer. Bu, insanların sezgisel stratejisine benzer.
    Eşitlikte listede önce gelen kelime seçilir, yani ajan deterministiktir.
    """

    name = "harf_sikligi"

    def choose_guess(self, history: History, candidates: Sequence[str]) -> str:
        letter_counts = Counter()
        for word in candidates:
            letter_counts.update(set(word))
        return max(candidates, key=lambda word: sum(letter_counts[ch] for ch in set(word)))
