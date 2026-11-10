"""Türk alfabesi ve Türkçeye özgü harf dönüşümleri.

Python'un str.lower() ve str.upper() fonksiyonları noktalı/noktasız i harflerini
Türkçe kurallarına göre çevirmez:
    "I".lower() == "i"     (doğrusu "ı")
    "i".upper() == "I"     (doğrusu "İ")
    "İ".lower() == "i̇"     (iki karakter: i + birleşen nokta, kelime 6 harfe çıkar!)
Bu modüldeki fonksiyonlar bu dönüşümleri doğru yapar.
"""

WORD_LENGTH = 5

# Türk alfabesinin 29 harfi, alfabe sırasıyla. Q, W, X yoktur.
ALPHABET = "abcçdefgğhıijklmnoöprsştuüvyz"
LETTER_INDEX = {letter: i for i, letter in enumerate(ALPHABET)}

_LOWER_SPECIAL = str.maketrans({"I": "ı", "İ": "i"})
_UPPER_SPECIAL = str.maketrans({"i": "İ", "ı": "I"})
# Şapkalı harfler (kâğıt, hâlâ) oyunda düz harf olarak yazılır.
_CIRCUMFLEX = str.maketrans({"â": "a", "î": "i", "û": "u"})


def to_lower(text: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir (I -> ı, İ -> i)."""
    return text.translate(_LOWER_SPECIAL).lower()


def to_upper(text: str) -> str:
    """Türkçe kurallarına göre büyük harfe çevirir (i -> İ, ı -> I)."""
    return text.translate(_UPPER_SPECIAL).upper()


def normalize(word: str) -> str:
    """Kelimeyi oyun biçimine getirir: baştaki/sondaki boşlukları atar,
    Türkçe küçük harfe çevirir ve şapkalı harfleri düz harfe çevirir."""
    return to_lower(word.strip()).translate(_CIRCUMFLEX)


def is_valid_word(word: str) -> bool:
    """Kelime 5 harfli mi ve yalnızca Türk alfabesinin küçük harflerinden mi oluşuyor?"""
    return len(word) == WORD_LENGTH and all(ch in LETTER_INDEX for ch in word)


def sort_key(word: str) -> list[int]:
    """Kelimeleri Türk alfabesi sırasına göre sıralamak için anahtar (ç, c'den sonra gelir)."""
    return [LETTER_INDEX[ch] for ch in word]
