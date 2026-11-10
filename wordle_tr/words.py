"""Kelime listelerini yükleme ve sayısal kodlama."""

from pathlib import Path
from typing import Sequence

import numpy as np

from .alphabet import LETTER_INDEX, WORD_LENGTH, is_valid_word

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GUESSES_PATH = DATA_DIR / "guesses.txt"
ANSWERS_PATH = DATA_DIR / "answers.txt"


def load_words(path: Path) -> list[str]:
    """Her satırda bir kelime olan dosyayı okur. # ile başlayan satırlar yorumdur."""
    words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if not word or word.startswith("#"):
                continue
            if not is_valid_word(word):
                raise ValueError(f"Geçersiz kelime {word!r} ({path})")
            words.append(word)
    return words


def load_guesses() -> list[str]:
    """Tahmin olarak kabul edilen tüm kelimeler."""
    return load_words(GUESSES_PATH)


def load_answers() -> list[str]:
    """Gizli kelime olabilecek yaygın kelimeler (tahmin listesinin alt kümesi)."""
    return load_words(ANSWERS_PATH)


def encode(words: Sequence[str]) -> np.ndarray:
    """Kelimeleri (n, 5) boyutlu harf indeksi matrisine çevirir.
    Örnek: "kalem" -> [13, 0, 14, 5, 15]. numpy ile toplu hesap için kullanılır."""
    codes = np.empty((len(words), WORD_LENGTH), dtype=np.uint8)
    for row, word in enumerate(words):
        codes[row] = [LETTER_INDEX[ch] for ch in word]
    return codes
