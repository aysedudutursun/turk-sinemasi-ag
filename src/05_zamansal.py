"""
05_zamansal.py
Zorunlu ileri yöntem: on yıllık zamansal ağlar ve küçük dünya analizi.

Her on yıl için (yalnızca o on yılda çıkan filmlerden kurulan) oyuncu ağı:
  - dev bileşen payı, ortalama ayrım derecesi (ortalama en kısa yol, L), çap
  - C  : ortalama yerel kümelenme katsayısı (Watts-Strogatz tanımı)
  - Rastgele referans: aynı derece dizisine sahip N_RAND adet bağlı rastgele ağ (Viger-Latapy)
  - σ (Humphries & Gurney 2008) = (C / C_r) / (L / L_r)          σ > 1  → küçük dünya
  - ω (Telesford vd. 2011)      = L_r / L  -  C / C_l             ω ≈ 0 küçük dünya,
                                                                  ω → +1 rastgele, ω → -1 kafes
    C_l: aynı düğüm sayısı ve ortalama dereceye sahip halka kafesin kümelenmesi
    (igraph ile kafes gerçekten kurulup ölçülür). Not: Telesford vd. derece dağılımını koruyan
    kafes önerir; halka kafes yaygın bir yaklaşımdır ve raporda bu şekilde belirtilir.
Ayrıca birikimli ağ (başlangıçtan o on yılın sonuna kadar tüm filmler) için dev bileşen büyümesi.
"""
import os
import random
from itertools import combinations

import igraph as ig
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ortak import PROC, SEED, SEKIL, SONUC, kaydet_json, tohumla, yol_ornekle

N_RAND = int(os.environ.get("N_RAND", 100))
DILIMLER = [(1950, 1959), (1960, 1969), (1970, 1979), (1980, 1989),
            (1990, 1999), (2000, 2009), (2010, 2019), (2020, 2025)]


def dilim_grafi(fo: pd.DataFrame) -> ig.Graph:
    oyuncular = sorted(fo.oyuncu_qid.unique())
    idx = {q: i for i, q in enumerate(oyuncular)}
    kenar = set()
    for _, grup in fo.groupby("film_qid"):
        ids = sorted({idx[q] for q in grup.oyuncu_qid})
        kenar.update(combinations(ids, 2))
    g = ig.Graph(n=len(oyuncular), edges=list(kenar), directed=False)
    g.vs["qid"] = oyuncular
    return g


def kucuk_dunya(gc: ig.Graph, etiket: str):
    n, m = gc.vcount(), gc.ecount()
    C = gc.transitivity_avglocal_undirected(mode="zero")
    T = gc.transitivity_undirected()
    L, cap, tam = yol_ornekle(gc, k=500)
    deg = gc.degree()
    Cr, Lr, Tr = [], [], []
    for i in range(N_RAND):
        random.seed(SEED + 5000 + i)
        r = ig.Graph.Degree_Sequence(deg, method="vl")
        Cr.append(r.transitivity_avglocal_undirected(mode="zero"))
        Tr.append(r.transitivity_undirected())
        Lr.append(yol_ornekle(r, k=200, seed=SEED + i)[0])
    Cr_o, Lr_o = float(np.mean(Cr)), float(np.mean(Lr))
    k_ort = 2 * m / n
    yarim = max(1, int(round(k_ort / 2)))
    kafes = ig.Graph.Lattice([n], nei=yarim, directed=False, circular=True)
    Cl = kafes.transitivity_avglocal_undirected(mode="zero")
    sigma = (C / Cr_o) / (L / Lr_o)
    omega = Lr_o / L - C / Cl
    # σ'nın rastgele ağlar arası belirsizliği (her rastgele ağ tek tek)
    sig_dag = [(C / c) / (L / l) for c, l in zip(Cr, Lr) if c > 0]
    print(f"  {etiket}: n={n} C={C:.3f} Cr={Cr_o:.4f} L={L:.2f} Lr={Lr_o:.2f} σ={sigma:.1f} ω={omega:.3f}")
    return {"C": C, "transitivity": T, "L": L, "cap": cap, "yol_tam_hesap": tam,
            "C_r": Cr_o, "C_r_std": float(np.std(Cr, ddof=1)), "T_r": float(np.mean(Tr)),
            "L_r": Lr_o, "L_r_std": float(np.std(Lr, ddof=1)),
            "k_ort": k_ort, "kafes_nei": yarim, "C_l": Cl,
            "sigma": sigma, "sigma_p2_5": float(np.percentile(sig_dag, 2.5)),
            "sigma_p97_5": float(np.percentile(sig_dag, 97.5)), "omega": omega,
            "n_rand": N_RAND}


def main():
    tohumla()
    fo = pd.read_csv(PROC / "film_oyuncu_temiz.csv")
    satirlar = []
    for bas, son in DILIMLER:
        etiket = f"{bas}–{son}"
        d = fo[(fo.yil >= bas) & (fo.yil <= son)]
        kum = fo[fo.yil <= son]
        if d.film_qid.nunique() < 5:
            print(f"  {etiket}: yetersiz veri, atlandı")
            continue
        g = dilim_grafi(d)
        bil = g.connected_components()
        gc = bil.giant()
        gk = dilim_grafi(kum)
        gk_gc = gk.connected_components().giant()
        satir = {"dilim": etiket, "bas": bas, "son": son,
                 "film": int(d.film_qid.nunique()), "oyuncu": g.vcount(), "kenar": g.ecount(),
                 "yogunluk": g.density(), "ortalama_derece": float(np.mean(g.degree())),
                 "bilesen": len(bil), "gc_dugum": gc.vcount(), "gc_pay": gc.vcount() / g.vcount(),
                 "oyuncu_basina_film": float(d.groupby("oyuncu_qid").film_qid.nunique().mean()),
                 "film_basina_oyuncu": float(d.groupby("film_qid").oyuncu_qid.nunique().mean()),
                 "birikimli_oyuncu": gk.vcount(), "birikimli_gc_dugum": gk_gc.vcount(),
                 "birikimli_gc_pay": gk_gc.vcount() / gk.vcount()}
        if gc.vcount() >= 30:
            satir.update(kucuk_dunya(gc, etiket))
        satirlar.append(satir)

    df = pd.DataFrame(satirlar)
    df.to_csv(SONUC / "zamansal_kucuk_dunya.csv", index=False)
    kaydet_json(df.to_dict("records"), "zamansal_kucuk_dunya.json")

    x = df.dilim
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    ax[0, 0].bar(x, df.sigma, color="#2a6f97")
    ax[0, 0].errorbar(x, df.sigma, yerr=[df.sigma - df.sigma_p2_5, df.sigma_p97_5 - df.sigma],
                      fmt="none", ecolor="k", capsize=3)
    ax[0, 0].axhline(1, color="#c44536", ls="--", lw=1)
    ax[0, 0].set_title("Küçük dünya katsayısı σ (σ>1: küçük dünya)")
    ax[0, 1].plot(x, df.omega, "o-", color="#6a994e")
    ax[0, 1].axhline(0, color="#c44536", ls="--", lw=1)
    ax[0, 1].set_ylim(-1, 1)
    ax[0, 1].set_title("ω (0: küçük dünya, −1: kafes, +1: rastgele)")
    ax[1, 0].plot(x, df.L, "o-", label="Gözlenen L (ayrım derecesi)", color="#2a6f97")
    ax[1, 0].plot(x, df.L_r, "s--", label="Rastgele L_r", color="#999")
    ax[1, 0].set_title("Ortalama ayrım derecesi (dev bileşen)")
    ax[1, 0].legend()
    ax[1, 1].plot(x, df.gc_pay, "o-", label="On yıllık dilim", color="#bc6c25")
    ax[1, 1].plot(x, df.birikimli_gc_pay, "s--", label="Birikimli ağ", color="#7b2cbf")
    ax[1, 1].set_ylim(0, 1)
    ax[1, 1].set_title("Dev bileşenin oyuncular içindeki payı")
    ax[1, 1].legend()
    for a in ax.flat:
        a.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(SEKIL / "zamansal_kucuk_dunya.png", dpi=200)
    plt.close(fig)
    print(df[["dilim", "film", "oyuncu", "gc_pay", "C", "C_r", "L", "L_r", "sigma", "omega"]].round(3).to_string())


if __name__ == "__main__":
    main()
