# Hafta 6: Problem tanımı, literatür taraması ve kelime listesi

**Sorumlu:** Faruk · **Kod:** `wordle_tr/alphabet.py`, `wordle_tr/words.py`, `scripts/build_word_lists.py`, `scripts/word_stats.py`, `scripts/play.py`

## 1. Problem tanımı

Ajan, gizli 5 harfli Türkçe bir kelimeyi en fazla 6 tahminde bulmaya çalışır. Her tahminden sonra her harf için bir renk görür:

- **Yeşil:** harf doğru pozisyonda
- **Sarı:** harf kelimede var ama başka pozisyonda
- **Gri:** harf kelimede yok (ya da kelimedeki tüm kopyaları zaten işaretlendi)

**Formal model**

| Kavram | Bizim projede |
| --- | --- |
| Gizli kelime | s ∈ A, A = gizli kelime listesi (1.900 kelime), düzgün dağılımlı varsayılır |
| Eylem | Tahmin g ∈ G, G = tahmin listesi (5.370 kelime), A ⊆ G |
| Gözlem | Desen p = f(g, s), 3^5 = 243 olası renk kombinasyonundan biri |
| Bilgi durumu | Aday küme C_t = {w ∈ A : her i ≤ t için f(g_i, w) = p_i}, başta C_0 = A |
| Geçiş | C_{t+1} = {w ∈ C_t : f(g_{t+1}, w) = p_{t+1}} |
| Amaç | Beklenen tahmin sayısını en aza indirmek; ikincil ölçüt 6 tahminde çözme oranı |

Ajan gizli kelimeyi göremez ama gözlemler deterministiktir. Aday küme, ajanın gizli kelime hakkındaki **inanç durumudur** (belief state). Bu yüzden problem kısmi gözlemlenebilir bir karar problemi (POMDP) olarak da görülebilir. Proje dersin şu konularına dokunur:

- **Kısıt sağlama (CSP):** geri bildirimlerle tutarlı adayları bulmak (Hafta 8)
- **Olasılık ve bilgi teorisi:** en çok bilgi veren tahmini seçmek, entropi (Hafta 9)
- **Arama:** ajanın tahmini, geri bildirimin bir "şans" düğümü olduğu expectimax (Hafta 10)

**Girdi ve çıktı örneği** (harf sıklığı ajanı, gizli kelime KALEM):

| Tahmin | Desen | Kalan aday |
| --- | --- | --- |
| ERİKA | 🟨⬜⬜🟨🟨 | 1.900 → 17 |
| KEMAN | 🟩🟨🟨🟨⬜ | 17 → 2 |
| KADEM | 🟩🟩⬜🟩🟩 | 2 → 1 |
| KALEM | 🟩🟩🟩🟩🟩 | bulundu |

## 2. Türkçeye özgü zorluklar

- **Alfabe:** 29 harf. Ç, Ğ, I, İ, Ö, Ş, Ü var; Q, W, X yok.
- **Büyük/küçük harf:** Python'da `"İ".lower()` iki karakter (`i` + birleşen nokta) üretir ve kelime 6 harfe çıkar; `"i".upper()` ise `"I"` verir. `alphabet.py` bu dönüşümleri Türkçe kurallarıyla yapar.
- **Şapkalı harfler:** kâğıt, hâlâ gibi yazımlar düz harfe çevrilir (176 kelime).
- **Harf dağılımı farklı:** A, gizli kelimelerin %52'sinde geçer. İngilizce Wordle için bulunan en iyi açılış kelimeleri burada geçersizdir.
- **Eklemeli dil, benzer kelimeler:** SAÇMA, SANMA, SAPMA, SAVMA, SAYMA gibi tek harfle ayrılan kelime aileleri çok. Basit ajanlar bunları tek tek denemek zorunda kalıyor (Hafta 7 sonuçları).
- **Tekrarlanan harf:** gizli kelimelerin %42,5'inde en az bir harf tekrar ediyor (KAPAK, KEKİK). Geri bildirim kuralı bu yüzden dikkat istiyor.

## 3. Veri seti

| Kaynak | Ne için | Boyut |
| --- | --- | --- |
| [CanNuhlar/Turkce-Kelime-Listesi](https://github.com/CanNuhlar/Turkce-Kelime-Listesi) (TDK Güncel Türkçe Sözlük'ten) | Geçerli kelimeler | 76.186 satır |
| [mertemin/turkish-word-list](https://github.com/mertemin/turkish-word-list) (TDK'den) | Geçerli kelimeler | 63.839 satır |
| [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords), OpenSubtitles 2018 Türkçe, ilk 50.000 kelime | Kelimenin yaygın olup olmadığı | 50.000 kelime |

`scripts/build_word_lists.py` şu adımları uygular:

1. İki sözlük listesindeki 140.026 girdi okunur.
2. Büyük harfle başlayan özel isimler (4.978), birden çok kelimeli ya da noktalamalı girdiler (28.293) ve 5 harfli olmayanlar (96.127) atılır. Şapkalı harfler düzeltilir.
3. Kalan **5.370 kelime tahmin listesidir** (`data/guesses.txt`).
4. Bunlardan altyazı derleminin ilk 50.000 kelimesinde geçen 1.907 kelime "yaygın" sayılır.
5. Küfür, cinsel içerik ya da bir gruba yönelik aşağılayıcı kullanımı olan 7 kelime elle çıkarılır (`data/excluded_answers.txt`).
6. Kalan **1.900 kelime gizli kelime listesidir** (`data/answers.txt`).

**Kelime istatistikleri** (`python scripts/word_stats.py`, grafik `results/harf_sikligi.png`)

- En yaygın harfler (gizli kelimelerin yüzde kaçında geçtiği): A %52,0 · E %34,1 · K %32,0 · İ %29,5 · R %29,1 · M %24,2 · L %23,8 · N %23,4
- Harf kapsamına göre en iyi açılışlar: ERİKA, AKEMİ, İKAME, KAİME, KAMER, KREMA, MARKE, MERAK

## 4. Literatür taraması

| Çalışma | Ne yapıyor | Bizim projeyle ilişkisi |
| --- | --- | --- |
| G. Sanderson (3Blue1Brown), [*Solving Wordle using information theory*](https://www.youtube.com/watch?v=v68zYyaEmEA), 6 Şubat 2022 | Her tahmin için beklenen bilgi kazancını (entropi) hesaplayıp en yükseğini seçen bir çözücü kuruyor; kelime yaygınlığını da hesaba katıyor | Hafta 9'daki entropi ajanının temeli |
| A. Selby, [*The best strategies for Wordle*](http://sonorouschocolate.com/notes/index.php?title=The_best_strategies_for_Wordle), 2022 | İngilizce Wordle'ı (2.315 gizli, 12.972 tahmin kelimesi) tam olarak çözüyor: SALET ile ortalama 3,4212 tahmin, zor modda 3,5084 | Ulaşılabilecek en iyi sonuç için referans |
| D. Bertsimas, A. Paskov, [*An Exact Solution to Wordle*](https://ideas.repec.org/a/inm/oropre/v73y2025i3p1384-1394.html), Operations Research 73(3), 2025 | Bellman denklemiyle kesin dinamik programlama; SALET ile ortalama 3,421, her kelime en fazla 5 tahminde | Hafta 10'daki kesin çözücünün (oracle) yöntemi |
| D. Lokshtanov, B. Subercaseaux, [*Wordle Is NP-Hard*](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FUN.2022.19), FUN 2022 | Belli sayıda tahminde kazanmayı garanti etmenin genel durumda NP-zor olduğunu kanıtlıyor | Büyük listede tam arama yerine sezgisel ve derinliği sınırlı arama kullanmamızın gerekçesi |
| S. Bhambri, A. Bhattacharjee, D. Bertsekas, [*Reinforcement Learning Methods for Wordle: A POMDP/Adaptive Control Approach*](https://arxiv.org/abs/2211.10298), 2022 | Wordle'ı POMDP olarak modelliyor; bilgi kazancı sezgiselinin üzerine "rollout" ekleyerek optimuma %0,4 yaklaşıyor | İleriye bakmanın (expectimax) sezgiseli iyileştirdiğine dair kanıt |
| R. I. Greenberg, [*Effective Wordle Heuristics*](https://arxiv.org/abs/2408.11730), 2024 | Adayları en çok gruba bölen tahmini seçen basit sezgisel, 2.315 kelimede yaklaşık 3,46 ortalama | Entropiye hızlı bir alternatif ölçüt |
| S. Russell, P. Norvig, *Artificial Intelligence: A Modern Approach*, 4. baskı, 2020 | Bölüm 5 (oyunlar, expectiminimax) ve Bölüm 6 (kısıt sağlama problemleri) | Kullandığımız yöntemlerin ders kitabı tanımları |

**Boşluk:** Bulabildiğimiz çalışmaların neredeyse hepsi İngilizce Wordle üzerine. Kısa bir web taramasında Türkçe Wordle için yöntemleri sistematik olarak karşılaştıran bir çalışmaya rastlamadık. Türkçe veriyle karşılaştırma bu projenin katkısıdır.
