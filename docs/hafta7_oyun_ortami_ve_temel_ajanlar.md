# Hafta 7: Oyun ortamı, geri bildirim ve temel ajanlar

**Sorumlu:** Arda · **Kod:** `wordle_tr/feedback.py`, `wordle_tr/game.py`, `wordle_tr/agents/`, `wordle_tr/simulate.py`, `scripts/evaluate.py`

## 1. Geri bildirim fonksiyonu

`feedback(tahmin, gizli)` iki geçişte çalışır:

1. Doğru pozisyondaki harfler yeşil yapılır. Gizli kelimenin eşleşmeyen harfleri sayılır.
2. Kalan harfler soldan sağa gezilir. Harf, gizli kelimenin henüz kullanılmamış harfleri arasında varsa sarı olur ve o kopya kullanılır; yoksa gri kalır.

Zor kısım tekrarlanan harflerdir. Testlerdeki örnekler:

| Tahmin | Gizli | Desen | Neden |
| --- | --- | --- | --- |
| KAPAK | KALEM | 🟩🟩⬜⬜⬜ | KALEM'deki tek A ve tek K yeşil olarak kullanıldı, ikinci A ve son K gri |
| EKLER | KALEM | ⬜🟨🟩🟩⬜ | Baştaki E gri: tek E zaten 4. pozisyonda yeşil |
| TATLI | OTLAK | 🟨🟨⬜🟨⬜ | Tek T var: ilk T sarı, ikinci T gri |
| KEKİK | KAYAK | 🟩⬜⬜⬜🟩 | İki K'nın ikisi de yeşil, ortadaki K gri |

**Desen kodlaması:** 5 renk 3 tabanında tek bir sayıya çevrilir (gri 0, sarı 1, yeşil 2). 243 olası desen 0..242 arasındadır ve 242 "hepsi yeşil" demektir. Bu sayede Hafta 8'deki desen tablosu 1 baytlık hücrelerle saklanabiliyor.

## 2. Oyun ortamı

`WordleGame(gizli, izinli_tahminler, max_guesses=6)`:

- `play(tahmin)` deseni döndürür ve geçmişe ekler.
- Geçersiz tahmin (5 harfli değil, listede yok, oyun bitti) `InvalidGuessError` verir ve hak harcamaz.
- `max_guesses=None` ile oyun kelime bulunana kadar sürer. Deneylerde 6'yı aşan oyunları da ölçmek için kullanılır.

## 3. Ajan arayüzü

Her ajan tek bir fonksiyon yazar: `choose_guess(gecmis, adaylar) -> tahmin`. Aday listesini oyun döngüsü (`simulate.play_game`) günceller. Böylece Hafta 8'de filtreleme yöntemi değiştiğinde ajanlara dokunmak gerekmedi; Hafta 9 ve 10'daki ajanlar da aynı arayüzü kullanacak.

## 4. Temel ajanlar

- **Rastgele ajan:** Geri bildirimle tutarlı adaylardan rastgele birini seçer. 5 farklı tohumla çalıştırılıp ortalaması alınır.
- **Harf sıklığı ajanı:** Her adayın puanı, içindeki farklı harflerin kaç adayda geçtiğinin toplamıdır. En yüksek puanlı aday seçilir. İnsanların sezgisel stratejisine benzer ve deterministiktir. İlk tahmini her zaman ERİKA'dır.

## 5. Değerlendirme

`python scripts/evaluate.py` her ajanı 1.900 gizli kelimenin hepsinde bir kez oynatır. Oyun 6 tahminde kesilmez, böylece tam dağılım görülür.

| Ajan | Ortalama tahmin | 6 tahminde çözme | En çok tahmin | Tahmin başına süre |
| --- | --- | --- | --- | --- |
| Rastgele (5 tohum) | 4,111 ± 0,014 | %98,3 ± 0,3 | 8 | 0,04 ms |
| Harf sıklığı | 3,740 | %99,3 | 8 | 1,06 ms |

Tahmin sayısı dağılımı (`results/tahmin_dagilimi.png`):

| Tahmin sayısı | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Rastgele | 4 | 81 | 452 | 715 | 462 | 159 | 23 | 4 |
| Harf sıklığı | 1 | 95 | 691 | 805 | 242 | 52 | 12 | 2 |

**Hata analizi:** Harf sıklığı ajanının 6 tahminde bulamadığı 14 kelimenin çoğu tek harfle ayrılan kelime ailelerinden: SAYMA ve YAZMA 8 tahmin, SAVMA, KAZAK, KUŞAK 7 tahmin. SAYMA oyununda 4. tahminden sonra SA_MA kalıbı belli oluyor; ajan SAÇMA, SANMA, SAPMA, SAVMA'yı tek tek deniyor ve SAYMA'yı 8. tahminde buluyor:

| Tahmin | ERİKA | DOLMA | SITMA | SAÇMA | SANMA | SAPMA | SAVMA | SAYMA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kalan aday | 1.900 → 84 | 84 → 20 | 20 → 5 | 5 → 4 | 4 → 3 | 3 → 2 | 2 → 1 | bulundu |

Bu, yalnızca adaylardan tahmin yapmanın sınırıdır. Hafta 9'daki entropi ajanı burada Ç, N, P, V, Y harflerinin birkaçını aynı anda deneyen, aday olmayan bir kelime seçerek bu tuzaktan çıkabilir.

## Komutlar

```bash
python scripts/evaluate.py                 # tüm ajanlar, 1.900 kelime (~10 saniye)
python scripts/evaluate.py --ornek 300     # hızlı deneme
python scripts/play.py izle --ajan harf --kelime sayma
```
