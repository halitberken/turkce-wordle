from wordle_tr.alphabet import ALPHABET, is_valid_word, normalize, sort_key, to_lower, to_upper


def test_alphabet_has_29_turkish_letters():
    assert len(ALPHABET) == 29
    assert not set("qwx") & set(ALPHABET)


def test_turkish_case_conversion():
    assert to_upper("ılık") == "ILIK"
    assert to_upper("işçi") == "İŞÇİ"
    assert to_lower("IŞIK") == "ışık"
    assert to_lower("İNCİR") == "incir"
    assert len("İNCİR".lower()) == 7  # Python'un kendi lower() fonksiyonu bozuyor
    assert len(to_lower("İNCİR")) == 5


def test_normalize_removes_circumflex_and_spaces():
    assert normalize("  Kâğıt ") == "kağıt"
    assert normalize("hâlâ") == "hala"


def test_is_valid_word():
    assert is_valid_word("kalem")
    assert is_valid_word("çiçek")
    assert not is_valid_word("ağaç")    # 4 harf
    assert not is_valid_word("Kalem")   # büyük harf
    assert not is_valid_word("wordl")   # W Türk alfabesinde yok


def test_sort_key_follows_turkish_order():
    assert sorted(["çanta", "cadde", "dalga"], key=sort_key) == ["cadde", "çanta", "dalga"]


def test_word_lists_are_clean(guesses, answers):
    assert len(guesses) > 5000 and len(answers) > 1500
    assert all(is_valid_word(w) for w in guesses)
    assert set(answers) <= set(guesses)
    assert len(set(guesses)) == len(guesses)
    assert guesses == sorted(guesses, key=sort_key)
