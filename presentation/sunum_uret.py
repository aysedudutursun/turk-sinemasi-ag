"""
sunum_uret.py
Sunum slaytlarını (16:9 HTML -> PDF) üretir. Tüm sayılar results/ ve data/processed/ dosyalarından okunur.
Çalıştırma: python presentation/sunum_uret.py   (Playwright + Chromium gerekir)
"""
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parents[1]
R, F, P = KOK / "results", KOK / "figures", KOK / "presentation"
IMG = P / "img"
IMG.mkdir(parents=True, exist_ok=True)

RED, BLUE, INK, MUTED, BG, GREEN = "#c0392b", "#2874a6", "#1d1b18", "#6b645b", "#fbf8f3", "#239b56"
plt.rcParams.update({"font.family": "Inter", "font.size": 15, "axes.edgecolor": "#cfc8bc",
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": BG,
                     "axes.facecolor": BG, "savefig.facecolor": BG})


def tr(x, d=2):
    """Türkçe ondalık biçim: 3.44 -> 3,44 ; binlik ayırıcı nokta."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------------------------------------------------------ veriler
tm = json.loads((R / "temel_olculer.json").read_text(encoding="utf-8"))
t, dd = tm["temel"], tm["derece_dagilimi"]
tn = json.loads((R / "topluluk_null.json").read_text(encoding="utf-8"))
nm = tn["null_model"]["olcular"]
zm = pd.read_csv(R / "zamansal_kucuk_dunya.csv")
kp = json.loads((R / "kopru_testi.json").read_text(encoding="utf-8"))
adlar = json.loads((R / "topluluk_adlari.json").read_text(encoding="utf-8"))
ilk_bt = pd.read_csv(R / "ilk10_betweenness.csv")
ilk_d = pd.read_csv(R / "ilk10_derece.csv")
toplama = json.loads((KOK / "data" / "raw" / "toplama_bilgisi.json").read_text(encoding="utf-8"))
fo = pd.read_csv(KOK / "data" / "processed" / "film_oyuncu_temiz.csv")
kadro = fo.groupby("film_qid").size()

# topluluklar arası kenar sayıları
uy = pd.read_csv(R / "topluluk_uyelik.csv").set_index("qid").topluluk
ken = pd.read_csv(KOK / "data" / "processed" / "kenar_listesi.csv")
ken = ken[ken.kaynak.isin(uy.index) & ken.hedef.isin(uy.index)]
ka, kb = ken.kaynak.map(uy), ken.hedef.map(uy)


def arasi(a, b):
    return int(((ka == a) & (kb == b)).sum() + ((ka == b) & (kb == a)).sum())


YESIL, YENI, SUNAL = 1, 0, 2          # topluluk_adlari.json'daki kimlikler
k_yy, k_ys, k_sy = arasi(YESIL, YENI), arasi(YESIL, SUNAL), arasi(SUNAL, YENI)

boy = uy.value_counts()
ozet = {c["topluluk"]: c for c in tn["en_buyuk_topluluklar"]}

# ------------------------------------------------------------------ şekiller
# 1) ağ görseli: poster PDF'inden ağ panelini kırp
subprocess.run(["pdftoppm", "-r", "170", "-png", "-singlefile", str(F / "poster_A3.pdf"), str(IMG / "poster_tam")], check=True)
from PIL import Image
im = Image.open(IMG / "poster_tam.png")
W, H = im.size
im.crop((int(.03 * W), int(.105 * H), int(.97 * W), int(.575 * H))).save(IMG / "ag.png")

# 2) null model histogramları
nd = pd.read_csv(R / "null_model_dagilim.csv")
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
for a, kol, baslik in [(ax[0], "ortalama_yerel_kumelenme", "Kümelenme katsayısı"),
                       (ax[1], "modularite_louvain", "Modülerlik (Louvain)")]:
    a.hist(nd[kol], bins=15, color="#9a948a", label="100 rastgele ağ")
    a.axvline(nm[kol]["gozlenen"], color=RED, lw=3, label="Türk sineması")
    a.set_xlim(0, max(nm[kol]["gozlenen"] * 1.15, nd[kol].max() * 1.15))
    a.set_title(f"{baslik}\nz = {tr(nm[kol]['z'], 0)}", fontsize=16, loc="left", color=INK)
    a.set_yticks([])
    a.spines["left"].set_visible(False)
ax[0].legend(frameon=False, fontsize=13, loc="upper center")
fig.tight_layout()
fig.savefig(IMG / "null.png", dpi=200)
plt.close(fig)

# 3) kafes - küçük dünya - rastgele şeması (Watts-Strogatz, n=20, k=4)
fig, ax = plt.subplots(1, 3, figsize=(11, 3.9))
for a, p, ad in [(ax[0], 0, "Kafes\nkümeli ama yollar uzun"),
                 (ax[1], 0.12, "Küçük dünya\nkümeli VE yollar kısa"),
                 (ax[2], 1.0, "Rastgele\nyollar kısa ama kümesiz")]:
    G = nx.connected_watts_strogatz_graph(30, 4, p, seed=16)   # Watts-Strogatz örneği (n=30, k=4)
    pos = nx.circular_layout(G)
    nx.draw_networkx_edges(G, pos, ax=a, edge_color="#b5aea3", width=1.4)
    nx.draw_networkx_nodes(G, pos, ax=a, node_size=60, node_color=BLUE if p != .12 else RED)
    C, L = nx.average_clustering(G), nx.average_shortest_path_length(G)
    a.set_title(ad, fontsize=15, color=INK)
    a.text(0.5, -0.08, f"C = {tr(C)}   L = {tr(L)}", transform=a.transAxes, ha="center", fontsize=14, color=MUTED)
    a.axis("off")
fig.tight_layout()
fig.savefig(IMG / "sema.png", dpi=200)
plt.close(fig)

# 4) σ ve ω zaman grafiği
x = zm.dilim.str.replace("–", "–\n", regex=False)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
ax[0].bar(x, zm.sigma, color=BLUE)
ax[0].errorbar(x, zm.sigma, yerr=[zm.sigma - zm.sigma_p2_5, zm.sigma_p97_5 - zm.sigma], fmt="none", ecolor=INK, capsize=3)
ax[0].axhline(1, color=RED, ls="--", lw=2)
ax[0].text(7.4, 1.25, "σ = 1", color=RED, fontsize=13, ha="right")
ax[0].set_title("σ: her on yılda 1'in üstünde", fontsize=16, loc="left", color=INK)
ax[1].plot(x, zm.omega, "o-", color=GREEN, lw=2.5, ms=8)
ax[1].axhline(0, color=RED, ls="--", lw=2)
ax[1].set_ylim(-1, 1)
ax[1].text(0, .85, "+1 rastgele", fontsize=12, color=MUTED)
ax[1].text(0, -.92, "−1 kafes", fontsize=12, color=MUTED)
ax[1].set_title("ω: sıfırın altında, kümeli tarafta", fontsize=16, loc="left", color=INK)
for a in ax:
    a.tick_params(labelsize=11)
fig.tight_layout()
fig.savefig(IMG / "sigma_omega.png", dpi=200)
plt.close(fig)

# 5) ayrım derecesi ve dev bileşen
fig, ax = plt.subplots(figsize=(6.2, 4.4))
ax.plot(x, zm.L, "o-", color=BLUE, lw=2.5, ms=7, label="Gözlenen L")
ax.plot(x, zm.L_r, "s--", color="#9a948a", lw=2, label="Rastgele L")
ax.set_title("Ortalama ayrım derecesi (adım)", fontsize=16, loc="left", color=INK)
ax.legend(frameon=False, fontsize=12)
ax.tick_params(labelsize=10)
fig.tight_layout()
fig.savefig(IMG / "L.png", dpi=200)
plt.close(fig)

# ------------------------------------------------------------------ slaytlar
s_all = (nm["ortalama_yerel_kumelenme"]["gozlenen"] / nm["ortalama_yerel_kumelenme"]["null_ort"]) / \
        (nm["ortalama_yol"]["gozlenen"] / nm["ortalama_yol"]["null_ort"])
tek = kp["tekli"][0]
bes = [b for b in kp["birlikte"] if b["k"] == 5][0]
lognorm = dd["karsilastirma"]["lognormal"]
z_min = min(nm["ortalama_yerel_kumelenme"]["z"], nm["modularite_louvain"]["z"], nm["transitivity"]["z"])
z2020 = zm[zm.bas == 2020].iloc[0]
s_min, s_max = zm.sigma.min(), zm.sigma.max()
gc_pct = t["dev_bilesen_payi"] * 100
lv, ld = tn["louvain"], tn["leiden"]


def kart(sayi, alt, renk=RED):
    return f'<div class="kart"><b style="color:{renk}">{sayi}</b><span>{alt}</span></div>'


slaytlar = []

# 1 — Soru
slaytlar.append(f"""
<div class="kapak">
  <div class="ust">Sosyal Ağ Analizi · Dönem Ödevi</div>
  <h1 class="buyuk">Türk sineması bir küçük dünya: <br>{tr(t['dugum'],0)} oyuncu ortalama <span class="vurgu">{tr(t['ortalama_en_kisa_yol_gc'])} adımla</span> birbirine bağlı</h1>
  <div class="soru"><b>Araştırma sorusu:</b> Türk sineması bir “küçük dünya” mı?
  Yeşilçam’dan bugüne oyuncu ağının yapısı nasıl değişti?</div>
  <div class="imza">Ayşe Dudu Tursun · Manisa Celal Bayar Üniversitesi · Büyük Veri Analistliği</div>
</div>""")

# 2 — Veri ve ağ
slaytlar.append(f"""
<h1>Wikidata’daki {tr(toplama['film_sayisi_yilli_aralikta'],0)} Türk filminin {tr(toplama['p161_olan_film'],0)}’ünden {tr(t['dugum'],0)} oyunculu bir ağ kurdum</h1>
<div class="iki">
 <div>
  <div class="akis">
    <div class="adim"><b>1 · Toplama</b>Wikidata SPARQL (script, CC0): menşe ülke = Türkiye, film, 1950–2025, oyuncu (P161)</div>
    <div class="ok">↓</div>
    <div class="adim"><b>2 · İki parçalı ağ</b>{tr(toplama['p161_olan_film'],0)} film ↔ {tr(toplama['benzersiz_oyuncu'],0)} oyuncu, {tr(toplama['film_oyuncu_satiri'],0)} bağ</div>
    <div class="ok">↓</div>
    <div class="adim"><b>3 · Projeksiyon</b>Aynı filmde oynayan iki oyuncu arasına bağ → <b>{tr(t['kenar'],0)} kenar</b></div>
  </div>
 </div>
 <div>
  <h3>Kararlar ve gerekçeleri</h3>
  <ul>
   <li><b>Düğüm:</b> oyuncu (Wikidata kimliğiyle; aynı adlı iki kişi karışmaz)</li>
   <li><b>Yön yok:</b> birlikte oynamak karşılıklı bir ilişki</li>
   <li><b>Ağırlık:</b> ortak film sayısı (en güçlü bağ: {ken.agirlik.max()} ortak film)</li>
   <li><b>Zaman:</b> her bağın ilk ve son ortak film yılı saklandı → on yıllık ağlar</li>
  </ul>
  <p class="not">Kenar listesi (CSV), GraphML ve veri sözlüğü depoda.</p>
 </div>
</div>""")

# 3 — Temel yapı
slaytlar.append(f"""
<h1>Oyuncuların %{tr(gc_pct,0)}’i tek bir dev bileşende; en uzak iki oyuncu bile {t['cap_gc']} adım uzakta</h1>
<div class="iki genis-sag">
 <div class="kartlar dikey">
  {kart(tr(t['ortalama_en_kisa_yol_gc']), 'ortalama ayrım derecesi: iki oyuncu arasında ortalama 3–4 “birlikte oynadı” adımı')}
  {kart(tr(nm['ortalama_yerel_kumelenme']['gozlenen']), 'kümelenme: bir oyuncunun iki partneri büyük olasılıkla birbiriyle de oynamış', BLUE)}
  {kart(tr(t['derece_assortativity']), 'derece benzeşimi ≈ 0: çok bağlı oyuncular özellikle birbirini seçmiyor', MUTED)}
  {kart('%' + tr(t['yogunluk']*100,2), 'yoğunluk: olası bağların çok küçük bir kısmı var (seyrek ağ)', MUTED)}
 </div>
 <div>
  <img src="../figures/derece_dagilimi.png" class="sekil">
  <p class="not">Derece dağılımı ağır kuyruklu ama <b>kuvvet yasası değil</b>: log-normal daha iyi uyuyor
  (R = {tr(lognorm['R'])}, p &lt; 0,001). Ağ “ölçekten bağımsız” değil; çok bağlı oyuncu sayısı sınırlı.</p>
 </div>
</div>""")

# 4 — Merkeziyet + köprü testi + canlı gösterim
satir = "".join(f"<tr><td>{i+1}</td><td>{r.ad}</td><td>{tr(r.betweenness,3)}</td><td>{r.film_sayisi}</td><td>{r.ilk_yil}–{r.son_yil}</td></tr>"
                for i, r in enumerate(ilk_bt.head(5).itertuples()))
slaytlar.append(f"""
<h1>Cüneyt Arkın ağın merkezinde, ama Türk sineması ona bağımlı değil</h1>
<div class="iki">
 <div>
  <h3>En yüksek köprü (betweenness) değerleri</h3>
  <table><tr><th>#</th><th>Oyuncu</th><th>Betweenness</th><th>Film</th><th>Yıllar</th></tr>{satir}</table>
  <p class="not">Cüneyt Arkın: {ilk_d.iloc[0].derece} farklı partner (derece 1.), köprü değeri ikinciye göre ≈{tr(ilk_bt.betweenness.iloc[0]/ilk_bt.betweenness.iloc[1],1)} kat.</p>
 </div>
 <div>
  <h3>“Bu oyuncu olmasaydı?” testi</h3>
  <div class="kartlar">
   {kart(str(tek['kopan']), 'Cüneyt Arkın çıkarılınca ağdan kopan oyuncu')}
   {kart(tr(kp['temel']['L']) + ' → ' + tr(tek['L']), 'ortalama ayrım derecesi', BLUE)}
  </div>
  <p>İlk 5 köprü oyuncu birlikte çıkarılınca yalnızca <b>{bes['kopan']}</b> oyuncu kopuyor
  (rastgele 5 oyuncu: ortalama {tr(bes['rastgele_kopan_ort'],1)}). Yollar biraz uzuyor ama alternatif yollar var.</p>
  <div class="canli">▶ Canlı gösterim: etkileşimli ağda <b>Cüneyt Arkın</b> ve <b>Şener Şen</b>’i arayıp partnerlerini ve topluluklarını göster.</div>
 </div>
</div>""")

# 5 — Topluluklar
sira = [c["topluluk"] for c in tn["en_buyuk_topluluklar"]]   # en büyük 6 topluluk (özeti olanlar)
POSTER_PAL = ["#c0392b", "#2874a6", "#239b56", "#d68910", "#7d3c98", "#d63384", "#17a589", "#6e2c00", "#5d6d7e"]
boy_sira = sorted(boy.index, key=lambda c: (-boy[c], c))
renkler = [POSTER_PAL[boy_sira.index(c)] for c in [c["topluluk"] for c in tn["en_buyuk_topluluklar"]]]   # posterle aynı renk
liste = ""
for c, rk in zip(sira, renkler):
    o = ozet.get(int(c))
    yil = f"film yılı ortancası {int(o['film_yili_medyan'])}" if o else ""
    liste += (f'<li><span class="kare" style="background:{rk}"></span><b>{adlar.get(str(c),{}).get("tr",f"Topluluk {c}")}</b>'
              f'<br><span class="gri girinti">{boy[c]} oyuncu · {yil}</span></li>')
slaytlar.append(f"""
<h1>Ağ dönemlere ayrışıyor: Yeşilçam ile 2000’ler arasındaki köprüyü Kemal Sunal – Şener Şen çevresi kuruyor</h1>
<div class="iki genis-sag">
 <div>
  <ul class="topluluk">{liste}</ul>
  <div class="kartlar uc">
   {kart(str(k_yy), 'Yeşilçam ↔ 2000’ler doğrudan bağ', MUTED)}
   {kart(str(k_ys), 'Yeşilçam ↔ Sunal–Şen', BLUE)}
   {kart(str(k_sy), 'Sunal–Şen ↔ 2000’ler', BLUE)}
  </div>
  <p class="not">Leiden modülerlik {tr(tn['referans']['modularite'])} · Louvain {tr(lv['modularite_ort'])} ·
  10 tohumda kararlılık NMI ≈ {tr(ld['nmi_ort'])} (Leiden), {tr(lv['nmi_ort'])} (Louvain) — orta-iyi.</p>
 </div>
 <div><img src="img/ag.png" class="sekil"></div>
</div>""")

# 6 — Null model
slaytlar.append(f"""
<h1>Bu yapı tesadüf değil: 100 rastgele ağın hiçbiri bu kadar kümeli ve modüler olmuyor</h1>
<img src="img/null.png" class="sekil orta">
<div class="kartlar uc">
 {kart(tr(nm['ortalama_yerel_kumelenme']['gozlenen']) + ' / ' + tr(nm['ortalama_yerel_kumelenme']['null_ort']), 'kümelenme: gerçek / rastgele (≈' + tr(nm['ortalama_yerel_kumelenme']['gozlenen']/nm['ortalama_yerel_kumelenme']['null_ort'],0) + ' kat)')}
 {kart(tr(nm['modularite_louvain']['gozlenen']) + ' / ' + tr(nm['modularite_louvain']['null_ort']), 'modülerlik: gerçek / rastgele', BLUE)}
 {kart(tr(nm['ortalama_yol']['gozlenen']) + ' / ' + tr(nm['ortalama_yol']['null_ort']), 'ortalama yol: gerçek / rastgele (aynı büyüklükte)', MUTED)}
</div>
<p class="not">Rastgele ağlar: aynı derece dizisine sahip, bağlı configuration model (Viger–Latapy), 100 adet.
Herkes aynı sayıda partnere sahip olsaydı bile bu kümelenme ortaya çıkmazdı.</p>""")

# 7 — Yöntem: σ ve ω
slaytlar.append(f"""
<h1>Küçük dünya = kafese yakın kümeli, rastgele ağa yakın kısa yollu; σ ve ω bunu ölçüyor</h1>
<img src="img/sema.png" class="sekil orta">
<div class="iki">
 <div class="formul"><b>σ = (C / C<sub>rastgele</sub>) ÷ (L / L<sub>rastgele</sub>)</b><br>
 σ &gt; 1 → küçük dünya. Tüm ağ için: ({tr(nm['ortalama_yerel_kumelenme']['gozlenen'])} / {tr(nm['ortalama_yerel_kumelenme']['null_ort'])}) ÷ ({tr(nm['ortalama_yol']['gozlenen'])} / {tr(nm['ortalama_yol']['null_ort'])}) ≈ <b>{tr(s_all,1)}</b></div>
 <div class="formul"><b>ω = L<sub>rastgele</sub> / L − C / C<sub>kafes</sub></b><br>
 ω ≈ 0 küçük dünya · −1’e yakın kafes · +1’e yakın rastgele. σ ağ büyüdükçe kendiliğinden büyüdüğü için ω’yı da hesapladım.</div>
</div>
<p class="not">Her on yıl için: o on yılın filmlerinden ağ kur → dev bileşen → 100 rastgele ağ ile C<sub>r</sub>, L<sub>r</sub>; aynı boyutta halka kafes ile C<sub>kafes</sub>.</p>""")

# 8 — Zamansal sonuç
slaytlar.append(f"""
<h1>Yeşilçam’dan bugüne her on yılda σ &gt; 1: küçük dünya yapısı hiç kaybolmamış</h1>
<img src="img/sigma_omega.png" class="sekil orta">
<div class="iki">
 <p>σ en düşük {tr(s_min,1)}, en yüksek {tr(s_max,1)}. 2000’ler ve 2010’lardaki yükselişin önemli kısmı ağın büyümesinden
 (rastgele kümelenme C<sub>r</sub> {tr(zm.C_r.iloc[0])} → {tr(zm[zm.bas==2010].C_r.iloc[0])}).</p>
 <p>Ayrım derecesi Yeşilçam’da {tr(zm.L.iloc[0])}–{tr(zm[zm.bas==1970].L.iloc[0])}, 2010’larda {tr(zm[zm.bas==2010].L.iloc[0])}: dünya küçük kaldı ama biraz “uzadı”.
 ω hep negatif: ağ rastgeleden çok kümeli tarafa yakın.</p>
</div>""")

# 9 — Cevap ve sınırlar
slaytlar.append(f"""
<h1>Cevap: Evet, Türk sineması bir küçük dünya — ama veri ünlü oyunculara doğru yanlı</h1>
<div class="iki">
 <div>
  <h3>Cevap</h3>
  <ul>
   <li>Her on yılda σ &gt; 1 ({tr(s_min,1)}–{tr(s_max,1)}); tüm ağda σ ≈ {tr(s_all,1)}</li>
   <li>Kümelenme rastgelenin ≈{tr(nm['ortalama_yerel_kumelenme']['gozlenen']/nm['ortalama_yerel_kumelenme']['null_ort'],0)} katı, yollar neredeyse aynı kısa ({tr(nm['ortalama_yol']['gozlenen'])} / {tr(nm['ortalama_yol']['null_ort'])})</li>
   <li>Yapı değişti: dönem toplulukları oluştu, ayrım derecesi {tr(zm.L.iloc[0])} → {tr(zm[zm.bas==2010].L.iloc[0])}</li>
   <li>Dev bileşen birikimli ağda hep %{tr(zm.birikimli_gc_pay.min()*100,0)}–{tr(zm.birikimli_gc_pay.max()*100,0)}; mutlak boyut {tr(zm.birikimli_oyuncu.iloc[0]*zm.birikimli_gc_pay.iloc[0],0)} → {tr(t['dev_bilesen_dugum'],0)} oyuncu</li>
  </ul>
 </div>
 <div>
  <h3>Sınırlar</h3>
  <ul>
   <li>Kadrolar eksik: film başına ortanca <b>{int(kadro.median())}</b> oyuncu kayıtlı → başroller ağırlıkta</li>
   <li>{tr(toplama['yili_olmayan_film'],0)} filmin yılı yok, {tr(toplama['film_sayisi_yilli_aralikta']-toplama['p161_olan_film'],0)} filmin kadrosu yok</li>
   <li>2020–2025 dilimi eksik: {int(z2020.film)} film, dev bileşen yalnızca %{tr(z2020.gc_pay*100,0)}</li>
   <li>σ ağ boyutuna duyarlı; ω’da kafes yaklaşık (halka kafes)</li>
   <li>Ağ ilişki gösterir, <b>nedensellik</b> iddia etmez</li>
  </ul>
 </div>
</div>
<div class="kartlar uc" style="margin-top:34px">
 {kart(tr(s_min,1) + '–' + tr(s_max,1), 'on yıllık ağlarda σ (hepsi 1’in üstünde)')}
 {kart('≈' + tr(nm['ortalama_yerel_kumelenme']['gozlenen']/nm['ortalama_yerel_kumelenme']['null_ort'],0) + ' kat', 'kümelenme, rastgele ağlara göre', BLUE)}
 {kart(tr(t['ortalama_en_kisa_yol_gc']) + ' adım', 'iki oyuncu arası ortalama uzaklık', MUTED)}
</div>""")

CSS = """
@page{size:1280px 720px;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,'DejaVu Sans',sans-serif;color:#1d1b18;background:#fbf8f3}
.s{width:1280px;height:720px;padding:46px 60px 40px;position:relative;overflow:hidden;page-break-after:always;background:#fbf8f3}
.s:before{content:"";position:absolute;left:0;top:0;width:10px;height:100%;background:#c0392b}
h1{font-size:33px;line-height:1.18;margin:0 0 22px;font-weight:700;letter-spacing:-.01em;max-width:1140px}
h3{font-size:19px;margin:0 0 10px;color:#2874a6;text-transform:uppercase;letter-spacing:.04em}
p,li{font-size:19px;line-height:1.4}
ul{margin:0;padding-left:22px} li{margin:0 0 8px}
.iki{display:grid;grid-template-columns:1fr 1fr;gap:36px;align-items:start}
.genis-sag{grid-template-columns:.85fr 1.15fr}
.sekil{width:100%;border-radius:6px}
.orta{display:block;margin:0 auto 14px;max-height:330px;width:auto;max-width:100%}
.not{font-size:16px;color:#6b645b;margin-top:10px}
.kartlar{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:6px 0 12px}
.kartlar.uc{grid-template-columns:1fr 1fr 1fr}
.kartlar.dikey{grid-template-columns:1fr;gap:12px}
.kart{background:#fff;border:1px solid #e3ddd3;border-radius:10px;padding:12px 16px}
.kart b{display:block;font-size:30px;line-height:1.1;font-variant-numeric:tabular-nums}
.kart span{font-size:15px;color:#6b645b;line-height:1.3;display:block;margin-top:3px}
table{border-collapse:collapse;width:100%;font-size:17px}
th{text-align:left;color:#6b645b;font-weight:600;border-bottom:2px solid #1d1b18;padding:6px 8px}
td{padding:6px 8px;border-bottom:1px solid #e3ddd3;font-variant-numeric:tabular-nums}
.akis{display:flex;flex-direction:column;gap:6px}
.adim{background:#fff;border:1px solid #e3ddd3;border-left:6px solid #2874a6;border-radius:8px;padding:14px 18px;font-size:18px;line-height:1.35}
.adim b{display:block;font-size:20px;margin-bottom:3px}
.ok{text-align:center;font-size:24px;color:#c0392b;line-height:1}
.canli{margin-top:14px;background:#1d1b18;color:#fbf8f3;border-radius:10px;padding:14px 18px;font-size:18px;line-height:1.35}
.topluluk{list-style:none;padding:0;margin:0 0 14px}
.topluluk li{font-size:17px;margin:0 0 6px;line-height:1.25}
.girinti{margin-left:23px}
.kare{display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:9px;vertical-align:-1px}
.gri{color:#6b645b;font-size:15px}
.formul{background:#fff;border:1px solid #e3ddd3;border-radius:10px;padding:14px 18px;font-size:17px;line-height:1.45}
.formul b{font-size:20px}
.kapak{display:flex;flex-direction:column;justify-content:center;height:100%;padding-left:20px}
.ust{font-size:18px;color:#6b645b;letter-spacing:.08em;text-transform:uppercase;margin-bottom:24px}
.buyuk{font-size:52px;line-height:1.12;margin-bottom:34px}
.vurgu{color:#c0392b}
.soru{font-size:24px;line-height:1.45;max-width:1000px;border-left:4px solid #2874a6;padding-left:20px}
.imza{position:absolute;bottom:40px;left:80px;font-size:17px;color:#6b645b}
.sayfa{position:absolute;right:40px;bottom:22px;font-size:14px;color:#9a948a}
"""
html = "<!doctype html><html lang='tr'><head><meta charset='utf-8'><style>" + CSS + "</style></head><body>"
for i, s in enumerate(slaytlar, 1):
    html += f'<section class="s">{s}<div class="sayfa">{i} / {len(slaytlar)}</div></section>'
html += "</body></html>"
(P / "sunum.html").write_text(html, encoding="utf-8")

js = f"""
const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{(P / "sunum.html").as_posix()}');await p.waitForTimeout(800);
await p.pdf({{path:'{(P / "sunum.pdf").as_posix()}',width:'1280px',height:'720px',printBackground:true}});await b.close()}})();"""
subprocess.run(["node", "-e", js], check=True)
print(f"sunum.pdf yazıldı: {len(slaytlar)} slayt")
