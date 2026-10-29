"""
08_kopru_testi.py
"Bu oyuncu olmasaydı?" testi: betweenness'ı en yüksek oyuncular dev bileşenden tek tek
ve birlikte çıkarılınca dev bileşen boyutu ve ortalama ayrım derecesi nasıl değişir?
Karşılaştırma için aynı sayıda rastgele oyuncu çıkarma (100 tekrar) da yapılır.
"""
import random

import numpy as np
import pandas as pd

from ortak import SEED, SONUC, ag_yukle, dev_bilesen, kaydet_json, tohumla


def olc(g):
    gc = g.connected_components().giant()
    return gc.vcount(), gc.average_path_length(directed=False)


def main():
    tohumla()
    gc = dev_bilesen(ag_yukle())
    mk = pd.read_csv(SONUC / "merkeziyet_tum.csv").nlargest(5, "betweenness")
    q2i = {q: i for i, q in enumerate(gc.vs["qid"])}
    n0, L0 = olc(gc)
    sonuc = {"temel": {"gc": n0, "L": L0}, "tekli": [], "birlikte": []}
    for r in mk.itertuples():
        g = gc.copy(); g.delete_vertices([q2i[r.qid]])
        n, L = olc(g)
        sonuc["tekli"].append({"ad": r.ad, "gc": n, "kopan": n0 - 1 - n, "L": L, "L_degisim": L - L0})
    for k in (1, 3, 5):
        g = gc.copy(); g.delete_vertices([q2i[q] for q in mk.qid[:k]])
        n, L = olc(g)
        rast = []
        for i in range(100):
            random.seed(SEED + i)
            h = gc.copy(); h.delete_vertices(random.sample(range(gc.vcount()), k))
            rast.append(olc(h))
        rast = np.array(rast)
        sonuc["birlikte"].append({"k": k, "adlar": mk.ad[:k].tolist(), "gc": n, "kopan": n0 - k - n, "L": L,
                                  "rastgele_kopan_ort": float(np.mean(n0 - k - rast[:, 0])),
                                  "rastgele_L_ort": float(rast[:, 1].mean())})
    kaydet_json(sonuc, "kopru_testi.json")
    print(pd.DataFrame(sonuc["tekli"]).round(3).to_string(index=False))
    print(pd.DataFrame(sonuc["birlikte"]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
