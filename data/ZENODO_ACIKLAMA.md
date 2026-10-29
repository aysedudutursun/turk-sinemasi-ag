# Zenodo / Kaggle yükleme bilgileri (bonus +3)

Yüklemeyi kendi hesabınla yapacaksın. Aşağıdaki alanları kopyalayıp kullanabilirsin.

**Başlık:** Turkish Cinema Actor Co-appearance Network (Wikidata, 1950–2025) / Türk Sineması Oyuncu Ağı

**Yazar:** Ayşe Dudu Tursun (Manisa Celal Bayar Üniversitesi)

**Açıklama (TR):**
Wikidata SPARQL ile toplanmış, 1950–2025 arası Türk yapımı filmler (P31/P279* Q11424, P495 = Q43) ve oyuncularından (P161) oluşan veri seti. İçinde film ↔ oyuncu iki parçalı ağ ile oyuncu–oyuncu ortak film projeksiyonu var (2.070 oyuncu, 16.073 ağırlıklı kenar; ağırlık = ortak film sayısı). Veri 2026-10-29 tarihinde toplanmıştır. Wikidata'daki kadro bilgisi eksik olduğundan (film başına ortanca 2 kayıtlı oyuncu) veri ünlü oyunculara doğru yanlıdır. Sosyal Ağ Analizi dersi kapsamında hazırlanmıştır.

**Description (EN):**
Turkish-produced films released 1950–2025 (Wikidata: P31/P279* Q11424, P495 = Q43) and their cast members (P161), collected via the Wikidata SPARQL endpoint on 2026-10-29. Includes the film–actor bipartite network and the actor–actor co-appearance projection (2,070 actors, 16,073 weighted edges; weight = number of shared films). Cast coverage in Wikidata is incomplete (median 2 recorded actors per film), so the data is biased toward well-known actors.

**Anahtar kelimeler:** social network analysis, small-world, Turkish cinema, Yeşilçam, co-appearance network, Wikidata, temporal networks

**Lisans:** Creative Commons Zero v1.0 (CC0 1.0). Kaynak veri Wikidata, CC0.

**Kaynak türü:** Dataset

**Yüklenecek dosyalar:**
- `data/raw/filmler.csv`
- `data/raw/film_oyuncu.csv`
- `data/raw/oyuncular.csv`
- `data/raw/toplama_bilgisi.json`
- `data/processed/dugumler.csv`
- `data/processed/kenar_listesi.csv`
- `data/processed/film_oyuncu_temiz.csv`
- `data/processed/oyuncu_agi.graphml`
- `data/processed/iki_parcali_ag.graphml`
- `data/VERI_SOZLUGU.md`

**İlgili bağlantı:** GitHub deposu (yükleme sırasında "Related identifiers" alanına ekle)
