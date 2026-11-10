# Aday filtreleme karşılaştırması (500 rastgele oyun durumu)

Dört yöntem 500 durumun hepsinde aynı aday kümesini verdi mi: evet.
Bir durumda ortalama 115.1 aday kaldı (medyan 19.0).

| Yöntem | Ortalama süre (µs) | Medyan süre (µs) | Hızlanma |
| --- | --- | --- | --- |
| Geri bildirimi yeniden hesapla (referans) | 8,081.2 | 7,152.8 | 1.0× |
| Kısıt kontrolü | 1,792.7 | 1,376.9 | 4.5× |
| CSP: trie + geri izleme + ileri kontrol | 1,208.6 | 938.0 | 6.7× |
| Desen tablosu (numpy) | 27.1 | 25.9 | 298.2× |

CSP araması ortalama 703.0 trie düğümü genişletti (ağaçta toplam 4,933 düğüm var).

Desen tablosu: 5,370 × 1,900 = 10,203,000 hücre, 10.2 MB, hesaplama 4.17 s. Rastgele 200,000 çiftte uyuşmayan: 0; tüm hücrelerde uyuşmayan: 0.

## Uçtan uca: harf sıklığı ajanı, 1,900 oyun

| Filtre | Toplam süre (s) | Filtre süresi / tahmin (ms) | Ortalama tahmin |
| --- | --- | --- | --- |
| Geri bildirimi yeniden hesapla (referans) | 22.15 | 2.011 | 3.74 |
| Kısıt kontrolü | 14.47 | 0.926 | 3.74 |
| Desen tablosu (numpy) | 8.13 | 0.049 | 3.74 |
