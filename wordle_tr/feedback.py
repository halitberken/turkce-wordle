"""Wordle renk geri bildirimi ve desen (pattern) kodlaması.

Her harf için üç renk vardır:
    GRAY   (gri)   = 0: harf gizli kelimede yok ya da tüm kopyaları zaten işaretlendi
    YELLOW (sarı)  = 1: harf var ama başka pozisyonda
    GREEN  (yeşil) = 2: harf doğru pozisyonda

Beş rengi 3 tabanında tek bir tamsayıya kodluyoruz:
    desen = renk[0]·1 + renk[1]·3 + renk[2]·9 + renk[3]·27 + renk[4]·81
Böylece 3^5 = 243 olası desen 0..242 arası sayılarla gösterilir. 242 "hepsi yeşil",
yani kelimenin bulunduğu anlamına gelir. Tamsayı kodlama sayesinde desen tablosu
(pattern_table.py) küçük bir uint8 matrisi olarak saklanabilir.
"""

from collections import Counter
from typing import Iterable, Sequence

from .alphabet import WORD_LENGTH

GRAY, YELLOW, GREEN = 0, 1, 2
NUM_PATTERNS = 3 ** WORD_LENGTH
ALL_GREEN = NUM_PATTERNS - 1

# Oyun geçmişi: [(tahmin, desen), ...]
History = Sequence[tuple[str, int]]

_POWERS = tuple(3 ** i for i in range(WORD_LENGTH))
_EMOJI = {GRAY: "⬜", YELLOW: "🟨", GREEN: "🟩"}
_INPUT_CODES = {"g": GRAY, "0": GRAY, "s": YELLOW, "1": YELLOW, "y": GREEN, "2": GREEN}


def feedback(guess: str, answer: str) -> int:
    """`guess` tahmini, gizli kelime `answer` iken hangi deseni üretir?

    Tekrarlanan harfler gerçek Wordle kuralıyla işlenir:
      1. Önce doğru pozisyondaki harfler yeşil yapılır.
      2. Sonra kalan harfler soldan sağa gezilir. Harf, gizli kelimenin henüz
         eşleşmemiş harfleri arasında varsa sarı olur ve o kopya "kullanılır";
         yoksa gri kalır.
    Örnek: gizli KALEM, tahmin KAPAK -> K, A yeşil; P gri; ikinci A gri
    (KALEM'deki tek A yeşil olarak kullanıldı); son K gri.
    """
    colors = [GRAY] * WORD_LENGTH
    unmatched = Counter()
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i]:
            colors[i] = GREEN
        else:
            unmatched[answer[i]] += 1
    for i in range(WORD_LENGTH):
        if colors[i] == GRAY and unmatched[guess[i]] > 0:
            colors[i] = YELLOW
            unmatched[guess[i]] -= 1
    return encode_colors(colors)


def encode_colors(colors: Iterable[int]) -> int:
    """[2, 2, 0, 0, 0] gibi bir renk listesini desen sayısına çevirir."""
    return sum(color * power for color, power in zip(colors, _POWERS))


def decode_pattern(pattern: int) -> tuple[int, ...]:
    """Desen sayısını 5 renkten oluşan bir demete çevirir."""
    colors = []
    for _ in range(WORD_LENGTH):
        pattern, color = divmod(pattern, 3)
        colors.append(color)
    return tuple(colors)


def pattern_to_emoji(pattern: int) -> str:
    return "".join(_EMOJI[color] for color in decode_pattern(pattern))


def parse_pattern(text: str) -> int:
    """Kullanıcının yazdığı deseni sayıya çevirir.
    y = yeşil, s = sarı, g = gri (ya da 2, 1, 0). Örnek: "yysgg"."""
    text = text.strip().lower()
    if len(text) != WORD_LENGTH or any(ch not in _INPUT_CODES for ch in text):
        raise ValueError("Desen 5 karakter olmalı: y (yeşil), s (sarı), g (gri). Örnek: yysgg")
    return encode_colors(_INPUT_CODES[ch] for ch in text)


def is_consistent(word: str, history: History) -> bool:
    """`word` gizli kelime olsaydı şimdiye kadarki tüm geri bildirimler aynı mı çıkardı?"""
    return all(feedback(guess, word) == pattern for guess, pattern in history)


def filter_candidates(candidates: Iterable[str], guess: str, pattern: int) -> list[str]:
    """Bir tahminden sonra hâlâ gizli kelime olabilecek adayları döndürür.

    En basit ve tanım gereği doğru yöntem: her aday için geri bildirimi yeniden
    hesaplayıp gözlenen desenle karşılaştırmak. Hafta 8'deki hızlı yöntemler bu
    fonksiyonla aynı sonucu vermek zorundadır (testlerde kontrol edilir).
    """
    return [word for word in candidates if feedback(guess, word) == pattern]
