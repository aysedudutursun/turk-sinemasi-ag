# Veri Sözlüğü — Türk Sineması Oyuncu Ağı

## Kaynak, lisans ve toplama

| Alan | Değer |
|---|---|
| Kaynak | Wikidata SPARQL uç noktası — `https://query.wikidata.org/sparql` |
| Lisans | Wikidata verisi **CC0 1.0** (kamu malı) |
| Toplama zamanı (UTC) | `2026-10-29T18:19:25+00:00` (`data/raw/toplama_bilgisi.json`) |
| Toplama script'i | `src/01_veri_topla.py` |
| Film tanımı | `P31/P279* Q11424` (film veya alt sınıfı) **ve** `P495` (menşe ülke) = `Q43` (Türkiye) |
| Yıl | Filmin `P577` (yayın tarihi) değerlerinin **en erken yılı**; yalnızca 1950–2025 arası tutulur |
| Oyuncu | Filmin `P161` (cast member) değerleri |
| Ad etiketleri | Türkçe, yoksa İngilizce, yoksa `mul` etiketi |

### Kapsam (toplama_bilgisi.json)

| Ölçü | Sayı |
|---|---|
| Ölçütlere uyan tüm filmler | 3.652 |
| Yılı 1950–2025 arası olan film | 2.961 |
| Yılı (P577) olmayan film (dışarıda) | 602 |
| En az bir P161 oyuncusu olan film | 1.954 |
| Film–oyuncu satırı | 6.099 |
| Benzersiz oyuncu | 2.070 |

### Bilinen eksiklikler
- Wikidata'da oyuncu kadroları eksik girilmiştir: P161'i olan filmlerde film başına kayıtlı oyuncu sayısının **ortancası 2**'dir. Veri, ünlü / başrol oyunculara doğru yanlıdır.
- Yılı olmayan 602 film ve 1950–2025 dışındaki filmler analize girmez.
- Türkçe/İngilizce etiketi olmayan bazı filmler ad yerine QID ile görünür (ör. `Q113675166`).
- 2020–2025 dilimi altı yıllık ve henüz eksik girilmiş bir dönemdir.

## data/raw/

### filmler.csv — 1950–2025 arası yılı olan filmler (P161 olsun olmasın)
| Sütun | Tip | Anlam |
|---|---|---|
| film_qid | metin | Filmin Wikidata kimliği (ör. `Q100215065`) |
| film_adi | metin | Filmin etiketi (tr → en → mul) |
| yil | tamsayı | P577 yayın tarihlerinin en erken yılı |

### film_oyuncu.csv — film ile oyuncu arasındaki P161 bağları
| Sütun | Tip | Anlam |
|---|---|---|
| film_qid | metin | Film QID |
| oyuncu_qid | metin | Oyuncu QID |
| oyuncu_adi | metin | Oyuncunun etiketi |

### oyuncular.csv — oyuncu nitelikleri
| Sütun | Tip | Anlam |
|---|---|---|
| oyuncu_qid | metin | Oyuncu QID |
| oyuncu_adi | metin | Oyuncunun etiketi |
| cinsiyet | metin | P21 (cinsiyet) etiketi; boş olabilir |
| dogum_yili | ondalık | P569 doğum tarihlerinin en erken yılı; boş olabilir |

### toplama_bilgisi.json
Toplama zamanı, kaynak, lisans, film tanımı, yıl aralığı ve yukarıdaki kapsam sayıları.

## data/processed/

### dugumler.csv — oyuncu ağının düğümleri
| Sütun | Tip | Anlam |
|---|---|---|
| oyuncu_qid | metin | Oyuncu QID (düğüm kimliği) |
| film_sayisi | tamsayı | Veri setindeki farklı film sayısı |
| ilk_yil / son_yil | tamsayı | Veri setindeki ilk ve son filminin yılı |
| oyuncu_adi | metin | Oyuncunun adı |
| cinsiyet | metin | P21 etiketi |
| dogum_yili | ondalık | P569 yılı |

### kenar_listesi.csv — oyuncu–oyuncu projeksiyonu (yönsüz)
| Sütun | Tip | Anlam |
|---|---|---|
| kaynak / hedef | metin | İki oyuncunun QID'si (alfabetik sıralı; yön yoktur) |
| kaynak_adi / hedef_adi | metin | Oyuncu adları |
| agirlik | tamsayı | Birlikte oynadıkları farklı film sayısı |
| ilk_yil / son_yil | tamsayı | Ortak filmlerinin ilk ve son yılı |

### film_oyuncu_temiz.csv — yıl filtresi uygulanmış film–oyuncu bağları
| Sütun | Tip | Anlam |
|---|---|---|
| film_qid, oyuncu_qid, oyuncu_adi | metin | `film_oyuncu.csv` ile aynı |
| film_adi | metin | Film adı |
| yil | tamsayı | Film yılı |

### oyuncu_agi.graphml
Oyuncu ağı. Düğüm öznitelikleri: `ad`, `film_sayisi`, `ilk_yil`, `son_yil`, `cinsiyet`, `dogum_yili` (bilinmiyorsa −1). Kenar öznitelikleri: `weight` (ortak film sayısı), `ilk_yil`, `son_yil`.

### iki_parcali_ag.graphml
Film ↔ oyuncu iki parçalı ağı. Düğüm öznitelikleri: `tur` (`film`/`oyuncu`), `ad`, `yil` (film yılı veya oyuncunun ilk yılı), `bipartite` (0 = film, 1 = oyuncu).

## results/ (analiz çıktıları)

| Dosya | İçerik |
|---|---|
| temel_olculer.json | Temel ölçüler (`temel`), derece dağılımı uyumu (`derece_dagilimi`: α, xmin, alternatif dağılımlarla R ve p), Spearman matrisi |
| merkeziyet_tum.csv | Dev bileşendeki her oyuncu için: `derece`, `guc_agirlikli_derece` (ağırlıklı derece), `derece_merk` (derece/(n−1)), `betweenness` (normalize), `closeness`, `harmonik_closeness`, `eigenvector` (en büyüğü 1), `pagerank` |
| ilk10_<ölçü>.csv | Her merkeziyet ölçüsünde ilk 10 oyuncu |
| spearman_merkeziyet.csv | Merkeziyet ölçüleri ve film sayısı arasındaki Spearman korelasyonları |
| topluluk_null.json | Louvain/Leiden modülerlikleri, 10 tohumla NMI/ARI, referans bölüm, en büyük toplulukların özetleri, null model z-skorları |
| topluluk_uyelik.csv | Dev bileşendeki her oyuncunun referans Leiden topluluğu (`topluluk`) |
| topluluk_adlari.json | Topluluk numarası → TR/EN ad (içeriğe bakılarak verildi) |
| null_model_dagilim.csv | 100 rastgele ağın her biri için `transitivity`, `ortalama_yerel_kumelenme`, `ortalama_yol`, `modularite_louvain`, `assortativity` |
| zamansal_kucuk_dunya.csv/.json | On yıllık her dilim için film/oyuncu/kenar sayıları, dev bileşen payı (dilim ve birikimli), `C`, `C_r`, `L`, `L_r`, `C_l`, `sigma` (ve rastgele ağlara göre %2,5–%97,5 aralığı), `omega` |
| kopru_testi.json | En yüksek betweenness'lı oyuncular çıkarılınca dev bileşen boyutu ve ortalama yol; aynı sayıda rastgele çıkarmayla karşılaştırma |
| poster_ozet.txt | Posterdeki özet metin |
