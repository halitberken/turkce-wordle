"""Hafta 6: Kelime listelerinin istatistikleri.

Kullanım:
  python scripts/word_stats.py

Çıktılar: results/word_stats.json, results/harf_sikligi.png
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wordle_tr.alphabet import ALPHABET, WORD_LENGTH, to_upper  # noqa: E402
from wordle_tr.words import load_answers, load_guesses  # noqa: E402

RESULTS_DIR = ROOT / "results"
VOWELS = set("aeıioöuü")


def letter_coverage(words):
    """Her harf, kelimelerin yüzde kaçında geçiyor?"""
    counts = Counter()
    for word in words:
        counts.update(set(word))
    return {letter: counts[letter] / len(words) for letter in ALPHABET}


def best_openers(guesses, answers, count=10):
    """Gizli kelimelerde en yaygın farklı harfleri kapsayan açılış kelimeleri."""
    coverage = letter_coverage(answers)
    scored = sorted(guesses, key=lambda w: -sum(coverage[ch] for ch in set(w)))
    return [(w, round(sum(coverage[ch] for ch in set(w)), 3)) for w in scored[:count]]


def main():
    guesses, answers = load_guesses(), load_answers()
    coverage = letter_coverage(answers)
    positional = [Counter(word[i] for word in answers) for i in range(WORD_LENGTH)]
    stats = {
        "tahmin_kelimesi": len(guesses),
        "gizli_kelime": len(answers),
        "tekrarlanan_harfli_gizli_kelime_orani": round(sum(len(set(w)) < WORD_LENGTH for w in answers) / len(answers), 4),
        "unlu_sayisi_dagilimi": dict(sorted(Counter(sum(ch in VOWELS for ch in w) for w in answers).items())),
        "harf_kapsama": {to_upper(l): round(v, 4) for l, v in sorted(coverage.items(), key=lambda x: -x[1])},
        "pozisyona_gore_en_sik_harfler": [
            [(to_upper(l), c) for l, c in positional[i].most_common(5)] for i in range(WORD_LENGTH)
        ],
        "harf_kapsamina_gore_en_iyi_acilis": best_openers(guesses, answers),
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "word_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Tahmin kelimesi: {len(guesses):,}   Gizli kelime: {len(answers):,}")
    print(f"Tekrarlanan harf içeren gizli kelimeler: %{100 * stats['tekrarlanan_harfli_gizli_kelime_orani']:.1f}")
    print("En yaygın harfler (gizli kelimelerin yüzde kaçında geçiyor):")
    for letter, value in list(stats["harf_kapsama"].items())[:10]:
        print(f"  {letter}: %{100 * value:.1f}")
    print("Harf kapsamına göre en iyi açılış kelimeleri:",
          ", ".join(to_upper(w) for w, _ in stats["harf_kapsamina_gore_en_iyi_acilis"]))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib yüklü değil, grafik atlandı.")
        return
    ordered = sorted(coverage.items(), key=lambda item: -item[1])
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar([to_upper(l) for l, _ in ordered], [100 * v for _, v in ordered],
           color=["#c9a227" if l in VOWELS else "#4a7c59" for l, _ in ordered])
    ax.set_ylabel("Gizli kelimelerin yüzdesi (%)")
    ax.set_title(f"Harflerin {len(answers):,} gizli kelimede geçme oranı (sarı: ünlü)".replace(",", "."))
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "harf_sikligi.png", dpi=150)
    print(f"Grafik: {RESULTS_DIR / 'harf_sikligi.png'}")


if __name__ == "__main__":
    main()
