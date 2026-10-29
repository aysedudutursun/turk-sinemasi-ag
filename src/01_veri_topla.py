"""
01_veri_topla.py
Wikidata SPARQL'den Türk yapımı filmleri (1950-2025) ve oyuncularını (P161) toplar.

Çıktılar (data/raw/):
  filmler.csv          film_qid, film_adi, yil  (yil = en erken yayın yılı, P577)
  film_oyuncu.csv      film_qid, oyuncu_qid, oyuncu_adi   (P161 "cast member")
  oyuncular.csv        oyuncu_qid, oyuncu_adi, cinsiyet, dogum_yili
  toplama_bilgisi.json sorgu zamanı, kaynak, lisans, satır sayıları

Kurallar:
  - Film: P31/P279* Q11424 (film veya alt sınıfı) VE P495 (menşe ülke) = Q43 (Türkiye)
  - Yıl: P577 (yayın tarihi) değerlerinin en küçüğü; 1950 <= yıl <= 2025
  - Hız sınırı: istekler arası bekleme + tanımlayıcı User-Agent (Wikidata kuralı)
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "TurkSinemasiAgi/1.0 (MCBU Sosyal Ag Analizi ders odevi; egitim amacli)",
}
YIL_MIN, YIL_MAX = 1950, 2025
BEKLEME = 1.5          # saniye, istekler arası
PARTI = 250            # VALUES içindeki QID sayısı

KOK = Path(__file__).resolve().parents[1]
RAW = KOK / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def sparql(sorgu: str, deneme: int = 5) -> list[dict]:
    for i in range(deneme):
        try:
            r = requests.post(ENDPOINT, data={"query": sorgu}, headers=HEADERS, timeout=120)
            if r.status_code == 429 or r.status_code >= 500:
                bekle = int(r.headers.get("Retry-After", 10 * (i + 1)))
                print(f"  HTTP {r.status_code}, {bekle} sn bekleniyor...")
                time.sleep(bekle)
                continue
            r.raise_for_status()
            time.sleep(BEKLEME)
            return r.json()["results"]["bindings"]
        except requests.RequestException as e:
            print(f"  hata: {e}; tekrar deneniyor")
            time.sleep(10 * (i + 1))
    raise RuntimeError("SPARQL sorgusu başarısız oldu")


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def deger(b: dict, k: str):
    return b[k]["value"] if k in b else None


# ---------------------------------------------------------------- 1) Filmler
FILM_SORGU = """
SELECT ?film ?filmLabel ?tarih WHERE {
  ?film wdt:P495 wd:Q43 ;
        wdt:P31/wdt:P279* wd:Q11424 .
  OPTIONAL { ?film wdt:P577 ?tarih . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "tr,en,mul". }
}
"""


def filmleri_topla() -> pd.DataFrame:
    print("Filmler sorgulanıyor...")
    rows = []
    for b in sparql(FILM_SORGU):
        t = deger(b, "tarih")
        yil = None
        m = re.match(r"^\+?(\d{4})-", t or "")     # "1975-03-01T00:00:00Z"; bilinmeyen değerler eşleşmez
        if m:
            yil = int(m.group(1))
        rows.append({"film_qid": qid(b["film"]["value"]), "film_adi": deger(b, "filmLabel"), "yil": yil})
    df = pd.DataFrame(rows)
    print(f"  ham satır: {len(df)}, benzersiz film: {df.film_qid.nunique()}")
    # her film için en erken yıl
    yillar = df.groupby("film_qid")["yil"].min()
    adlar = df.groupby("film_qid")["film_adi"].first()
    filmler = pd.DataFrame({"film_adi": adlar, "yil": yillar}).reset_index()
    filmler["yil_yok"] = filmler["yil"].isna()
    return filmler


# ---------------------------------------------------------------- 2) Oyuncular (P161)
def oyunculari_topla(film_qids: list[str]) -> pd.DataFrame:
    print(f"P161 oyuncu bilgisi {len(film_qids)} film için sorgulanıyor...")
    rows = []
    for i in range(0, len(film_qids), PARTI):
        parca = film_qids[i:i + PARTI]
        values = " ".join(f"wd:{q}" for q in parca)
        s = f"""
        SELECT ?film ?oyuncu ?oyuncuLabel WHERE {{
          VALUES ?film {{ {values} }}
          ?film wdt:P161 ?oyuncu .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "tr,en,mul". }}
        }}"""
        for b in sparql(s):
            rows.append({
                "film_qid": qid(b["film"]["value"]),
                "oyuncu_qid": qid(b["oyuncu"]["value"]),
                "oyuncu_adi": deger(b, "oyuncuLabel"),
            })
        print(f"  {min(i + PARTI, len(film_qids))}/{len(film_qids)}")
    return pd.DataFrame(rows).drop_duplicates(["film_qid", "oyuncu_qid"])


# ---------------------------------------------------------------- 3) Oyuncu nitelikleri
def nitelikleri_topla(oyuncu_qids: list[str]) -> pd.DataFrame:
    print(f"{len(oyuncu_qids)} oyuncunun cinsiyet/doğum yılı sorgulanıyor...")
    rows = []
    for i in range(0, len(oyuncu_qids), PARTI):
        parca = oyuncu_qids[i:i + PARTI]
        values = " ".join(f"wd:{q}" for q in parca)
        s = f"""
        SELECT ?o ?oLabel ?cinsiyetLabel (MIN(YEAR(?d)) AS ?dy) WHERE {{
          VALUES ?o {{ {values} }}
          OPTIONAL {{ ?o wdt:P21 ?cinsiyet . }}
          OPTIONAL {{ ?o wdt:P569 ?d . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "tr,en,mul".
                                   ?o rdfs:label ?oLabel . ?cinsiyet rdfs:label ?cinsiyetLabel . }}
        }} GROUP BY ?o ?oLabel ?cinsiyetLabel"""
        for b in sparql(s):
            dy = deger(b, "dy")
            rows.append({
                "oyuncu_qid": qid(b["o"]["value"]),
                "oyuncu_adi": deger(b, "oLabel"),
                "cinsiyet": deger(b, "cinsiyetLabel"),
                "dogum_yili": int(float(dy)) if dy else None,
            })
        print(f"  {min(i + PARTI, len(oyuncu_qids))}/{len(oyuncu_qids)}")
    return pd.DataFrame(rows).drop_duplicates("oyuncu_qid")


def main():
    zaman = datetime.now(timezone.utc).isoformat(timespec="seconds")
    filmler_tum = filmleri_topla()
    filmler = filmler_tum[(filmler_tum.yil >= YIL_MIN) & (filmler_tum.yil <= YIL_MAX)].copy()
    filmler["yil"] = filmler["yil"].astype(int)
    print(f"Yılı {YIL_MIN}-{YIL_MAX} arası film: {len(filmler)} "
          f"(yılı olmayan: {int(filmler_tum.yil_yok.sum())}, aralık dışı: "
          f"{int((~filmler_tum.yil_yok).sum() - len(filmler))})")

    fo = oyunculari_topla(filmler.film_qid.tolist())
    oy = nitelikleri_topla(sorted(fo.oyuncu_qid.unique()))

    filmler.drop(columns="yil_yok").to_csv(RAW / "filmler.csv", index=False)
    fo.to_csv(RAW / "film_oyuncu.csv", index=False)
    oy.to_csv(RAW / "oyuncular.csv", index=False)

    bilgi = {
        "toplama_zamani_utc": zaman,
        "kaynak": ENDPOINT,
        "lisans": "Wikidata verisi CC0 1.0 (kamu malı) lisanslıdır",
        "film_tanimi": "P31/P279* Q11424 ve P495 = Q43",
        "yil_araligi": [YIL_MIN, YIL_MAX],
        "film_sayisi_tum": int(len(filmler_tum)),
        "film_sayisi_yilli_aralikta": int(len(filmler)),
        "yili_olmayan_film": int(filmler_tum.yil_yok.sum()),
        "p161_olan_film": int(fo.film_qid.nunique()),
        "film_oyuncu_satiri": int(len(fo)),
        "benzersiz_oyuncu": int(fo.oyuncu_qid.nunique()),
    }
    (RAW / "toplama_bilgisi.json").write_text(json.dumps(bilgi, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(bilgi, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
