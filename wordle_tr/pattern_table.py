"""Hafta 8: Önceden hesaplanmış desen tablosu.

Tablo M[g, a] = feedback(tahmin g, gizli kelime a). 5.370 tahmin × 1.900 gizli kelime
için yaklaşık 10 milyon hücre vardır; her hücre 0..242 arası bir desen olduğu için
uint8 (1 bayt) yeter ve tablo ~10 MB tutar.

Tablo bir kez hesaplanıp diske kaydedilir. Sonrasında:
  - filtreleme tek bir dizi karşılaştırmasıdır: adaylar[M[g, adaylar] == desen]
  - Hafta 9'daki entropi ajanı bir tahminin adayları nasıl böldüğünü
    np.bincount(M[g, adaylar]) ile anında bulur.

Hesaplama numpy ile vektörleştirilmiştir. Tekrarlanan harf kuralı (bkz. feedback.py)
şu gözleme dayanır: yeşil olmayan i pozisyonundaki harf L, ancak gizli kelimede
eşleşmemiş L sayısı, tahminde i'den önceki eşleşmemiş L sayısından büyükse sarıdır.
"""

import hashlib
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from .alphabet import WORD_LENGTH
from .feedback import NUM_PATTERNS
from .words import DATA_DIR, encode

DEFAULT_CACHE_DIR = DATA_DIR / "cache"

_POWERS = 3 ** np.arange(WORD_LENGTH, dtype=np.int32)
# _EARLIER[i, k] = k < i
_EARLIER = np.tril(np.ones((WORD_LENGTH, WORD_LENGTH), dtype=bool), k=-1)


def compute_pattern_matrix(guess_codes: np.ndarray, answer_codes: np.ndarray,
                           chunk_size: int = 128) -> np.ndarray:
    """Tüm (tahmin, gizli kelime) çiftlerinin desenlerini hesaplar.
    Girdiler words.encode() çıktısıdır; sonuç (tahmin sayısı, gizli kelime sayısı) uint8 matrisi."""
    matrix = np.empty((len(guess_codes), len(answer_codes)), dtype=np.uint8)
    answers = answer_codes[None, :, None, :]                       # (1, A, 1, 5)
    for start in range(0, len(guess_codes), chunk_size):
        guesses = guess_codes[start:start + chunk_size]            # (C, 5)
        # same[c, a, i, j]: tahminin i. harfi gizli kelimenin j. harfine eşit mi
        same = guesses[:, None, :, None] == answers                 # (C, A, 5, 5)
        green = np.diagonal(same, axis1=2, axis2=3)                 # (C, A, 5)
        not_green = ~green
        # Gizli kelimede, yeşil olmayan pozisyonlardaki aynı harf sayısı
        available = (same & not_green[:, :, None, :]).sum(axis=3)   # (C, A, 5)
        # Tahminde i'den önce gelen, yeşil olmayan aynı harf sayısı
        repeats = (guesses[:, :, None] == guesses[:, None, :]) & _EARLIER   # (C, 5, 5)
        earlier = (repeats[:, None, :, :] & not_green[:, :, None, :]).sum(axis=3)  # (C, A, 5)
        yellow = not_green & (available > earlier)
        colors = 2 * green.astype(np.int32) + yellow
        matrix[start:start + len(guesses)] = colors @ _POWERS
    return matrix


class PatternTable:
    def __init__(self, guesses: Sequence[str], answers: Sequence[str], matrix: np.ndarray):
        self.guesses = list(guesses)
        self.answers = list(answers)
        self.matrix = matrix
        self.guess_index = {word: i for i, word in enumerate(self.guesses)}
        self.answer_index = {word: i for i, word in enumerate(self.answers)}

    @classmethod
    def build(cls, guesses: Sequence[str], answers: Sequence[str],
              cache_dir: Optional[Path] = DEFAULT_CACHE_DIR) -> "PatternTable":
        """Tabloyu önbellekten yükler; yoksa hesaplayıp önbelleğe yazar."""
        cache_path = None
        if cache_dir is not None:
            key = hashlib.sha1(("\n".join(guesses) + "|" + "\n".join(answers)).encode()).hexdigest()[:12]
            cache_path = Path(cache_dir) / f"pattern_matrix_{key}.npy"
            if cache_path.exists():
                return cls(guesses, answers, np.load(cache_path))
        matrix = compute_pattern_matrix(encode(guesses), encode(answers))
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache_path, matrix)
        return cls(guesses, answers, matrix)

    def pattern(self, guess: str, answer: str) -> int:
        return int(self.matrix[self.guess_index[guess], self.answer_index[answer]])

    def all_ids(self) -> np.ndarray:
        return np.arange(len(self.answers))

    def filter_ids(self, candidate_ids: np.ndarray, guess: str, pattern: int) -> np.ndarray:
        """Desenle tutarlı adayların indeksleri: tek bir vektör karşılaştırması."""
        row = self.matrix[self.guess_index[guess]]
        return candidate_ids[row[candidate_ids] == pattern]

    def filter_words(self, candidates: Sequence[str], guess: str, pattern: int) -> list[str]:
        """simulate.play_game ile uyumlu (kelime listesi alan) filtre."""
        ids = np.fromiter((self.answer_index[w] for w in candidates), dtype=np.int64, count=len(candidates))
        return [self.answers[i] for i in self.filter_ids(ids, guess, pattern)]

    def partition_counts(self, guess: str, candidate_ids: np.ndarray) -> np.ndarray:
        """Tahmin adayları hangi desenlere kaç kelime olarak böler? (Hafta 9: entropi)"""
        row = self.matrix[self.guess_index[guess]]
        return np.bincount(row[candidate_ids], minlength=NUM_PATTERNS)
