"""Wordle oyun ortamı."""

from typing import Collection, Optional

from .alphabet import is_valid_word, normalize
from .feedback import ALL_GREEN, feedback

MAX_GUESSES = 6


class InvalidGuessError(ValueError):
    """Geçersiz tahmin: 5 harfli değil, kelime listesinde yok ya da oyun bitti."""


class WordleGame:
    """Tek bir Wordle oyunu.

    allowed_guesses verilirse yalnızca bu kelimeler tahmin edilebilir (hız için set verin).
    max_guesses=None verilirse oyun kelime bulunana kadar sürer; deneylerde ajanların
    6 tahmini aşan oyunlarını da ölçmek için kullanılır.
    """

    def __init__(self, answer: str, allowed_guesses: Optional[Collection[str]] = None,
                 max_guesses: Optional[int] = MAX_GUESSES):
        answer = normalize(answer)
        if not is_valid_word(answer):
            raise ValueError(f"Gizli kelime geçersiz: {answer!r}")
        self.answer = answer
        self.allowed_guesses = allowed_guesses
        self.max_guesses = max_guesses
        self.history: list[tuple[str, int]] = []

    @property
    def guesses_used(self) -> int:
        return len(self.history)

    @property
    def won(self) -> bool:
        return bool(self.history) and self.history[-1][1] == ALL_GREEN

    @property
    def over(self) -> bool:
        out_of_guesses = self.max_guesses is not None and self.guesses_used >= self.max_guesses
        return self.won or out_of_guesses

    def play(self, guess: str) -> int:
        """Tahmini yapar, geçmişe ekler ve renk desenini döndürür."""
        if self.over:
            raise InvalidGuessError("Oyun bitti.")
        guess = normalize(guess)
        if not is_valid_word(guess):
            raise InvalidGuessError(f"'{guess}' 5 harfli bir Türkçe kelime değil.")
        if self.allowed_guesses is not None and guess not in self.allowed_guesses:
            raise InvalidGuessError(f"'{guess}' kelime listesinde yok.")
        pattern = feedback(guess, self.answer)
        self.history.append((guess, pattern))
        return pattern
