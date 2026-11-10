# Türkçe Wordle Çözücü

BIL 4112 Yapay Zeka dönem projesi, Dokuz Eylül Üniversitesi. Ekip: Berken, Arda, Faruk.

Gizli 5 harfli Türkçe bir kelimeyi en az tahminle bulan yapay zeka ajanları geliştiriyor ve karşılaştırıyoruz: kısıt tabanlı aday filtreleme (CSP), bilgi teorisi (entropi) ve expectimax araması.

## Durum

| Hafta | Konu | Durum | Belge |
| --- | --- | --- | --- |
| 6 | Problem tanımı, literatür taraması, Türkçe kelime listesi | Tamam | [hafta6](docs/hafta6_problem_tanimi_ve_literatur.md) |
| 7 | Oyun ortamı, geri bildirim fonksiyonu, temel ajanlar | Tamam | [hafta7](docs/hafta7_oyun_ortami_ve_temel_ajanlar.md) |
| 8 | Kısıt tabanlı (CSP) aday filtreleme, desen tablosu | Tamam | [hafta8](docs/hafta8_kisitlar_ve_desen_tablosu.md) |
| 9 | Entropi tabanlı açgözlü ajan | Sırada | |
| 10 | Expectimax araması ve kesin çözücü (oracle) | | |
| 11 | Deneyler, karşılaştırma, hata analizi | | |
| 12 | Final raporu, sunum, teslim | | |

İş bölümü: [docs/is_bolumu.md](docs/is_bolumu.md)

## Kurulum

Python 3.10 veya üstü gerekir.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest            # 36 test, ~20 saniye
```

## Kullanım

```bash
python scripts/play.py oyna                        # terminalde Wordle oyna
python scripts/play.py izle --ajan harf --kelime kalem   # ajanın çözüşünü izle
python scripts/play.py yardimci                    # başka bir sitede oynarken ajandan öneri al
python scripts/evaluate.py                         # ajanları 1.900 kelimenin hepsinde değerlendir
python scripts/benchmark_filters.py                # filtreleme yöntemlerini karşılaştır
python scripts/build_word_lists.py                 # kelime listelerini yeniden üret
python scripts/word_stats.py                       # harf istatistikleri ve grafik
```

## İlk sonuçlar

Temel ajanlar, 1.900 gizli kelimenin hepsinde (`results/baselines.md`):

| Ajan | Ortalama tahmin | 6 tahminde çözme |
| --- | --- | --- |
| Rastgele aday (5 tohum) | 4,111 ± 0,014 | %98,3 |
| Harf sıklığı | 3,740 | %99,3 |

Aday filtreleme, 500 rastgele oyun durumu (`results/filters.md`). Dört yöntem her durumda aynı adayları buldu:

| Yöntem | Ortalama süre | Hızlanma |
| --- | --- | --- |
| Geri bildirimi yeniden hesapla | 8,1 ms | 1× |
| Kısıt kontrolü | 1,8 ms | 4,5× |
| CSP (trie + geri izleme + ileri kontrol) | 1,2 ms | 6,7× |
| Desen tablosu (numpy) | 0,03 ms | 298× |

## Klasör yapısı

```
wordle_tr/
  alphabet.py       Türk alfabesi, İ/ı dönüşümleri              (Faruk)
  words.py          kelime listelerini yükleme                  (Faruk)
  feedback.py       renk geri bildirimi, desen kodlaması         (Arda)
  game.py           oyun ortamı                                 (Arda)
  agents/           ajan arayüzü ve temel ajanlar                (Arda)
  simulate.py       oyun döngüsü ve değerlendirme                (Arda)
  constraints.py    geri bildirimden kısıtlar                   (Berken)
  csp_solver.py     trie + geri izleme + ileri kontrol           (Berken)
  pattern_table.py  önceden hesaplanmış desen tablosu            (Berken)
  filters.py        filtreleme yöntemleri tek arayüzde           (Berken)
scripts/            komut satırı betikleri
tests/              pytest testleri
data/
  guesses.txt       tahmin listesi (5.370 kelime)
  answers.txt       gizli kelime listesi (1.900 kelime)
  excluded_answers.txt  gizli listeden elle çıkarılanlar
  raw/              ham kaynak dosyalar
results/            deney çıktıları (json, md, png)
docs/               haftalık belgeler ve iş bölümü
```

## Veri kaynakları

- TDK Güncel Türkçe Sözlük'ten derlenmiş listeler: [CanNuhlar/Turkce-Kelime-Listesi](https://github.com/CanNuhlar/Turkce-Kelime-Listesi), [mertemin/turkish-word-list](https://github.com/mertemin/turkish-word-list)
- Kelime sıklığı: [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) (OpenSubtitles 2018, Türkçe)

Literatür taraması: [docs/hafta6_problem_tanimi_ve_literatur.md](docs/hafta6_problem_tanimi_ve_literatur.md)
