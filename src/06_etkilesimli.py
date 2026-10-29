"""
06_etkilesimli.py
Sigma.js ile etkileşimli ağ (docs/index.html): arama, detay paneli, topluluk filtresi, TR/EN.

Filtreleme kararı: Tüm ağı tarayıcıda çizmek okunaksız ve yavaş olur. Dev bileşenden
derecesi en yüksek N_DUGUM oyuncu alınır; aralarındaki kenarlardan en fazla N_KENAR tanesi
(ağırlığa göre en güçlüler) gösterilir. Detay panelindeki sayılar ise TÜM ağdan hesaplanmıştır.
"""
import json
import random

import igraph as ig
import numpy as np
import pandas as pd

from ortak import KOK, PROC, SEED, SONUC, ag_yukle, dev_bilesen

N_DUGUM = 1200
N_KENAR = 20000
DOCS = KOK / "docs"
DOCS.mkdir(exist_ok=True)


def main():
    random.seed(SEED)
    g = ag_yukle()
    gc = dev_bilesen(g)
    mk = pd.read_csv(SONUC / "merkeziyet_tum.csv")
    uy = pd.read_csv(SONUC / "topluluk_uyelik.csv")
    fo = pd.read_csv(PROC / "film_oyuncu_temiz.csv")
    adlar = json.loads((SONUC / "topluluk_adlari.json").read_text(encoding="utf-8"))

    mk["sira_derece"] = mk.derece.rank(ascending=False, method="min").astype(int)
    mk["sira_betweenness"] = mk.betweenness.rank(ascending=False, method="min").astype(int)
    mk["sira_pagerank"] = mk.pagerank.rank(ascending=False, method="min").astype(int)
    mk = mk.merge(uy[["qid", "topluluk"]], on="qid", how="left").set_index("qid")

    secilen = mk.nlargest(N_DUGUM, "derece").index.tolist()
    q2i = {q: i for i, q in enumerate(gc.vs["qid"])}
    alt = gc.subgraph([q2i[q] for q in secilen])
    random.seed(SEED)
    yer = alt.layout_fruchterman_reingold(weights=[np.log1p(w) for w in alt.es["weight"]], niter=1500)
    xy = np.array(yer.coords)

    # ortak oyuncular (tüm ağdan)
    def ortaklar(q, k=8):
        v = gc.vs[q2i[q]]
        komsu = []
        for e in gc.incident(v.index):
            ed = gc.es[e]
            o = ed.target if ed.source == v.index else ed.source
            komsu.append((ed["weight"], gc.vs[o]["ad"]))
        komsu.sort(reverse=True)
        return [[a, int(w)] for w, a in komsu[:k]]

    film_liste = (fo.sort_values("yil").groupby("oyuncu_qid")
                  .apply(lambda d: [[str(a), int(y)] for a, y in zip(d.film_adi, d.yil)]).to_dict())

    nodes = []
    for i, q in enumerate(alt.vs["qid"]):
        r = mk.loc[q]
        filmler = film_liste.get(q, [])
        nodes.append({
            "id": q, "label": r.ad, "x": float(xy[i, 0]), "y": float(-xy[i, 1]),
            "c": int(r.topluluk) if pd.notna(r.topluluk) else -1,
            "d": int(r.derece), "f": int(r.film_sayisi), "y0": int(r.ilk_yil), "y1": int(r.son_yil),
            "rd": int(r.sira_derece), "rb": int(r.sira_betweenness), "rp": int(r.sira_pagerank),
            "co": ortaklar(q), "fl": filmler[:3] + (filmler[-2:] if len(filmler) > 5 else filmler[3:5]),
        })
    kenarlar = sorted(((e["weight"], e.source, e.target) for e in alt.es), reverse=True)[:N_KENAR]
    edges = [[alt.vs[s]["qid"], alt.vs[t]["qid"], int(w)] for w, s, t in kenarlar]

    boy = uy.topluluk.value_counts()                      # renk sırası posterle aynı: tüm ağdaki boyut
    gosterilen = sorted({n["c"] for n in nodes if n["c"] >= 0}, key=lambda c: (-boy[c], c))
    topluluklar = []
    for c in gosterilen:
        a = adlar.get(str(c), {})
        topluluklar.append({"id": c, "tr": a.get("tr", f"Topluluk {c}"), "en": a.get("en", f"Community {c}"),
                            "n": sum(1 for n in nodes if n["c"] == c)})

    meta = json.loads((SONUC / "temel_olculer.json").read_text(encoding="utf-8"))["temel"]
    veri = {"nodes": nodes, "edges": edges, "communities": topluluklar,
            "meta": {"n_all": meta["dugum"], "m_all": meta["kenar"], "n_show": len(nodes), "m_show": len(edges)}}
    sablon = (KOK / "src" / "etkilesimli_sablon.html").read_text(encoding="utf-8")
    html = sablon.replace("/*__VERI__*/null", json.dumps(veri, ensure_ascii=False, separators=(",", ":")))
    # Kütüphaneler sayfaya gömülür (CDN'e bağımlı kalmasın); src/lib/ altında npm'den alınmış resmi dosyalar
    for ad, url in [("graphology.umd.min.js", "https://cdn.jsdelivr.net/npm/graphology@0.25.4/dist/graphology.umd.min.js"),
                    ("sigma.min.js", "https://cdn.jsdelivr.net/npm/sigma@2.4.0/build/sigma.min.js")]:
        kod = (KOK / "src" / "lib" / ad).read_text(encoding="utf-8").replace("</script", "<\\/script")
        html = html.replace(f'<script src="{url}"></script>', f"<script>{kod}</script>")
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"docs/index.html: {len(nodes)} düğüm, {len(edges)} kenar, {len(html)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
