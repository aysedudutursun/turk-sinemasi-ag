"""
02_ag_kur.py
Ham veriden (data/raw) iki parçalı film-oyuncu ağını ve oyuncu-oyuncu projeksiyonunu kurar.

Kararlar ve gerekçeleri
  * Düğüm (projeksiyon): oyuncu (Wikidata QID ile tekil; aynı adlı iki kişi karışmaz).
  * Kenar: iki oyuncu en az bir Türk filminde birlikte P161 olarak listelenmişse.
  * Yön: yok. Birlikte oynamak simetrik bir ilişkidir.
  * Ağırlık: ortak film sayısı. Tekrarlanan iş birliği, tek seferlikten daha güçlü bağdır.
  * Kenar öznitelikleri: ilk_yil / son_yil (ortak filmlerin ilk ve son yılı) zamansal analiz için.

Çıktılar (data/processed/):
  dugumler.csv, kenar_listesi.csv, film_oyuncu_temiz.csv,
  oyuncu_agi.graphml, iki_parcali_ag.graphml
"""
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

KOK = Path(__file__).resolve().parents[1]
RAW, PROC = KOK / "data" / "raw", KOK / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)


def yukle():
    filmler = pd.read_csv(RAW / "filmler.csv")
    fo = pd.read_csv(RAW / "film_oyuncu.csv")
    oy = pd.read_csv(RAW / "oyuncular.csv")
    fo = fo.merge(filmler[["film_qid", "film_adi", "yil"]], on="film_qid", how="inner")
    return filmler, fo, oy


def projeksiyon(fo: pd.DataFrame) -> pd.DataFrame:
    """Her film içindeki oyuncu çiftlerinden kenar listesi üretir (ağırlık = ortak film sayısı)."""
    kayit = []
    for (fq, yil), grup in fo.groupby(["film_qid", "yil"]):
        oyuncular = sorted(set(grup.oyuncu_qid))
        for a, b in combinations(oyuncular, 2):
            kayit.append((a, b, fq, yil))
    ciftler = pd.DataFrame(kayit, columns=["kaynak", "hedef", "film_qid", "yil"])
    kenar = (ciftler.groupby(["kaynak", "hedef"])
             .agg(agirlik=("film_qid", "nunique"), ilk_yil=("yil", "min"), son_yil=("yil", "max"))
             .reset_index())
    return kenar


def main():
    filmler, fo, oy = yukle()

    # Oyuncu tablosu
    ozet = (fo.groupby("oyuncu_qid")
            .agg(film_sayisi=("film_qid", "nunique"), ilk_yil=("yil", "min"), son_yil=("yil", "max"))
            .reset_index())
    dug = ozet.merge(oy, on="oyuncu_qid", how="left")
    ad_yedek = fo.drop_duplicates("oyuncu_qid").set_index("oyuncu_qid")["oyuncu_adi"]
    dug["oyuncu_adi"] = dug["oyuncu_adi"].fillna(dug["oyuncu_qid"].map(ad_yedek)).fillna(dug["oyuncu_qid"])

    kenar = projeksiyon(fo)
    ad = dug.set_index("oyuncu_qid")["oyuncu_adi"]
    kenar["kaynak_adi"] = kenar.kaynak.map(ad)
    kenar["hedef_adi"] = kenar.hedef.map(ad)

    # Graf
    G = nx.Graph()
    for r in dug.itertuples(index=False):
        G.add_node(r.oyuncu_qid, ad=str(r.oyuncu_adi), film_sayisi=int(r.film_sayisi),
                   ilk_yil=int(r.ilk_yil), son_yil=int(r.son_yil),
                   cinsiyet=str(r.cinsiyet) if pd.notna(r.cinsiyet) else "",
                   dogum_yili=int(r.dogum_yili) if pd.notna(r.dogum_yili) else -1)
    for r in kenar.itertuples(index=False):
        G.add_edge(r.kaynak, r.hedef, weight=int(r.agirlik), ilk_yil=int(r.ilk_yil), son_yil=int(r.son_yil))

    # İki parçalı graf
    B = nx.Graph()
    for r in filmler.itertuples(index=False):
        if r.film_qid in set(fo.film_qid):
            B.add_node(r.film_qid, tur="film", ad=str(r.film_adi), yil=int(r.yil), bipartite=0)
    for r in dug.itertuples(index=False):
        B.add_node(r.oyuncu_qid, tur="oyuncu", ad=str(r.oyuncu_adi), yil=int(r.ilk_yil), bipartite=1)
    B.add_edges_from(zip(fo.film_qid, fo.oyuncu_qid))

    dug.to_csv(PROC / "dugumler.csv", index=False)
    kenar[["kaynak", "hedef", "kaynak_adi", "hedef_adi", "agirlik", "ilk_yil", "son_yil"]] \
        .to_csv(PROC / "kenar_listesi.csv", index=False)
    fo.to_csv(PROC / "film_oyuncu_temiz.csv", index=False)
    nx.write_graphml(G, PROC / "oyuncu_agi.graphml")
    nx.write_graphml(B, PROC / "iki_parcali_ag.graphml")

    print(f"İki parçalı ağ: {sum(1 for _, d in B.nodes(data=True) if d['tur']=='film')} film, "
          f"{sum(1 for _, d in B.nodes(data=True) if d['tur']=='oyuncu')} oyuncu, {B.number_of_edges()} bağ")
    print(f"Oyuncu ağı: {G.number_of_nodes()} düğüm, {G.number_of_edges()} kenar, "
          f"yoğunluk {nx.density(G):.6f}, bileşen {nx.number_connected_components(G)}")


if __name__ == "__main__":
    main()
