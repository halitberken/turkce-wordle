# Hafta 8: Kısıt tabanlı aday filtreleme ve desen tablosu

**Sorumlu:** Berken · **Kod:** `wordle_tr/constraints.py`, `wordle_tr/csp_solver.py`, `wordle_tr/pattern_table.py`, `wordle_tr/filters.py`, `scripts/benchmark_filters.py`

## 1. Neden önemli?

Her tahminden sonra "hâlâ gizli kelime olabilecek" adayları bulmamız gerekiyor. Hafta 7'de bunu en basit yolla yaptık: her aday için geri bildirimi yeniden hesaplayıp gözlenen desenle karşılaştırdık. Bu doğru ama yavaş.

Asıl ihtiyaç Hafta 9'da ortaya çıkacak: entropi ajanı her turda 5.370 olası tahminin her biri için adayların hangi desenlere bölündüğünü hesaplamalı. İlk turda bu 5.370 × 1.900 ≈ 10,2 milyon geri bildirim hesabı demek. Python'da tek hesap yaklaşık 3,4 µs sürdüğü için bu yaklaşık **34 saniye** eder. Desen tablosuyla aynı iş **0,05 saniye** sürüyor.

## 2. Geri bildirimden kısıtlara

Bir (tahmin, desen) gözlemi dört tür kısıt üretir:

| Kısıt | Kural | KAPAK → KALEM örneği |
| --- | --- | --- |
| Sabit harf | Yeşil harf o pozisyonda kesin | 1. harf K, 2. harf A |
| Yasak harf | Sarı ya da gri harf o pozisyonda olamaz | 3. pozisyon P değil, 4. pozisyon A değil, 5. pozisyon K değil |
| En az sayı | Tahmindeki yeşil + sarı kopya sayısı k ise harf en az k kez geçer | K en az 1, A en az 1 |
| Tam sayı | Aynı harfin bir kopyası griyse harf tam k kez geçer (k = 0: hiç yok) | P hiç yok; K tam 1, A tam 1 |

`Constraints.describe()` bunları Türkçe cümlelere çevirir: `1. harf K; 2. harf A; Kelimede yok: P; A başka pozisyonda yok; K başka pozisyonda yok`.

Birden çok gözlem birleşirken en az sayıların en büyüğü, tam/en çok sayıların en küçüğü alınır. Çelişen gözlemler (örneğin desen yanlış girildiyse) `ContradictionError` verir.

### Denklik kanıtı

**Önerme.** g bir tahmin, p gerçek bir gizli kelimenin ürettiği desen, w herhangi bir kelime olsun. w, (g, p)'nin kısıtlarını sağlar ⇔ feedback(g, w) = p.

**Yardımcı gözlem.** Herhangi bir feedback(g, w) deseninde, L harfinin yeşil + sarı kopya sayısı min(n_g(L), n_w(L))'dir. Burada n_g(L) ve n_w(L), L'nin g ve w'deki kopya sayısıdır. Yeşiller kopyaları birebir eşler, sarılar da eşleşmemiş kopya kaldığı sürece verilir.

**(⇒)** feedback(g, w) = p olsun. Yeşil pozisyonlar tam olarak g_i = w_i olan pozisyonlardır, dolayısıyla sabit ve yasak harf kısıtları sağlanır. Yardımcı gözlemden k_L = min(n_g(L), n_w(L)). L'nin gri bir kopyası varsa k_L < n_g(L) olur, o halde n_w(L) = k_L (tam sayı kısıtı). Gri kopya yoksa k_L = n_g(L) ≤ n_w(L) (en az sayı kısıtı).

**(⇐)** w kısıtları sağlasın. Pozisyon kısıtları, feedback(g, w)'nin yeşillerinin p'ninkilerle aynı olmasını sağlar. Sayı kısıtlarının iki durumunda da min(n_g(L), n_w(L)) = k_L çıkar. Yani her L için feedback(g, w) ile p aynı sayıda sarı içerir. İki desen de sarıları g'deki yeşil olmayan L kopyalarının en soldakilerine verir (p de aynı kuralla üretildi). O halde sarılar aynı pozisyonlardadır ve feedback(g, w) = p. ∎

Birden çok gözlem için kısıtların birleşimi, tüm gözlemlerle tutarlı olmaya denktir. Bu sonuç ayrıca testlerde 300 rastgele oyun durumunda ve 15.000 rastgele kelime çiftinde doğrulanıyor.

## 3. CSP modeli ve çözücü

| CSP öğesi | Bizim modelde |
| --- | --- |
| Değişkenler | X1, ..., X5: gizli kelimenin harfleri |
| Alanlar | Her X_i için mümkün harfler: başta 29 harf, sabit ve yasak harflerle daralır (düğüm tutarlılığı) |
| Kısıtlar | Tekli kısıtlar, harf sayısı kısıtları (global) ve sözlük kısıtı: X1..X5 geçerli bir kelime olmalı |

`CSPSolver` soldan sağa **geri izleme** (backtracking) yapar:

- Sözlük bir **önek ağacında** (trie, 4.933 düğüm) tutulur. Sözlükte olmayan bir önek hiç genişletilmez, yani sözlük kısıtı aramanın içinde uygulanır.
- Her atamadan sonra **ileri kontrol** (forward checking): bir harfin en çok sayısı aşıldıysa ya da hâlâ eksik olan harfler kalan pozisyonların alanlarına sığmıyorsa dal budanır.
- 500 rastgele durumda arama ortalama **703 düğüm** genişletti, yani ağacın yaklaşık %14'ü.

## 4. Desen tablosu

Tablo M[g, a] = feedback(g, a), tüm tahmin × gizli kelime çiftleri için önceden hesaplanır:

- 5.370 × 1.900 = **10.203.000 hücre**, uint8 ile **10,2 MB**
- numpy ile vektörleştirilmiş hesap **4,2 saniye**; sonra `data/cache/` altından 0,01 saniyede yüklenir
- **10.203.000 hücrenin hepsi** skaler `feedback()` ile tek tek karşılaştırıldı: uyuşmayan hücre **0**

Vektörleştirmenin anahtarı tekrarlanan harf kuralını sayılarla ifade etmek: yeşil olmayan i pozisyonundaki L harfi sarıdır ancak ve ancak

```
(gizli kelimede yeşil olmayan pozisyonlardaki L sayısı) > (tahminde i'den önce gelen, yeşil olmayan L sayısı)
```

Bu iki sayı, 5 × 5'lik harf eşitlik matrisleri üzerinde toplu toplamlarla bulunur.

Tablo hazır olunca:

- Filtreleme tek satır: `adaylar[M[g, adaylar] == desen]`
- Hafta 9 için bir tahminin adayları nasıl böldüğü: `np.bincount(M[g, adaylar], minlength=243)` (`PatternTable.partition_counts`)

## 5. Karşılaştırma sonuçları

`python scripts/benchmark_filters.py --tam-dogrulama --uctan-uca` (500 rastgele oyun durumu; her durumda 1.900 kelimenin hepsi filtreleniyor):

| Yöntem | Ortalama süre (µs) | Hızlanma |
| --- | --- | --- |
| Geri bildirimi yeniden hesapla (referans) | 8.081 | 1× |
| Kısıt kontrolü | 1.793 | 4,5× |
| CSP: trie + geri izleme + ileri kontrol | 1.209 | 6,7× |
| Desen tablosu (numpy) | 27 | 298× |

Dört yöntem 500 durumun **hepsinde aynı aday kümesini** verdi.

**Uçtan uca:** Harf sıklığı ajanını 1.900 kelimenin hepsinde oynatmak referans filtreyle 22,2 saniye, desen tablosuyla 8,1 saniye sürüyor. Filtre süresi tahmin başına 2,01 ms'den 0,05 ms'ye iniyor (41×). Sonuç (ortalama 3,74 tahmin) üç filtrede de aynı.

## 6. Hafta 9'a hazırlık

Entropi ajanı `PatternTable.partition_counts` ile her tahminin aday kümesini 243 desene nasıl böldüğünü bulacak ve beklenen bilgi kazancı en yüksek tahmini seçecek. Tablo tüm 5.370 tahmin için bu bölmeyi 0,05 saniyede veriyor.
