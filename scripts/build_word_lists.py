"""Hafta 6: Türkçe 5 harfli kelime listelerini oluşturur.

Kaynaklar data/raw/ altında saklanır; dosya yoksa indirilir:
  - TDK Güncel Türkçe Sözlük'ten derlenmiş iki açık kelime listesi (sözlük)
  - OpenSubtitles 2018 Türkçe kelime sıklık listesi, ilk 50.000 kelime (yaygınlık)

Çıktılar:
  data/guesses.txt      tahmin olarak kabul edilen tüm kelimeler
  data/answers.txt      gizli kelime olabilecek yaygın kelimeler
  data/frequencies.tsv  gizli kelimelerin altyazı derlemindeki geçiş sayısı

Kullanım:
  python scripts/build_word_lists.py
"""

import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wordle_tr.alphabet import WORD_LENGTH, is_valid_word, normalize, sort_key  # noqa: E402
from wordle_tr.words import ANSWERS_PATH, DATA_DIR, GUESSES_PATH  # noqa: E402

RAW_DIR = DATA_DIR / "raw"
EXCLUDED_PATH = DATA_DIR / "excluded_answers.txt"
FREQUENCIES_PATH = DATA_DIR / "frequencies.tsv"

DICTIONARY_SOURCES = {
    "tdk_cannuhlar.txt":
        "https://raw.githubusercontent.com/CanNuhlar/Turkce-Kelime-Listesi/master/turkce_kelime_listesi.txt",
    "tdk_mertemin.txt":
        "https://raw.githubusercontent.com/mertemin/turkish-word-list/master/words.txt",
}
FREQUENCY_SOURCE = (
    "opensubtitles_tr_50k.txt",
    "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/tr/tr_50k.txt",
)


def ensure_downloaded(name: str, url: str) -> Path:
    path = RAW_DIR / name
    if not path.exists():
        print(f"İndiriliyor: {url}")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return path


def read_lines(path: Path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def dictionary_words(stats: Counter) -> set[str]:
    """Sözlük listelerinden geçerli 5 harfli kelimeleri çıkarır ve neden elendiklerini sayar."""
    words = set()
    for name, url in DICTIONARY_SOURCES.items():
        for entry in read_lines(ensure_downloaded(name, url)):
            entry = entry.strip()
            stats["sözlük girdisi"] += 1
            if not entry:
                continue
            if entry[0].isupper():
                stats["özel isim (büyük harfle başlıyor)"] += 1
                continue
            if any(ch in entry for ch in " -'./"):
                stats["birden çok kelime ya da noktalama"] += 1
                continue
            word = normalize(entry)
            if len(word) != WORD_LENGTH:
                stats["5 harfli değil"] += 1
                continue
            if not is_valid_word(word):
                stats["Türk alfabesinde olmayan harf (q, w, x...)"] += 1
                continue
            if word != entry:
                stats["şapkalı harf düzeltildi (â, î, û)"] += 1
            words.add(word)
    return words


def subtitle_frequencies() -> Counter:
    """Altyazı derlemindeki kelime sıklıkları (şapkalı yazımlar birleştirilir)."""
    frequencies = Counter()
    for line in read_lines(ensure_downloaded(*FREQUENCY_SOURCE)):
        word, count = line.rsplit(" ", 1)
        frequencies[normalize(word)] += int(count)
    return frequencies


def load_excluded() -> set[str]:
    if not EXCLUDED_PATH.exists():
        return set()
    return {normalize(line) for line in read_lines(EXCLUDED_PATH)
            if line.strip() and not line.startswith("#")}


def write_words(path: Path, words: list[str], header: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {header}\n")
        f.writelines(word + "\n" for word in words)


def main() -> None:
    stats = Counter()
    guesses = sorted(dictionary_words(stats), key=sort_key)

    frequencies = subtitle_frequencies()
    excluded = load_excluded()
    common = [word for word in guesses if frequencies[word] > 0]
    answers = [word for word in common if word not in excluded]

    write_words(GUESSES_PATH, guesses,
                f"Tahmin olarak kabul edilen 5 harfli kelimeler ({len(guesses)} kelime). "
                "scripts/build_word_lists.py ile üretildi.")
    write_words(ANSWERS_PATH, answers,
                f"Gizli kelime olabilecek yaygın kelimeler ({len(answers)} kelime). "
                "scripts/build_word_lists.py ile üretildi.")
    with open(FREQUENCIES_PATH, "w", encoding="utf-8") as f:
        f.write("kelime\taltyazi_sikligi\n")
        for word in sorted(answers, key=lambda w: -frequencies[w]):
            f.write(f"{word}\t{frequencies[word]}\n")

    print("Sözlük temizleme:")
    for reason, count in stats.most_common():
        print(f"  {reason:45s} {count:>7,}")
    print(f"\nTahmin listesi (5 harfli sözlük kelimeleri): {len(guesses):,}")
    print(f"Altyazı derleminin ilk 50.000 kelimesinde geçenler: {len(common):,}")
    print(f"Elle çıkarılan uygunsuz kelimeler:            {len(common) - len(answers):,}")
    print(f"Gizli kelime listesi:                          {len(answers):,}")


if __name__ == "__main__":
    main()
