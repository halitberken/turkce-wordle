"""Hafta 8: Geri bildirimleri kısıtlara (constraints) çevirme.

Her (tahmin, desen) gözlemi gizli kelime hakkında kısıtlar üretir:
  - Yeşil harf:  o pozisyondaki harf kesin belli          (X_i = L)
  - Sarı/gri harf: o pozisyonda o harf olamaz              (X_i ≠ L)
  - Harf sayısı: tahmindeki yeşil + sarı kopya sayısı k ise harf en az k kez geçer;
    aynı harfin bir kopyası gri ise harf tam olarak k kez geçer (k = 0 ise hiç yok).

Bu dört kısıt türünün birlikte sağlanması, "kelime gizli olsaydı aynı deseni üretirdi"
koşuluna denktir (kanıt: docs/hafta8_kisitlar_ve_desen_tablosu.md). Bu yüzden filtrelerken
her aday için geri bildirimi yeniden hesaplamak yerine kısıtları kontrol etmek yeterlidir.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from .alphabet import ALPHABET, WORD_LENGTH, sort_key, to_upper
from .feedback import GREEN, YELLOW, History, decode_pattern


class ContradictionError(ValueError):
    """Gözlemler birbiriyle çelişiyor (örneğin desen yanlış girildi)."""


@dataclass
class Constraints:
    fixed: list[Optional[str]] = field(default_factory=lambda: [None] * WORD_LENGTH)
    forbidden: list[set[str]] = field(default_factory=lambda: [set() for _ in range(WORD_LENGTH)])
    min_count: dict[str, int] = field(default_factory=dict)
    max_count: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_history(cls, history: History) -> "Constraints":
        constraints = cls()
        for guess, pattern in history:
            constraints.add_observation(guess, pattern)
        return constraints

    def add_observation(self, guess: str, pattern: int) -> None:
        """Bir tahmin ve deseninden çıkan kısıtları ekler."""
        seen = Counter()      # harfin yeşil + sarı kopya sayısı
        has_gray = set()      # en az bir kopyası gri olan harfler
        for i, (letter, color) in enumerate(zip(guess, decode_pattern(pattern))):
            if color == GREEN:
                if self.fixed[i] not in (None, letter):
                    raise ContradictionError(f"{i + 1}. pozisyon hem {to_upper(self.fixed[i])} "
                                             f"hem {to_upper(letter)} olamaz")
                self.fixed[i] = letter
                seen[letter] += 1
            else:
                self.forbidden[i].add(letter)
                if color == YELLOW:
                    seen[letter] += 1
                else:
                    has_gray.add(letter)
        for letter, count in seen.items():
            self.min_count[letter] = max(self.min_count.get(letter, 0), count)
        for letter in has_gray:
            self.max_count[letter] = min(self.max_count.get(letter, WORD_LENGTH), seen[letter])
        self._check_consistency()

    def _check_consistency(self) -> None:
        for i, letter in enumerate(self.fixed):
            if letter is not None and letter in self.forbidden[i]:
                raise ContradictionError(f"{i + 1}. pozisyondaki {to_upper(letter)} hem yeşil hem yasak")
        for letter, low in self.min_count.items():
            if low > self.max_count.get(letter, WORD_LENGTH):
                raise ContradictionError(f"{to_upper(letter)} harfi için en az {low}, en çok "
                                         f"{self.max_count[letter]} kopya çelişiyor")
        if sum(self.min_count.values()) > WORD_LENGTH:
            raise ContradictionError("Gereken harfler 5 pozisyona sığmıyor")

    def is_satisfied(self, word: str) -> bool:
        """Kelime tüm kısıtları sağlıyor mu?"""
        for i, letter in enumerate(word):
            if self.fixed[i] is not None and letter != self.fixed[i]:
                return False
            if letter in self.forbidden[i]:
                return False
        counts = Counter(word)
        if any(counts[letter] < low for letter, low in self.min_count.items()):
            return False
        return all(counts[letter] <= high for letter, high in self.max_count.items())

    def domains(self) -> list[set[str]]:
        """Her pozisyon için hâlâ mümkün olan harfler (CSP'deki değişken alanları).
        Tekli kısıtlar burada uygulanır: buna düğüm tutarlılığı (node consistency) denir."""
        absent = {letter for letter, high in self.max_count.items() if high == 0}
        result = []
        for i in range(WORD_LENGTH):
            if self.fixed[i] is not None:
                result.append({self.fixed[i]})
            else:
                result.append(set(ALPHABET) - self.forbidden[i] - absent)
        return result

    def describe(self) -> list[str]:
        """Kısıtları insanın okuyabileceği Türkçe cümlelere çevirir (demo ve sunum için)."""
        lines = [f"{i + 1}. harf {to_upper(letter)}"
                 for i, letter in enumerate(self.fixed) if letter is not None]
        absent = sorted((l for l, high in self.max_count.items() if high == 0), key=sort_key)
        if absent:
            lines.append("Kelimede yok: " + ", ".join(to_upper(l) for l in absent))
        for letter in sorted(self.min_count, key=sort_key):
            low = self.min_count[letter]
            exact = self.max_count.get(letter) == low
            known = self.fixed.count(letter)
            if low > known:
                text = f"{to_upper(letter)} {'tam' if exact else 'en az'} {low} kez geçiyor"
                banned = [str(i + 1) for i in range(WORD_LENGTH)
                          if self.fixed[i] is None and letter in self.forbidden[i]]
                if banned:
                    text += f", {'/'.join(banned)}. pozisyonda değil"
                lines.append(text)
            elif exact:
                lines.append(f"{to_upper(letter)} başka pozisyonda yok")
        return lines
