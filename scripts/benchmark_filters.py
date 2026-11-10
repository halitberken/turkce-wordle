"""Hafta 8: Aday filtreleme yöntemlerini doğruluk ve hız açısından karşılaştırır.

Rastgele oyun durumları üretilir (rastgele gizli kelime + 1-3 rastgele tahmin) ve her
durumda tüm gizli kelime listesi dört yöntemle filtrelenir:
  1. geri bildirim: her aday için feedback() yeniden hesaplanır (referans)
  2. kısıt:         geçmiş kısıtlara çevrilir, her aday kontrol edilir
  3. CSP:           kısıtlarla sözlük ağacında geri izleme + ileri kontrol
  4. desen tablosu: önceden hesaplanmış tablodan vektör karşılaştırması
Dört yöntem her durumda aynı kelime kümesini vermelidir.

Ayrıca --uctan-uca ile harf sıklığı ajanı tüm gizli kelimelerde her filtreyle oynatılır;
böylece filtrelemenin bütün bir değerlendirmeyi ne kadar hızlandırdığı görülür.

Kullanım:
  python scripts/benchmark_filters.py                  # 500 durum
  python scripts/benchmark_filters.py --tam-dogrulama  # tablonun 10 milyon hücresini tek tek doğrula
  python scripts/benchmark_filters.py --uctan-uca      # tam değerlendirme süreleri (~1 dakika)

Çıktılar: results/filters.json, results/filters.md
"""

import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wordle_tr.agents import LetterFrequencyAgent  # noqa: E402
from wordle_tr.constraints import Constraints  # noqa: E402
from wordle_tr.csp_solver import CSPSolver  # noqa: E402
from wordle_tr.feedback import feedback, is_consistent  # noqa: E402
from wordle_tr.filters import filter_by_constraints, filter_by_feedback  # noqa: E402
from wordle_tr.pattern_table import PatternTable, compute_pattern_matrix  # noqa: E402
from wordle_tr.simulate import evaluate  # noqa: E402
from wordle_tr.words import encode, load_answers, load_guesses  # noqa: E402

RESULTS_DIR = ROOT / "results"


def random_states(guesses, answers, count, rng):
    states = []
    for _ in range(count):
        answer = rng.choice(answers)
        history = [(g, feedback(g, answer)) for g in rng.sample(guesses, rng.randint(1, 3))]
        states.append(history)
    return states


def timed(fn, repeat):
    """fn'yi `repeat` kez çalıştırır, sonucu ve çağrı başına süreyi (µs) döndürür."""
    start = time.perf_counter()
    for _ in range(repeat):
        result = fn()
    return result, 1e6 * (time.perf_counter() - start) / repeat


def full_verification(table):
    """Tablonun her hücresini skaler feedback() ile karşılaştırır (birkaç dakika sürebilir)."""
    mismatches = 0
    for g, guess in enumerate(table.guesses):
        row = table.matrix[g]
        for a, answer in enumerate(table.answers):
            if row[a] != feedback(guess, answer):
                mismatches += 1
        if (g + 1) % 1000 == 0:
            print(f"  {g + 1}/{len(table.guesses)} tahmin satırı doğrulandı", flush=True)
    return mismatches


def end_to_end(guesses, answers, table):
    """Harf sıklığı ajanını tüm gizli kelimelerde her filtreyle oynatır."""
    rows = {}
    for name, filter_fn in [("geri_bildirim", filter_by_feedback), ("kisit", filter_by_constraints),
                            ("desen_tablosu", table.filter_words)]:
        print(f"  {name} filtresiyle {len(answers)} oyun...", flush=True)
        start = time.perf_counter()
        summary, results = evaluate(LetterFrequencyAgent(), answers, allowed_guesses=set(guesses),
                                    filter_fn=filter_fn)
        moves = sum(r.num_guesses for r in results)
        rows[name] = {
            "toplam_saniye": round(time.perf_counter() - start, 2),
            "filtre_ms_tahmin_basina": round(1000 * sum(r.filter_seconds for r in results) / moves, 3),
            "ortalama_tahmin": round(summary.mean_guesses, 4),
        }
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--durum", type=int, default=500, help="rastgele oyun durumu sayısı")
    parser.add_argument("--tekrar", type=int, default=3, help="süre ölçümü için tekrar sayısı")
    parser.add_argument("--tam-dogrulama", action="store_true", help="tablonun tüm hücrelerini doğrula")
    parser.add_argument("--uctan-uca", action="store_true", help="tam değerlendirmeyi her filtreyle ölç")
    args = parser.parse_args()

    guesses, answers = load_guesses(), load_answers()
    rng = random.Random(42)

    print("Desen tablosu hesaplanıyor (önbellek kullanılmadan)...")
    start = time.perf_counter()
    matrix = compute_pattern_matrix(encode(guesses), encode(answers))
    build_seconds = time.perf_counter() - start
    table = PatternTable(guesses, answers, matrix)
    print(f"  {matrix.shape[0]:,} × {matrix.shape[1]:,} = {matrix.size:,} hücre, "
          f"{matrix.nbytes / 1e6:.1f} MB, {build_seconds:.2f} s")

    sample_pairs = [(rng.choice(guesses), rng.choice(answers)) for _ in range(200_000)]
    sample_mismatches = sum(table.pattern(g, a) != feedback(g, a) for g, a in sample_pairs)
    print(f"  Rastgele 200.000 çiftte skaler fonksiyonla uyuşmayan: {sample_mismatches}")
    full_mismatches = None
    if args.tam_dogrulama:
        print("Tam doğrulama...")
        full_mismatches = full_verification(table)
        print(f"  Uyuşmayan hücre: {full_mismatches}")

    solver = CSPSolver(answers)
    all_ids = table.all_ids()
    times = {"geri_bildirim": [], "kisit": [], "csp": [], "desen_tablosu": []}
    csp_nodes, sizes = [], []
    disagreements = 0

    print(f"{args.durum} rastgele oyun durumunda filtreleme karşılaştırılıyor...")
    for history in random_states(guesses, answers, args.durum, rng):
        reference, t = timed(lambda: [w for w in answers if is_consistent(w, history)], args.tekrar)
        times["geri_bildirim"].append(t)

        def by_constraints():
            constraints = Constraints.from_history(history)
            return [w for w in answers if constraints.is_satisfied(w)]
        constrained, t = timed(by_constraints, args.tekrar)
        times["kisit"].append(t)

        solved, t = timed(lambda: solver.solve(Constraints.from_history(history)), args.tekrar)
        times["csp"].append(t)
        csp_nodes.append(solved.stats.nodes_visited)

        def by_table():
            ids = all_ids
            for guess, pattern in history:
                ids = table.filter_ids(ids, guess, pattern)
            return ids
        ids, t = timed(by_table, args.tekrar)
        times["desen_tablosu"].append(t)

        expected = set(reference)
        results = (set(constrained), set(solved.words), {answers[i] for i in ids})
        disagreements += sum(result != expected for result in results)
        sizes.append(len(expected))

    summary = {
        "tablo": {
            "tahmin_sayisi": len(guesses),
            "gizli_kelime_sayisi": len(answers),
            "hucre_sayisi": int(matrix.size),
            "boyut_mb": round(matrix.nbytes / 1e6, 2),
            "hesaplama_saniye": round(build_seconds, 3),
            "ornek_dogrulama_cift": len(sample_pairs),
            "ornek_dogrulama_uyusmayan": int(sample_mismatches),
            "tam_dogrulama_uyusmayan": full_mismatches,
        },
        "durum_sayisi": args.durum,
        "uyusmazlik": disagreements,
        "ortalama_kalan_aday": round(statistics.fmean(sizes), 1),
        "medyan_kalan_aday": statistics.median(sizes),
        "trie_dugum_sayisi": solver.trie.node_count,
        "csp_ortalama_genisletilen_dugum": round(statistics.fmean(csp_nodes), 1),
        "sure_mikrosaniye": {
            name: {"ortalama": round(statistics.fmean(v), 1), "medyan": round(statistics.median(v), 1)}
            for name, v in times.items()
        },
    }
    base = summary["sure_mikrosaniye"]["geri_bildirim"]["ortalama"]
    for name, value in summary["sure_mikrosaniye"].items():
        value["hizlanma"] = round(base / value["ortalama"], 1)
    if args.uctan_uca:
        print("Uçtan uca değerlendirme süreleri ölçülüyor...")
        summary["uctan_uca"] = end_to_end(guesses, answers, table)

    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "filters.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    labels = {"geri_bildirim": "Geri bildirimi yeniden hesapla (referans)", "kisit": "Kısıt kontrolü",
              "csp": "CSP: trie + geri izleme + ileri kontrol", "desen_tablosu": "Desen tablosu (numpy)"}
    lines = [
        f"# Aday filtreleme karşılaştırması ({args.durum} rastgele oyun durumu)",
        "",
        f"Dört yöntem {args.durum} durumun hepsinde aynı aday kümesini verdi mi: "
        f"{'evet' if disagreements == 0 else f'HAYIR, {disagreements} uyuşmazlık'}.",
        f"Bir durumda ortalama {summary['ortalama_kalan_aday']} aday kaldı "
        f"(medyan {summary['medyan_kalan_aday']}).",
        "",
        "| Yöntem | Ortalama süre (µs) | Medyan süre (µs) | Hızlanma |",
        "| --- | --- | --- | --- |",
    ]
    for name, value in summary["sure_mikrosaniye"].items():
        lines.append(f"| {labels[name]} | {value['ortalama']:,.1f} | {value['medyan']:,.1f} | {value['hizlanma']}× |")
    lines += [
        "",
        f"CSP araması ortalama {summary['csp_ortalama_genisletilen_dugum']} trie düğümü genişletti "
        f"(ağaçta toplam {solver.trie.node_count:,} düğüm var).",
        "",
        f"Desen tablosu: {matrix.shape[0]:,} × {matrix.shape[1]:,} = {matrix.size:,} hücre, "
        f"{summary['tablo']['boyut_mb']} MB, hesaplama {build_seconds:.2f} s. "
        f"Rastgele {len(sample_pairs):,} çiftte uyuşmayan: {sample_mismatches}"
        + (f"; tüm hücrelerde uyuşmayan: {full_mismatches}." if full_mismatches is not None else "."),
    ]
    if "uctan_uca" in summary:
        lines += [
            "",
            f"## Uçtan uca: harf sıklığı ajanı, {len(answers):,} oyun",
            "",
            "| Filtre | Toplam süre (s) | Filtre süresi / tahmin (ms) | Ortalama tahmin |",
            "| --- | --- | --- | --- |",
        ]
        for name, row in summary["uctan_uca"].items():
            lines.append(f"| {labels[name]} | {row['toplam_saniye']} | {row['filtre_ms_tahmin_basina']} "
                         f"| {row['ortalama_tahmin']} |")
    (RESULTS_DIR / "filters.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
