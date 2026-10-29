"""
04_topluluk_null.py
Louvain ve Leiden topluluk tespiti (dev bileşende, ağırlıklı), 10 tohumla kararlılık (NMI/ARI),
topluluk özetleri ve configuration-model null karşılaştırması (100 rastgele ağ, z-skorları).
"""
import random
from itertools import combinations

import igraph as ig
import leidenalg as la
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from ortak import PROC, SEED, SONUC, ag_yukle, dev_bilesen, kaydet_json, tohumla, yol_ornekle

TOHUMLAR = list(range(10))
N_NULL = int(__import__("os").environ.get("N_NULL", 100))


def louvain(g, seed, weights="weight"):
    random.seed(seed)                     # python-igraph rastgeleliği Python random'dan gelir
    return g.community_multilevel(weights=weights)


def leiden(g, seed, weights="weight"):
    return la.find_partition(g, la.ModularityVertexPartition, weights=weights, seed=seed, n_iterations=-1)


def benzerlik(bolumler):
    nmi, ari = [], []
    for a, b in combinations(bolumler, 2):
        nmi.append(normalized_mutual_info_score(a, b))
        ari.append(adjusted_rand_score(a, b))
    return {"nmi_ort": float(np.mean(nmi)), "nmi_min": float(np.min(nmi)),
            "ari_ort": float(np.mean(ari)), "ari_min": float(np.min(ari))}


def topluluk_ozeti(gc, uyelik, fo, k=6):
    df = pd.DataFrame({"qid": gc.vs["qid"], "ad": gc.vs["ad"], "derece": gc.degree(),
                       "ilk_yil": gc.vs["ilk_yil"], "son_yil": gc.vs["son_yil"],
                       "film_sayisi": gc.vs["film_sayisi"], "topluluk": uyelik})
    boy = df.topluluk.value_counts()
    ozet = []
    for t in boy.index[:k]:
        uye = df[df.topluluk == t]
        f = fo[fo.oyuncu_qid.isin(uye.qid)]
        # filmlerin "çoğunluğu" bu topluluktaki oyunculardan oluşan filmler
        film_pay = f.groupby(["film_qid", "film_adi", "yil"]).size().reset_index(name="uye_oyuncu")
        film_yil = f.drop_duplicates("film_qid").yil
        ozet.append({
            "topluluk": int(t), "boyut": int(len(uye)), "pay": len(uye) / len(df),
            "film_yili_medyan": float(film_yil.median()),
            "film_yili_q1_q3": [float(film_yil.quantile(.25)), float(film_yil.quantile(.75))],
            "kariyer_baslangic_medyan": float(uye.ilk_yil.median()),
            "en_bagli_10": uye.nlargest(10, "derece")[["ad", "derece", "ilk_yil", "son_yil"]].to_dict("records"),
            "en_cok_uyeli_filmler": film_pay.nlargest(8, "uye_oyuncu").to_dict("records"),
        })
    return df, ozet


def null_model(gc, gozlenen):
    """Viger-Latapy: aynı derece dizisine sahip, basit ve bağlı rastgele ağlar."""
    deg = gc.degree()
    kayit = []
    for i in range(N_NULL):
        random.seed(SEED + 1000 + i)
        r = ig.Graph.Degree_Sequence(deg, method="vl")
        L, _, _ = yol_ornekle(r, k=300, seed=SEED + i)
        q = louvain(r, SEED + i, weights=None).modularity
        kayit.append({"transitivity": r.transitivity_undirected(),
                      "ortalama_yerel_kumelenme": r.transitivity_avglocal_undirected(mode="zero"),
                      "ortalama_yol": L, "modularite_louvain": q,
                      "assortativity": r.assortativity_degree(directed=False)})
        if (i + 1) % 10 == 0:
            print(f"  null {i + 1}/{N_NULL}")
    nd = pd.DataFrame(kayit)
    nd.to_csv(SONUC / "null_model_dagilim.csv", index=False)
    z = {}
    for c in nd.columns:
        mu, sd = nd[c].mean(), nd[c].std(ddof=1)
        z[c] = {"gozlenen": gozlenen[c], "null_ort": mu, "null_std": sd,
                "z": (gozlenen[c] - mu) / sd if sd > 0 else float("inf"),
                "null_min": nd[c].min(), "null_maks": nd[c].max()}
    return z


def main():
    tohumla()
    g = ag_yukle()
    gc = dev_bilesen(g)
    fo = pd.read_csv(PROC / "film_oyuncu_temiz.csv")
    print(f"Dev bileşen: {gc.vcount()} düğüm, {gc.ecount()} kenar")

    lv = [louvain(gc, s) for s in TOHUMLAR]
    ld = [leiden(gc, s) for s in TOHUMLAR]
    lv_u = [p.membership for p in lv]
    ld_u = [p.membership for p in ld]
    lv_q = [gc.modularity(m, weights="weight") for m in lv_u]
    ld_q = [gc.modularity(m, weights="weight") for m in ld_u]
    capraz = [normalized_mutual_info_score(a, b) for a, b in zip(lv_u, ld_u)]
    capraz_ari = [adjusted_rand_score(a, b) for a, b in zip(lv_u, ld_u)]

    sonuc = {
        "louvain": {"modularite_ort": float(np.mean(lv_q)), "modularite_std": float(np.std(lv_q)),
                    "topluluk_sayisi": [len(set(m)) for m in lv_u], **benzerlik(lv_u)},
        "leiden": {"modularite_ort": float(np.mean(ld_q)), "modularite_std": float(np.std(ld_q)),
                   "topluluk_sayisi": [len(set(m)) for m in ld_u], **benzerlik(ld_u)},
        "louvain_leiden_ayni_tohum_nmi_ort": float(np.mean(capraz)),
        "louvain_leiden_ayni_tohum_ari_ort": float(np.mean(capraz_ari)),
    }
    # En yüksek modülerlikli Leiden bölümü referans alınır
    en_iyi = int(np.argmax(ld_q))
    ref = ld_u[en_iyi]
    sonuc["referans"] = {"algoritma": "leiden", "tohum": TOHUMLAR[en_iyi], "modularite": ld_q[en_iyi],
                         "topluluk_sayisi": len(set(ref))}
    df, ozet = topluluk_ozeti(gc, ref, fo)
    df.to_csv(SONUC / "topluluk_uyelik.csv", index=False)
    sonuc["en_buyuk_topluluklar"] = ozet
    print("Topluluklar tamam:", {k: v for k, v in sonuc.items() if k in ("louvain", "leiden", "referans")})

    # Null model: ağırlıksız topolojide karşılaştırma
    L, _, _ = yol_ornekle(gc, k=300, seed=SEED)
    gozlenen = {"transitivity": gc.transitivity_undirected(),
                "ortalama_yerel_kumelenme": gc.transitivity_avglocal_undirected(mode="zero"),
                "ortalama_yol": L,
                "modularite_louvain": louvain(gc, SEED, weights=None).modularity,
                "assortativity": gc.assortativity_degree(directed=False)}
    sonuc["null_model"] = {"yontem": "Viger-Latapy configuration model (aynı derece dizisi, basit, bağlı)",
                           "adet": N_NULL, "olcular": null_model(gc, gozlenen)}
    kaydet_json(sonuc, "topluluk_null.json")
    for k, v in sonuc["null_model"]["olcular"].items():
        print(f"{k:28s} gözlenen={v['gozlenen']:.4f} null={v['null_ort']:.4f}±{v['null_std']:.4f} z={v['z']:.1f}")


if __name__ == "__main__":
    main()
