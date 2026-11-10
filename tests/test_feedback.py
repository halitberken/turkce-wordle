import pytest

from wordle_tr.feedback import (ALL_GREEN, GRAY, GREEN, NUM_PATTERNS, YELLOW, decode_pattern, encode_colors,
                                feedback, filter_candidates, is_consistent, parse_pattern)

G, Y, X = GREEN, YELLOW, GRAY


@pytest.mark.parametrize("guess, answer, expected", [
    ("kalem", "kalem", (G, G, G, G, G)),
    ("kapak", "kalem", (G, G, X, X, X)),  # KALEM'de tek A ve tek K var, ikisi de yeşil olarak kullanıldı
    ("lamba", "kalem", (Y, G, Y, X, X)),
    ("kasap", "kapak", (G, G, X, G, Y)),
    ("akrep", "kalem", (Y, Y, X, G, X)),
    # Tekrarlanan harfler
    ("ekmek", "melek", (Y, X, Y, G, G)),  # ilk E sarı; MELEK'in diğer E'si yeşil olarak kullanıldı
    ("ekler", "kalem", (X, Y, G, G, X)),  # baştaki E gri: tek E zaten 4. pozisyonda yeşil
    ("tatlı", "otlak", (Y, Y, X, Y, X)),  # tek T var: ilk T sarı, ikinci T gri
    ("kekik", "kayak", (G, X, X, X, G)),  # iki K'nın ikisi de yeşil, ortadaki K gri
])
def test_known_patterns(guess, answer, expected):
    assert decode_pattern(feedback(guess, answer)) == expected


def test_pattern_encoding_round_trip():
    for pattern in range(NUM_PATTERNS):
        assert encode_colors(decode_pattern(pattern)) == pattern
    assert encode_colors([G] * 5) == ALL_GREEN == 242


def test_parse_pattern():
    assert parse_pattern("yygss") == encode_colors([G, G, X, Y, Y])
    assert parse_pattern("22011") == parse_pattern("yygss")
    with pytest.raises(ValueError):
        parse_pattern("yyg")
    with pytest.raises(ValueError):
        parse_pattern("yygsk")


def test_filter_keeps_answer_and_is_consistent(random_histories, answers):
    for answer, history in random_histories:
        candidates = answers
        for guess, pattern in history:
            candidates = filter_candidates(candidates, guess, pattern)
        assert answer in candidates
        assert all(is_consistent(w, history) for w in candidates)
