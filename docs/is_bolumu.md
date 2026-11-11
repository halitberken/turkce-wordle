# İş bölümü: Hafta 6-8

Her kişi bir haftanın işini baştan sona sahiplenir ve sunumda o bölümü anlatır. Haftalar birbirinin üzerine kurulu, sıra da bu bağımlılığı izliyor: veri → oyun ve ajanlar → hızlı filtreleme.

| Kişi | Hafta | Dosyalar | Zorluk |
| --- | --- | --- | --- |
| **Berken** | 8: Kısıt tabanlı filtreleme, CSP çözücü, desen tablosu, hız karşılaştırması | `wordle_tr/constraints.py`, `csp_solver.py`, `pattern_table.py`, `filters.py`, `scripts/benchmark_filters.py`, `tests/test_week8.py` | Zor |
| **Arda** | 7: Geri bildirim fonksiyonu, oyun ortamı, temel ajanlar, değerlendirme | `wordle_tr/feedback.py`, `game.py`, `agents/`, `simulate.py`, `scripts/evaluate.py`, `tests/test_feedback.py`, `test_game.py`, `test_agents.py` | Orta |
| **Faruk** | 6: Problem tanımı, literatür taraması, kelime listesi, terminal oyunu | `wordle_tr/alphabet.py`, `words.py`, `scripts/build_word_lists.py`, `word_stats.py`, `play.py`, `tests/test_alphabet.py` | Kolay-orta |

## Sunumdan önce herkesin yapması gerekenler

Her kişi kendi hafta belgesini okusun, kendi dosyalarını açıp aşağıdaki noktaları anlatabilecek kadar anlasın ve komutları kendi bilgisayarında çalıştırsın.

**Faruk** (`docs/hafta6_problem_tanimi_ve_literatur.md`)
- Problem tanımı tablosu: aday küme neden bir "inanç durumu"?
- `alphabet.to_lower` neden gerekli? (`"İ".lower()` 2 karakter üretiyor)
- Kelime listesinin 6 adımı ve sayılar: 140.026 girdi → 5.370 tahmin → 1.900 gizli kelime
- Literatür tablosu ve projenin katkısı (Türkçe)
- Komutlar: `python scripts/build_word_lists.py`, `python scripts/word_stats.py`
- Canlı demo: `python scripts/play.py oyna` ve `python scripts/play.py izle --kelime kalem`

**Arda** (`docs/hafta7_oyun_ortami_ve_temel_ajanlar.md`)
- `feedback()` fonksiyonunun iki geçişi ve tekrarlanan harf örnekleri (KAPAK/KALEM, EKLER/KALEM)
- Desen kodlaması: neden 243 desen ve neden 242 "kazandı"?
- Ajan arayüzü `choose_guess(gecmis, adaylar)` ve harf sıklığı puanı
- Sonuç tablosu, dağılım grafiği ve SAYMA örneği (hata analizi)
- Komutlar: `python scripts/evaluate.py`, `python -m pytest tests/test_feedback.py`

**Berken** (`docs/hafta8_kisitlar_ve_desen_tablosu.md`)
- Dört kısıt türü ve denklik kanıtı
- CSP modeli (değişkenler, alanlar, kısıtlar), trie, geri izleme ve ileri kontrol
- Desen tablosundaki sarı kuralı ve tam doğrulama (10,2 milyon hücre, 0 hata)
- Hız tablosu ve Hafta 9'a köprü (34 saniye yerine 0,05 saniye)
- Komutlar: `python scripts/benchmark_filters.py`, `python -m pytest tests/test_week8.py`

## Sonraki haftalar için öneri

| Hafta | Konu | Önerilen sorumlu |
| --- | --- | --- |
| 9 | Entropi ajanı | Arda (kendi ajan arayüzü + Berken'in desen tablosu) |
| 10 | Expectimax araması ve kesin çözücü (oracle) | Berken |
| 11 | Deneyler, karşılaştırma ve hata analizi | Faruk |
| 12 | Final raporu, sunum ve teslim | Herkes |
