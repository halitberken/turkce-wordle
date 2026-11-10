"""Hafta 7: Ajanları tüm gizli kelimelerde oynatıp karşılaştırır.

Kullanım:
  python scripts/evaluate.py                         # tüm ajanlar, tüm gizli kelimeler
  python scripts/evaluate.py --ajan harf             # tek ajan
  python scripts/evaluate.py --ornek 300             # hızlı deneme: rastgele 300 kelime
  python scripts/evaluate.py --filtre tablo          # Hafta 8'deki desen tablosu ile filtrele

Çıktılar: results/baselines.json, results/baselines.md, results/tahmin_dagilimi.png
"""

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wordle_tr.agents import AGENTS, make_agent  # noqa: E402
from wordle_tr.filters import filter_by_constraints, filter_by_feedback  # noqa: E402
from wordle_tr.pattern_table import PatternTable  # noqa: E402
from wordle_tr.simulate import evaluate  # noqa: E402
from wordle_tr.words import load_answers, load_guesses  # noqa: E402

RESULTS_DIR = ROOT / "results"
DISPLAY_NAMES = {"rastgele": "Rastgele", "harf_sikligi": "Harf sıklığı"}


def make_filter(name: str, guesses, answers):
    if name == "geri_bildirim":
        return filter_by_feedback
    if name == "kisit":
        return filter_by_constraints
    return PatternTable.build(guesses, answers).filter_words


def run_agent(name, answers, secrets, allowed, filter_fn, seeds):
    """Rastgele ajan için birden çok tohumla çalıştırıp ortalamasını alır."""
    runs = []
    for seed in (seeds if name == "rastgele" else [None]):
        summary, _ = evaluate(make_agent(name, seed), answers, secrets, allowed, filter_fn, progress=True)
        runs.append(summary)
    result = runs[0].as_dict()
    if len(runs) > 1:
        means = [r.mean_guesses for r in runs]
        rates = [r.solve_rate for r in runs]
        result.update({
            "tohumlar": list(seeds),
            "ortalama_tahmin": round(statistics.fmean(means), 4),
            "ortalama_tahmin_std": round(statistics.stdev(means), 4),
            "cozme_orani_6": round(statistics.fmean(rates), 4),
            "cozme_orani_6_std": round(statistics.stdev(rates), 4),
            "not": "dağılım ve en kötü kelimeler ilk tohumdan",
        })
    return result


def write_markdown(results, path, games, filter_name):
    lines = [
        f"# Temel ajan sonuçları ({games} gizli kelime, filtre: {filter_name})",
        "",
        "| Ajan | Ortalama tahmin | 6 tahminde çözme | En çok tahmin | Tahmin başına süre |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results:
        mean = f"{r['ortalama_tahmin']:.3f}"
        rate = f"%{100 * r['cozme_orani_6']:.1f}"
        if "ortalama_tahmin_std" in r:
            mean += f" ± {r['ortalama_tahmin_std']:.3f}"
            rate += f" ± {100 * r['cozme_orani_6_std']:.1f}"
        worst = max(int(k) for k in r["dagilim"])
        lines.append(f"| {r['ajan']} | {mean} | {rate} | {worst} | {r['tahmin_basina_ms']:.2f} ms |")
    lines += ["", "## Tahmin sayısı dağılımı", ""]
    for r in results:
        lines.append(f"- **{r['ajan']}**: " + ", ".join(f"{k} tahmin: {v}" for k, v in r["dagilim"].items()))
    lines += ["", "## En çok zorlanılan kelimeler", ""]
    for r in results:
        lines.append(f"- **{r['ajan']}**: " + ", ".join(f"{w} ({n})" for w, n in r["en_kotu_kelimeler"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_distribution(results, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib yüklü değil, grafik atlandı.")
        return
    max_guesses = max(int(k) for r in results for k in r["dagilim"])
    xs = list(range(1, max_guesses + 1))
    width = 0.8 / len(results)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for n, r in enumerate(results):
        total = r["oyun_sayisi"]
        ys = [100 * r["dagilim"].get(str(x), 0) / total for x in xs]
        name = DISPLAY_NAMES.get(r["ajan"], r["ajan"])
        ax.bar([x + (n - (len(results) - 1) / 2) * width for x in xs], ys, width,
               label=f"{name} (ort. {r['ortalama_tahmin']:.2f})".replace(".", ","))
    ax.axvline(6.5, color="gray", linestyle="--", linewidth=1)
    ax.text(6.6, ax.get_ylim()[1] * 0.9, "6 tahmin sınırı", color="gray")
    ax.set_xticks(xs)
    ax.set_xlabel("Kelimeyi bulmak için gereken tahmin sayısı")
    ax.set_ylabel("Oyunların yüzdesi (%)")
    ax.set_title("Temel ajanların tahmin sayısı dağılımı")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Grafik: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ajan", choices=list(AGENTS), action="append",
                        help="değerlendirilecek ajan (birden çok verilebilir; varsayılan: hepsi)")
    parser.add_argument("--ornek", type=int, help="tüm kelimeler yerine rastgele N gizli kelime")
    parser.add_argument("--filtre", choices=["geri_bildirim", "kisit", "tablo"], default="tablo")
    parser.add_argument("--tohum-sayisi", type=int, default=5, help="rastgele ajan için tekrar sayısı")
    args = parser.parse_args()

    guesses, answers = load_guesses(), load_answers()
    secrets = answers if args.ornek is None else random.Random(0).sample(answers, args.ornek)
    filter_fn = make_filter(args.filtre, guesses, answers)
    allowed = set(guesses)

    results = []
    for name in args.ajan or list(AGENTS):
        print(f"{name} ajanı değerlendiriliyor ({len(secrets)} kelime)...")
        results.append(run_agent(name, answers, secrets, allowed, filter_fn, range(args.tohum_sayisi)))
        r = results[-1]
        print(f"  ortalama {r['ortalama_tahmin']:.3f} tahmin, %{100 * r['cozme_orani_6']:.1f} çözme, "
              f"{r['tahmin_basina_ms']:.2f} ms/tahmin")

    RESULTS_DIR.mkdir(exist_ok=True)
    payload = {"gizli_kelime_sayisi": len(secrets), "filtre": args.filtre, "ajanlar": results}
    (RESULTS_DIR / "baselines.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(results, RESULTS_DIR / "baselines.md", len(secrets), args.filtre)
    plot_distribution(results, RESULTS_DIR / "tahmin_dagilimi.png")
    print(f"Sonuçlar: {RESULTS_DIR / 'baselines.md'}")


if __name__ == "__main__":
    main()
