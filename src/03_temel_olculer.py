"""
03_temel_olculer.py
Temel ağ ölçüleri, derece dağılımı (powerlaw), merkeziyetler, ilk-10 tabloları, Spearman.

Topoloji ölçüleri ağırlıksız hesaplanır (bir bağın var olup olmaması); ağırlık yalnızca
"güçlü bağ" (weighted degree = strength) için raporlanır.
"""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import powerlaw
from scipy.stats import spearmanr

from ortak import SEKIL, SONUC, ag_yukle, dev_bilesen, kaydet_json, tohumla, yol_ornekle

warnings.filterwarnings("ignore")
tohumla()


def temel(g):
    n, m = g.vcount(), g.ecount()
    bil = g.connected_components()
    gc = bil.giant()
    ort_yol, cap, tam = yol_ornekle(gc)
    deg = np.array(g.degree())
    return {
        "dugum": n, "kenar": m,
        "yogunluk": 2 * m / (n * (n - 1)),
        "ortalama_derece": float(deg.mean()),
        "medyan_derece": float(np.median(deg)),
        "maks_derece": int(deg.max()),
        "izole_dugum": int((deg == 0).sum()),
        "bilesen_sayisi": len(bil),
        "dev_bilesen_dugum": gc.vcount(),
        "dev_bilesen_kenar": gc.ecount(),
        "dev_bilesen_payi": gc.vcount() / n,
        "ikinci_bilesen_dugum": sorted(bil.sizes(), reverse=True)[1] if len(bil) > 1 else 0,
        "ortalama_en_kisa_yol_gc": ort_yol,
        "cap_gc": cap,
        "yol_tam_hesap": tam,
        "global_kumelenme_transitivity": g.transitivity_undirected(),
        "ortalama_yerel_kumelenme": g.transitivity_avglocal_undirected(mode="zero"),
        "derece_assortativity": g.assortativity_degree(directed=False),
    }


def derece_dagilimi(g):
    deg = np.array(g.degree())
    deg = deg[deg > 0]
    fit = powerlaw.Fit(deg, discrete=True, verbose=False)
    sonuc = {"alpha": fit.power_law.alpha, "xmin": int(fit.power_law.xmin),
             "sigma_alpha": fit.power_law.sigma,
             "kuyruktaki_dugum": int((deg >= fit.power_law.xmin).sum()), "karsilastirma": {}}
    for alt in ["lognormal", "exponential", "truncated_power_law", "stretched_exponential"]:
        R, p = fit.distribution_compare("power_law", alt, normalized_ratio=True)
        sonuc["karsilastirma"][alt] = {"R": float(R), "p": float(p),
                                       "yorum": ("anlamlı fark yok" if p >= 0.1 else
                                                 ("power_law daha iyi" if R > 0 else f"{alt} daha iyi"))}
    if fit.lognormal is not None:
        sonuc["lognormal_mu"] = fit.lognormal.mu
        sonuc["lognormal_sigma"] = fit.lognormal.sigma

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    vals, cnts = np.unique(deg, return_counts=True)
    ax[0].loglog(vals, cnts / cnts.sum(), "o", ms=3, alpha=.6, color="#2a6f97")
    ax[0].set_xlabel("Derece k (birlikte oynanan farklı oyuncu)")
    ax[0].set_ylabel("P(k)")
    ax[0].set_title("Derece dağılımı (log-log)")
    fit.plot_ccdf(ax=ax[1], color="#2a6f97", linewidth=2, label="Gözlenen")
    fit.power_law.plot_ccdf(ax=ax[1], color="#c44536", linestyle="--", label=f"Kuvvet yasası α={fit.power_law.alpha:.2f}")
    fit.lognormal.plot_ccdf(ax=ax[1], color="#6a994e", linestyle=":", label="Log-normal")
    fit.truncated_power_law.plot_ccdf(ax=ax[1], color="#bc6c25", linestyle="-.", label="Kesik kuvvet yasası")
    ax[1].set_xlabel("Derece k (k ≥ xmin)")
    ax[1].set_ylabel("P(K ≥ k)")
    ax[1].set_title("CCDF ve aday dağılımlar")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(SEKIL / "derece_dagilimi.png", dpi=200)
    plt.close(fig)
    return sonuc


def merkeziyetler(gc):
    n = gc.vcount()
    df = pd.DataFrame({
        "qid": gc.vs["qid"], "ad": gc.vs["ad"], "film_sayisi": gc.vs["film_sayisi"],
        "ilk_yil": gc.vs["ilk_yil"], "son_yil": gc.vs["son_yil"],
        "derece": gc.degree(),
        "guc_agirlikli_derece": gc.strength(weights="weight"),
    })
    df["derece_merk"] = df.derece / (n - 1)
    # Betweenness: tam hesap (ağırlıksız, normalize)
    bt = np.array(gc.betweenness(directed=False))
    df["betweenness"] = bt / ((n - 1) * (n - 2) / 2)
    df["closeness"] = gc.closeness()
    df["harmonik_closeness"] = gc.harmonic_centrality()
    df["eigenvector"] = gc.eigenvector_centrality(scale=True)
    df["pagerank"] = gc.pagerank(directed=False)
    return df


def main():
    g = ag_yukle()
    gc = dev_bilesen(g)
    print(f"Ağ: {g.vcount()} düğüm, {g.ecount()} kenar; dev bileşen {gc.vcount()}")

    t = temel(g)
    print("Temel ölçüler tamam")
    dd = derece_dagilimi(g)
    print("Derece dağılımı tamam")
    mk = merkeziyetler(gc)
    print("Merkeziyetler tamam")

    olcu = ["derece", "betweenness", "closeness", "eigenvector", "pagerank", "film_sayisi"]
    rho, _ = spearmanr(mk[olcu])
    sp = pd.DataFrame(rho, index=olcu, columns=olcu)
    sp.to_csv(SONUC / "spearman_merkeziyet.csv")

    mk.sort_values("derece", ascending=False).to_csv(SONUC / "merkeziyet_tum.csv", index=False)
    ilk10 = {}
    for o in ["derece", "betweenness", "closeness", "eigenvector", "pagerank"]:
        tab = mk.nlargest(10, o)[["ad", "qid", o, "film_sayisi", "ilk_yil", "son_yil"]]
        ilk10[o] = tab.to_dict("records")
        tab.to_csv(SONUC / f"ilk10_{o}.csv", index=False)

    kaydet_json({"temel": t, "derece_dagilimi": dd, "spearman": sp.round(4).to_dict()}, "temel_olculer.json")
    print(pd.Series(t).to_string())
    print(dd)
    print(sp.round(3))


if __name__ == "__main__":
    main()
