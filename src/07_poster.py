"""
07_poster.py
A3 dikey (297 x 420 mm) statik poster: figures/poster_A3.pdf
Ağ paneli: dev bileşenin en bağlantılı N_POSTER oyuncusu (okunurluk için filtrelenmiş),
renk = Leiden topluluğu, boyut = derece, etiket = en yüksek dereceli N_ETIKET oyuncu.
"""
import json
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

from ortak import SEED, SEKIL, SONUC, ag_yukle, dev_bilesen

N_POSTER, N_ETIKET = 600, 30
PAL = ["#c0392b", "#2874a6", "#239b56", "#d68910", "#7d3c98", "#d63384",
       "#17a589", "#6e2c00", "#5d6d7e", "#1abc9c", "#7e5109", "#34495e"]
INK, MUTED, BG = "#1d1b18", "#6b645b", "#fbf8f3"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": "#cfc8bc"})


def main():
    g = ag_yukle()
    gc = dev_bilesen(g)
    tm = json.loads((SONUC / "temel_olculer.json").read_text(encoding="utf-8"))
    tn = json.loads((SONUC / "topluluk_null.json").read_text(encoding="utf-8"))
    zm = pd.read_csv(SONUC / "zamansal_kucuk_dunya.csv")
    uy = pd.read_csv(SONUC / "topluluk_uyelik.csv").set_index("qid")
    adlar = json.loads((SONUC / "topluluk_adlari.json").read_text(encoding="utf-8"))
    ozet = (SONUC / "poster_ozet.txt").read_text(encoding="utf-8").strip() if (SONUC / "poster_ozet.txt").exists() else ""

    sira = sorted(range(gc.vcount()), key=lambda i: -gc.degree(i))[:N_POSTER]
    alt = gc.subgraph(sira)
    random.seed(SEED)
    xy = np.array(alt.layout_fruchterman_reingold(weights=[np.log1p(w) for w in alt.es["weight"]], niter=2000).coords)
    # Uzak küçük kümeler ana yapıyı sıkıştırmasın: merkeze göre radyal sıkıştırma (yalnızca görsel)
    xy -= np.median(xy, axis=0)
    r = np.linalg.norm(xy, axis=1, keepdims=True) + 1e-9
    xy = xy / r * r ** 0.55
    com = [int(uy.loc[q, "topluluk"]) for q in alt.vs["qid"]]
    boy = uy.topluluk.value_counts()
    buyuk = sorted(boy.index, key=lambda c: (-boy[c], c))
    renk_id = {c: PAL[i] for i, c in enumerate(buyuk[:9])}
    renk = [renk_id.get(c, "#b5aea3") for c in com]
    deg = np.array(alt.degree())

    fig = plt.figure(figsize=(11.69, 16.54), facecolor=BG)
    fig.text(.05, .965, "Türk Sineması Bir Küçük Dünya mı?", fontsize=34, weight="bold", va="top")
    fig.text(.05, .935, "Yeşilçam'dan bugüne oyuncu iş birliği ağının zamansal küçük dünya analizi",
             fontsize=15, color=MUTED, va="top")
    t = tm["temel"]
    fig.text(.05, .912, f"Veri: Wikidata (CC0) · Türk yapımı filmler 1950–2025 · {t['dugum']:,} oyuncu, "
             f"{t['kenar']:,} bağ · Bağ = aynı filmde birlikte oynamak · Ayşe Dudu Tursun, MCBÜ Sosyal Ağ Analizi",
             fontsize=9.5, color=MUTED, va="top")

    ax = fig.add_axes([.03, .43, .94, .47])
    ax.set_facecolor(BG); ax.axis("off")
    segs = [(xy[e.source], xy[e.target]) for e in alt.es]
    ax.add_collection(LineCollection(segs, colors=(0.3, 0.25, 0.2, 0.05), linewidths=.3, zorder=1))
    ax.scatter(xy[:, 0], xy[:, 1], s=6 + 220 * (deg / deg.max()) ** 1.2, c=renk, alpha=.9,
               edgecolors="white", linewidths=.3, zorder=2)
    from adjustText import adjust_text
    yazilar = [ax.text(xy[i, 0], xy[i, 1], alt.vs[i]["ad"], fontsize=7.5, weight="bold", zorder=3,
                       bbox=dict(boxstyle="round,pad=.12", fc=BG, ec="none", alpha=.8))
               for i in np.argsort(-deg)[:N_ETIKET]]
    adjust_text(yazilar, ax=ax, arrowprops=dict(arrowstyle="-", color=MUTED, lw=.4))
    lej = [Patch(color=renk_id[c], label=adlar.get(str(c), {}).get("tr", f"Topluluk {c}"))
           for c in buyuk[:9] if c in renk_id]
    ax.legend(handles=lej, loc="lower left", fontsize=9, frameon=True, facecolor=BG, edgecolor="#cfc8bc",
              title="Leiden toplulukları", title_fontsize=9.5)
    ax.text(1, 0, f"En bağlantılı {N_POSTER} oyuncu gösterilmiştir · düğüm boyutu = derece",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=MUTED)

    # Alt paneller
    x = zm.dilim.str.replace("–", "–\n", regex=False)
    a1 = fig.add_axes([.07, .24, .40, .15])
    a1.bar(x, zm.sigma, color="#2874a6")
    a1.axhline(1, color="#c0392b", ls="--", lw=1)
    a1.set_title("Küçük dünya katsayısı σ (on yıllık ağlar)", fontsize=11, loc="left", weight="bold")
    a1.set_ylabel("σ  (>1 küçük dünya)")
    a1.tick_params(labelsize=7.5)
    a2 = fig.add_axes([.56, .24, .40, .15])
    a2.plot(x, zm.L, "o-", color="#2874a6", label="Gözlenen L")
    a2.plot(x, zm.L_r, "s--", color="#9a948a", label="Rastgele L")
    a2b = a2.twinx()
    a2b.plot(x, zm.birikimli_gc_pay * 100, "^-", color="#b9770e", label="Birikimli dev bileşen %")
    a2b.set_ylim(0, 100)
    a2.set_title("Ayrım derecesi ve dev bileşen", fontsize=11, loc="left", weight="bold")
    a2.set_ylabel("Ortalama en kısa yol")
    a2b.set_ylabel("Dev bileşen (%)")
    a2.tick_params(labelsize=7.5); a2b.tick_params(labelsize=7.5)
    h1, l1 = a2.get_legend_handles_labels(); h2, l2 = a2b.get_legend_handles_labels()
    a2.set_ylim(min(zm.L_r.min(), zm.L.min()) - .45, max(zm.L.max(), zm.L_r.max()) + .1)
    a2.legend(h1 + h2, l1 + l2, fontsize=7.5, loc="lower right", ncol=3)

    nm = tn["null_model"]["olcular"]
    kutular = [
        (f"{t['ortalama_en_kisa_yol_gc']:.2f}", "ortalama ayrım derecesi\n(dev bileşen)"),
        (f"{nm['ortalama_yerel_kumelenme']['gozlenen']:.2f}", f"kümelenme (dev bileşen) · rastgele: {nm['ortalama_yerel_kumelenme']['null_ort']:.2f}\n"
                                                  f"z = {nm['ortalama_yerel_kumelenme']['z']:.0f}"),
        (f"{t['dev_bilesen_payi']*100:.0f}%", "oyuncu dev bileşende"),
        (f"{tn['referans']['modularite']:.2f}", f"modülerlik (Leiden)\nrastgele: {nm['modularite_louvain']['null_ort']:.2f}"),
    ]
    for i, (b, k) in enumerate(kutular):
        x0 = .05 + i * .235
        fig.text(x0, .19, b, fontsize=26, weight="bold", color="#c0392b", va="top")
        fig.text(x0, .155, k, fontsize=9, color=MUTED, va="top")
    if ozet:
        fig.text(.05, .105, ozet, fontsize=11, va="top", wrap=True)
    fig.text(.05, .02, "Yöntem: iki parçalı film–oyuncu ağı → oyuncu projeksiyonu · σ = (C/Cᵣ)/(L/Lᵣ), "
             "Cᵣ ve Lᵣ: aynı derece dizisine sahip rastgele ağlar · Kod ve veri: GitHub deposu",
             fontsize=8, color=MUTED)
    fig.savefig(SEKIL / "poster_A3.pdf", facecolor=BG)
    fig.savefig(SEKIL / "poster_A3_onizleme.png", dpi=110, facecolor=BG)
    print("poster_A3.pdf yazıldı")


if __name__ == "__main__":
    main()
