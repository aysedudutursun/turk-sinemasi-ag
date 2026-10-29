# Türk Sineması Oyuncu Ağı — Zamansal Küçük Dünya Analizi

Manisa Celal Bayar Üniversitesi · Büyük Veri Analistliği · Sosyal Ağ Analizi dönem ödevi
Öğrenci: Ayşe Dudu Tursun

**Araştırma sorusu:** Türk sineması bir "küçük dünya" mı? Yeşilçam'dan bugüne ağın yapısı nasıl değişti?

## Bulgunun tek cümlelik özeti
Wikidata'daki 2.070 oyuncu ve 16.073 ortak film bağından kurulan Türk sineması ağı, 1950'lerden 2020'lere **her on yıllık dilimde küçük dünyadır (σ = 3,6–12,7 > 1)**. Bütün ağda oyuncular ortalama **3,44 adımla** birbirine bağlıdır, kümelenme ise aynı derece dizisine sahip 100 rastgele ağdakinin yaklaşık 18,6 katıdır (0,71'e karşı 0,04).

## CV cümlesi
> **Zamansal küçük dünya ağ analizi:** Wikidata SPARQL ile 2.070 oyuncu ve 16.073 bağlık Türk sineması oyuncu ağını kurdum. On yıllık ağlarda σ ve ω katsayılarıyla küçük dünya yapısını, Louvain/Leiden topluluklarını ve 100 rastgele ağlık null modeli Python (igraph, leidenalg, powerlaw) ile test ettim, sonuçları Sigma.js tabanlı etkileşimli bir ağla yayımladım.

## Çıktılar
- **Etkileşimli ağ:** `docs/index.html`. Arama, detay paneli, topluluk filtresi ve TR/EN var. Tek dosyadır, kütüphaneler içine gömülüdür. GitHub Pages ile (Settings → Pages → `docs/` klasörü) yayımlanabilir. Link: _(GitHub Pages / portfolyo linkini buraya ekle)_
- **A3 poster:** `figures/poster_A3.pdf`
- **Defter:** `analiz.ipynb`. Tüm adımları sırayla çalıştırır ve sonuçları gösterir.
- **Kenar listesi ve GraphML:** `data/processed/kenar_listesi.csv`, `data/processed/oyuncu_agi.graphml`, `data/processed/iki_parcali_ag.graphml`
- **Veri sözlüğü:** `data/VERI_SOZLUGU.md`
- **Rapor:** `report/rapor.pdf` (üretici: `report/rapor_uret.py`)
- **Sunum:** `presentation/sunum.pdf`, konuşma notları: `presentation/konusma_notlari.md`

## Klasör yapısı
```
src/
  01_veri_topla.py      Wikidata SPARQL → data/raw/
  02_ag_kur.py          iki parçalı ağ + oyuncu projeksiyonu → data/processed/
  03_temel_olculer.py   temel ölçüler, powerlaw, merkeziyetler, Spearman
  04_topluluk_null.py   Louvain/Leiden, 10 tohumla NMI/ARI, 100 rastgele ağlık null model
  05_zamansal.py        on yıllık ağlar: σ, ω, ayrım derecesi, dev bileşen büyümesi
  08_kopru_testi.py     yüksek betweenness'lı oyuncuları çıkarma testi
  06_etkilesimli.py     docs/index.html (şablon: etkilesimli_sablon.html, lib/ = sigma.js, graphology)
  07_poster.py          figures/poster_A3.pdf
  ortak.py              ortak yardımcılar, SEED = 42
data/raw/               ham Wikidata verisi (toplama anlık görüntüsü)
data/processed/         düğüm/kenar tabloları, GraphML
results/                tüm sayısal sonuçlar (JSON/CSV)
figures/                şekiller ve poster
docs/                   etkileşimli ağ
```

## Nasıl çalıştırılır
```bash
pip install -r requirements.txt
cd src
python 01_veri_topla.py      # internet gerekir; data/raw/ yeniden oluşturulur
python 02_ag_kur.py
python 03_temel_olculer.py
python 04_topluluk_null.py
python 05_zamansal.py
python 08_kopru_testi.py
python 06_etkilesimli.py
python 07_poster.py
```
Alternatif olarak `analiz.ipynb` defteri tüm adımları çalıştırır. `data/raw/` doluysa veri yeniden çekilmez. Tüm rastgele işlemler sabit tohumla (`SEED = 42`) yapılır. Not: Wikidata canlı bir veri tabanıdır, `01` yeniden çalıştırılırsa sayılar değişebilir. Rapordaki sonuçlar `data/raw/toplama_bilgisi.json`'daki tarihte alınmış anlık görüntüye dayanır.

## Yapay zekâ beyanı
Bu projede kod, analiz ve metin taslaklarının hazırlanmasında Anthropic'in Claude yapay zekâ asistanından yararlanılmıştır. Tüm sonuçlar öğrenci tarafından gözden geçirilmiştir.
_(Öğrenci notu: Bu beyanı son haliyle kendin düzenle.)_

## Lisans
- Kod: MIT
- Veri: Wikidata kaynaklı, CC0 1.0
