"""Ortak yardımcılar: ağ yükleme, dev bileşen, örneklemeli yol uzunluğu."""
import json
import random
from pathlib import Path

import igraph as ig
import numpy as np
import pandas as pd

SEED = 42
KOK = Path(__file__).resolve().parents[1]
PROC = KOK / "data" / "processed"
SONUC = KOK / "results"
SEKIL = KOK / "figures"
for p in (SONUC, SEKIL):
    p.mkdir(parents=True, exist_ok=True)


def tohumla(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)


def ag_yukle() -> ig.Graph:
    """Oyuncu ağını igraph olarak yükler (izole düğümler dahil)."""
    dug = pd.read_csv(PROC / "dugumler.csv")
    ken = pd.read_csv(PROC / "kenar_listesi.csv")
    idx = {q: i for i, q in enumerate(dug.oyuncu_qid)}
    g = ig.Graph(n=len(dug), edges=[(idx[a], idx[b]) for a, b in zip(ken.kaynak, ken.hedef)], directed=False)
    g.vs["qid"] = dug.oyuncu_qid.tolist()
    g.vs["ad"] = dug.oyuncu_adi.astype(str).tolist()
    g.vs["film_sayisi"] = dug.film_sayisi.tolist()
    g.vs["ilk_yil"] = dug.ilk_yil.tolist()
    g.vs["son_yil"] = dug.son_yil.tolist()
    g.es["weight"] = ken.agirlik.tolist()
    g.es["ilk_yil"] = ken.ilk_yil.tolist()
    return g


def dev_bilesen(g: ig.Graph) -> ig.Graph:
    return g.connected_components().giant()


def yol_ornekle(g: ig.Graph, k: int = 1000, seed: int = SEED, tam_esik: int = 6000):
    """Bağlı bir grafta ortalama en kısa yol ve çap.
    Küçük grafta tam hesap; büyükte k rastgele kaynaktan BFS (ortalama: yansız tahmin,
    çap: alt sınır). Döner: (ortalama, cap, tam_mi)"""
    n = g.vcount()
    if n <= tam_esik:
        return g.average_path_length(directed=False), g.diameter(directed=False), True
    rng = random.Random(seed)
    kaynaklar = rng.sample(range(n), min(k, n))
    toplam, sayi, cap = 0.0, 0, 0
    for s in kaynaklar:
        d = np.asarray(g.distances(source=s)[0], dtype=float)
        d = d[np.isfinite(d) & (d > 0)]
        toplam += d.sum()
        sayi += d.size
        cap = max(cap, int(d.max()) if d.size else 0)
    return toplam / sayi, cap, False


def kaydet_json(obj, ad: str):
    def donustur(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    (SONUC / ad).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=donustur), encoding="utf-8")
