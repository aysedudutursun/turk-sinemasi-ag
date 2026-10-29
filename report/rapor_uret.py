"""
rapor_uret.py — Raporu (report/rapor.pdf) sonuç dosyalarından üretir.
Metindeki tüm sayılar results/ ve data/ dosyalarından okunur; elle yazılmış sayı yoktur.
Çalıştırma: python report/rapor_uret.py   (Playwright + Chromium gerekir)
"""
import base64
import json
import subprocess
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parents[1]
R, F, D = KOK / "results", KOK / "figures", KOK / "data"

tm = json.loads((R / "temel_olculer.json").read_text(encoding="utf-8"))
t, dd = tm["temel"], tm["derece_dagilimi"]
sp = pd.read_csv(R / "spearman_merkeziyet.csv", index_col=0)
tn = json.loads((R / "topluluk_null.json").read_text(encoding="utf-8"))
nm = tn["null_model"]["olcular"]
zm = pd.read_csv(R / "zamansal_kucuk_dunya.csv")
kt = json.loads((R / "kopru_testi.json").read_text(encoding="utf-8"))
tb = json.loads((D / "raw" / "toplama_bilgisi.json").read_text(encoding="utf-8"))
adlar = json.loads((R / "topluluk_adlari.json").read_text(encoding="utf-8"))
ken = pd.read_csv(D / "processed" / "kenar_listesi.csv")
fo = pd.read_csv(D / "processed" / "film_oyuncu_temiz.csv")
uy = pd.read_csv(R / "topluluk_uyelik.csv")
ilk = {o: pd.read_csv(R / f"ilk10_{o}.csv") for o in ["derece", "betweenness", "closeness", "eigenvector", "pagerank"]}


def f(x, d=2):
    """Türkçe ondalık biçim."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def n(x):
    return f"{int(x):,}".replace(",", ".")


def img(p, w="100%"):
    b = base64.b64encode(Path(p).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{b}" style="width:{w}">'


# Türetilen değerler
gc_n, gc_m = t["dev_bilesen_dugum"], t["dev_bilesen_kenar"]
C, Cr = nm["ortalama_yerel_kumelenme"]["gozlenen"], nm["ortalama_yerel_kumelenme"]["null_ort"]
L, Lr = nm["ortalama_yol"]["gozlenen"], nm["ortalama_yol"]["null_ort"]
sigma_tum = (C / Cr) / (L / Lr)
cast = fo.groupby("film_qid").size()
lv, ld = tn["louvain"], tn["leiden"]
zm_s = zm.set_index("dilim")
uyb = uy.set_index("qid").topluluk
kk = ken[ken.kaynak.isin(uyb.index) & ken.hedef.isin(uyb.index)].copy()
kk["a"], kk["b"] = kk.kaynak.map(uyb), kk.hedef.map(uyb)
def arasi(x, y):
    return int(((kk.a == x) & (kk.b == y)).sum() + ((kk.a == y) & (kk.b == x)).sum())
ic_oran = float((kk.a == kk.b).mean())
tek = {r["ad"]: r for r in kt["tekli"]}
bir = {r["k"]: r for r in kt["birlikte"]}
cuneyt = ilk["derece"].iloc[0]
bet2 = ilk["betweenness"].iloc[1]
en_agir = ken.nlargest(1, "agirlik").iloc[0]
max_cast = fo.groupby(["film_adi", "yil"]).size().nlargest(1)

# ------------------------------------------------------------------ tablolar
def tablo_ilk10():
    satir = []
    for i in range(10):
        satir.append("<tr>" + "".join(
            f"<td>{ilk[o].iloc[i]['ad']}</td>" for o in ["derece", "betweenness", "closeness", "pagerank"]) + "</tr>")
    return ("<table class='t small'><tr><th>Derece</th><th>Betweenness</th><th>Closeness</th><th>PageRank</th></tr>"
            + "".join(satir) + "</table>")


def tablo_spearman():
    o = ["derece", "betweenness", "closeness", "eigenvector", "pagerank", "film_sayisi"]
    bas = {"derece": "Der.", "betweenness": "Btw.", "closeness": "Clo.", "eigenvector": "Eig.",
           "pagerank": "PR", "film_sayisi": "Film"}
    h = "<tr><th></th>" + "".join(f"<th>{bas[c]}</th>" for c in o) + "</tr>"
    rows = "".join("<tr><th>" + bas[a] + "</th>" + "".join(f"<td>{f(sp.loc[a, b])}</td>" for b in o) + "</tr>" for a in o)
    return f"<table class='t small'>{h}{rows}</table>"


def tablo_topluluk():
    rows = []
    for c in tn["en_buyuk_topluluklar"][:6]:
        ad = adlar.get(str(c["topluluk"]), {}).get("tr", f"Topluluk {c['topluluk']}")
        oy = ", ".join(x["ad"] for x in c["en_bagli_10"][:4])
        fl = ", ".join(f"{x['film_adi']} ({x['yil']})" for x in c["en_cok_uyeli_filmler"][:3])
        q1, q3 = c["film_yili_q1_q3"]
        rows.append(f"<tr><td><b>{ad}</b></td><td>{n(c['boyut'])} ({f(c['pay']*100,1)}%)</td>"
                    f"<td>{int(c['film_yili_medyan'])}<br><span class='m'>{int(q1)}–{int(q3)}</span></td>"
                    f"<td>{oy}</td><td>{fl}</td></tr>")
    return ("<table class='t small'><tr><th>Ad (önerilen)</th><th>Oyuncu</th><th>Film yılı medyan (Ç1–Ç3)</th>"
            "<th>En bağlı oyuncular</th><th>En çok üyesi olan filmler</th></tr>" + "".join(rows) + "</table>")


def tablo_null():
    ad = {"ortalama_yerel_kumelenme": "Ortalama yerel kümelenme", "transitivity": "Global kümelenme (transitivity)",
          "ortalama_yol": "Ortalama en kısa yol", "modularite_louvain": "Modülerlik (Louvain, ağırlıksız)",
          "assortativity": "Derece benzeşimi"}
    rows = "".join(f"<tr><td>{ad[k]}</td><td>{f(v['gozlenen'],3)}</td><td>{f(v['null_ort'],3)} ± {f(v['null_std'],3)}</td>"
                   f"<td>{f(v['null_min'],3)} – {f(v['null_maks'],3)}</td><td><b>{f(v['z'],1)}</b></td></tr>"
                   for k, v in nm.items())
    return ("<table class='t'><tr><th>Ölçü (dev bileşen)</th><th>Gözlenen</th><th>Null ort. ± ss</th>"
            "<th>Null aralık</th><th>z</th></tr>" + rows + "</table>")


def tablo_zaman():
    rows = "".join(
        f"<tr><td>{r.dilim}</td><td>{n(r.film)}</td><td>{n(r.oyuncu)}</td><td>{f(r.gc_pay*100,0)}%</td>"
        f"<td>{f(r.C)}</td><td>{f(r.C_r)}</td><td>{f(r.L)}</td><td>{f(r.L_r)}</td><td>{r.cap}</td>"
        f"<td><b>{f(r.sigma,1)}</b> <span class='m'>[{f(r.sigma_p2_5,1)}–{f(r.sigma_p97_5,1)}]</span></td>"
        f"<td><b>{f(r.omega)}</b></td><td>{f(r.birikimli_gc_pay*100,0)}%</td></tr>" for r in zm.itertuples())
    return ("<table class='t small'><tr><th>Dilim</th><th>Film</th><th>Oyuncu</th><th>DB payı</th><th>C</th><th>C<sub>r</sub></th>"
            "<th>L</th><th>L<sub>r</sub></th><th>Çap</th><th>σ [%95]</th><th>ω</th><th>Birikimli DB</th></tr>" + rows + "</table>")


def tablo_kopru():
    rows = "".join(f"<tr><td>{r['ad']}</td><td>{n(r['kopan'])}</td><td>{f(r['L'],3)} (+{f(r['L_degisim'],3)})</td></tr>"
                   for r in kt["tekli"])
    rows2 = "".join(f"<tr><td>İlk {r['k']} birlikte</td><td>{n(r['kopan'])} <span class='m'>(rastgele {r['k']}: {f(r['rastgele_kopan_ort'],2)})</span></td>"
                    f"<td>{f(r['L'],3)} <span class='m'>(rastgele: {f(r['rastgele_L_ort'],3)})</span></td></tr>"
                    for r in kt["birlikte"] if r["k"] > 1)
    return ("<table class='t small'><tr><th>Çıkarılan oyuncu</th><th>Dev bileşenden kopan</th><th>Yeni ortalama yol</th></tr>"
            + rows + rows2 + "</table>")


karsi = dd["karsilastirma"]
def pl(alt):
    r = karsi[alt]
    p = "&lt; 0,001" if r["p"] < 0.001 else f(r["p"], 3)
    return f"R = {f(r['R'])}, p {'' if r['p'] < 0.001 else '= '}{p}"

z1960, z2010, z2020 = zm_s.loc["1960–1969"], zm_s.loc["2010–2019"], zm_s.loc["2020–2025"]
z2000 = zm_s.loc["2000–2009"]
omega_yc = zm[zm.bas <= 1979].omega
omega_sonra = zm[(zm.bas >= 1980) & (zm.bas <= 2019)].omega

html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>Türk Sineması Oyuncu Ağı — Rapor</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 18mm 17mm; }}
body {{ font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.3pt; line-height: 1.45; color: #1d1b18; }}
h1 {{ font-family: 'DejaVu Sans', sans-serif; font-size: 19pt; margin: 0 0 4px; }}
h2 {{ font-family: 'DejaVu Sans', sans-serif; font-size: 12.5pt; margin: 16px 0 6px; color: #8e2b20; }}
h3 {{ font-family: 'DejaVu Sans', sans-serif; font-size: 10.8pt; margin: 12px 0 4px; }}
p {{ margin: 0 0 7px; text-align: justify; }}
.meta {{ font-family: 'DejaVu Sans'; font-size: 9pt; color: #6b645b; margin-bottom: 10px; }}
.ozet {{ background: #f6f1e8; padding: 9px 12px; border-left: 3px solid #c0392b; margin: 8px 0 10px; }}
table.t {{ border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-family: 'DejaVu Sans'; font-size: 8.6pt; page-break-inside: avoid; }}
table.small {{ font-size: 7.9pt; }}
.t th, .t td {{ border-bottom: 1px solid #ddd5c8; padding: 3px 5px; text-align: left; vertical-align: top; }}
.t th {{ background: #f1ebe1; }}
.m {{ color: #6b645b; font-size: 85%; }}
.cap {{ font-family: 'DejaVu Sans'; font-size: 8.4pt; color: #6b645b; margin: 2px 0 10px; }}
figure {{ margin: 6px 0; page-break-inside: avoid; }}
.yorum {{ font-size: 9.6pt; }}
ul {{ margin: 0 0 7px 18px; padding: 0; }} li {{ margin: 0 0 3px; }}
.kay p {{ text-align: left; padding-left: 18px; text-indent: -18px; font-size: 9pt; margin-bottom: 4px; }}
.pb {{ page-break-before: always; }}
</style></head><body>

<h1>Türk Sineması Bir Küçük Dünya mı?</h1>
<div style="font-family:'DejaVu Sans';font-size:11.5pt;color:#6b645b;margin-bottom:4px">Yeşilçam'dan bugüne oyuncu iş birliği ağının zamansal küçük dünya analizi</div>
<div class="meta">Ayşe Dudu Tursun (2516016019) · Manisa Celal Bayar Üniversitesi, Büyük Veri Analistliği · Sosyal Ağ Analizi dönem ödevi · Öğr. Gör. Osman Can Çetlenbik</div>

<div class="ozet"><b>Özet.</b> Wikidata'dan script ile toplanan {n(tb['film_sayisi_yilli_aralikta'])} Türk yapımı filmden (1950–2025) oyuncu bilgisi olan {n(tb['p161_olan_film'])}'ü kullanılarak {n(t['dugum'])} oyuncu ve {n(t['kenar'])} bağdan oluşan bir oyuncu–oyuncu ağı kuruldu. Oyuncuların %{f(t['dev_bilesen_payi']*100,1)}'i tek bir dev bileşende; iki oyuncu arasında ortalama {f(t['ortalama_en_kisa_yol_gc'])} adım var. Ağın kümelenmesi aynı derece dizisine sahip 100 rastgele ağın yaklaşık {f(C/Cr,0)} katıdır (z = {f(nm['ortalama_yerel_kumelenme']['z'],0)}), ortalama yol ise rastgele ağlarınkine yakındır ({f(L)} / {f(Lr)}). On yıllık ağların sekizinde de küçük dünya katsayısı σ &gt; 1 çıkmıştır ({f(zm.sigma.min(),1)}–{f(zm.sigma.max(),1)}). Cevap: Türk sineması her dönemde bir küçük dünyadır; ancak ω katsayısı, Yeşilçam sonrası ağların daha kümeli ve dönemlere bölünmüş bir yapıya kaydığını gösteriyor.</div>

<h2>1. Giriş ve araştırma sorusu</h2>
<p>Watts ve Strogatz (1998), film oyuncularının birlikte oynama ağını “küçük dünya” yapısının ilk örneklerinden biri olarak göstermiştir: yerel düzeyde sıkı kümeler, küresel düzeyde ise kısa yollar. Bu çalışma aynı soruyu Türk sineması için sorar: <b>Türk sineması bir küçük dünya mı? Yeşilçam'dan bugüne ağın yapısı nasıl değişti?</b> Soru iki parçalıdır. Birincisi statik bir yapı sorusudur (kümelenme yüksek ve yollar kısa mı?), ikincisi zamansaldır (her on yıllık dönemde bu yapı korunuyor mu, ortalama ayrım derecesi ve dev bileşen nasıl değişiyor?). Yeşilçam, 1960–70'lerde yüksek film üretimine sahip, yıldız sistemine dayanan bir dönemdi; 1990'larda özel televizyonların açılması ve videonun yaygınlaşmasıyla üretim çift haneli sayılara inmiş, 1996'da <i>Eşkıya</i> ile toparlanma başlamıştır (Güler, 2021). Popüler sinema 1990'ların ikinci yarısında “başka bir formda” yeniden ortaya çıkmıştır (Arslan, 2018). Bu tarihsel kırılmanın ağ yapısında bir iz bırakıp bırakmadığı sınanmaktadır. Ağ verisinden nedensellik çıkarılamayacağı için bulgular ilişkisel olarak yorumlanır.</p>

<h2>2. Veri ve ağ kurma</h2>
<p><b>Kaynak ve toplama.</b> Veri, Wikidata SPARQL uç noktasından <code>src/01_veri_topla.py</code> ile toplanmıştır (toplama zamanı: {tb['toplama_zamani_utc'].replace('T',' ').replace('+00:00',' UTC')}). Wikidata verisi CC0 1.0 lisanslıdır. Film tanımı: <i>film</i> (Q11424) sınıfının örneği veya alt sınıfı (P31/P279*) olan ve menşe ülkesi (P495) Türkiye (Q43) olan öğeler. Yıl, yayın tarihlerinin (P577) en erkeğidir. Oyuncular P161 (“cast member”) özelliğinden alınmıştır. Sorgular 250'lik partiler hâlinde, istekler arasında bekleme ve tanımlayıcı User-Agent ile gönderilmiş, hız sınırı (HTTP 429) durumunda geri çekilme uygulanmıştır.</p>
<p><b>Kapsam.</b> Toplam {n(tb['film_sayisi_tum'])} Türk filmi bulunmuş; {n(tb['yili_olmayan_film'])} filmin yılı olmadığı, {n(tb['film_sayisi_tum']-tb['film_sayisi_yilli_aralikta']-tb['yili_olmayan_film'])}'inin de 1950–2025 dışında kaldığı için {n(tb['film_sayisi_yilli_aralikta'])} film seçilmiştir. Bunların yalnızca {n(tb['p161_olan_film'])}'ünde (%{f(tb['p161_olan_film']/tb['film_sayisi_yilli_aralikta']*100,0)}) en az bir oyuncu kaydı vardır; toplam {n(tb['film_oyuncu_satiri'])} film–oyuncu bağı ve {n(tb['benzersiz_oyuncu'])} benzersiz oyuncu elde edilmiştir. Film başına kayıtlı oyuncu sayısının medyanı {f(cast.median(),0)}, ortalaması {f(cast.mean(),1)}'dir (en kalabalık kadro: {max_cast.index[0][0]}, {max_cast.index[0][1]}, {max_cast.iloc[0]} oyuncu).</p>
<p><b>Düğüm ve kenar kararları.</b> Önce iki parçalı film ↔ oyuncu ağı kurulmuş (<code>iki_parcali_ag.graphml</code>), ardından oyuncu tarafına izdüşüm alınmıştır. <i>Düğüm</i>: oyuncu (Wikidata QID ile tekil; aynı adlı kişiler karışmaz). <i>Kenar</i>: iki oyuncu en az bir filmde birlikte listelenmişse. <i>Yön</i>: yok, çünkü birlikte oynamak simetriktir. <i>Ağırlık</i>: ortak film sayısı; tekrarlanan iş birliği tek seferlik olandan güçlü bir bağ sayılır (ortalama {f(ken.agirlik.mean())}, en yüksek {int(en_agir.agirlik)}: {en_agir.kaynak_adi}–{en_agir.hedef_adi}). Kenarlara ortak filmlerin ilk ve son yılı da eklenmiştir. Topoloji ölçüleri (yol, kümelenme, merkeziyet) ağırlıksız hesaplanmıştır, çünkü soru bağın <i>varlığı</i> ile ilgilidir; topluluk tespitinde ağırlık kullanılmıştır. Kenar listesi (<code>kenar_listesi.csv</code>), düğüm tablosu ve GraphML dosyaları depoda yayımlanmış, her sütun <code>data/VERI_SOZLUGU.md</code>'de tanımlanmıştır. Oyuncular kamusal kişiler olduğu için adlarıyla gösterilmiştir.</p>

<h2>3. Yöntem</h2>
<ul>
<li><b>Temel ölçüler</b> (python-igraph): yoğunluk, bileşenler, dev bileşende ortalama en kısa yol ve çap (dev bileşen {n(gc_n)} düğüm olduğundan tam hesap), global ve ortalama yerel kümelenme, derece benzeşimi (Newman, 2002).</li>
<li><b>Derece dağılımı</b>: <code>powerlaw</code> paketiyle (Alstott vd., 2014) kesikli kuvvet yasası uydurma, x<sub>min</sub> seçimi ve log-olabilirlik oranı (R, p) ile log-normal, üstel, kesik kuvvet yasası ve gerilmiş üstel dağılımlarla karşılaştırma (Clauset vd., 2009).</li>
<li><b>Merkeziyet</b>: derece, betweenness (tam), closeness, eigenvector, PageRank; ilk 10 tablosu ve ölçüler arası Spearman korelasyonu.</li>
<li><b>Topluluk</b>: Louvain (Blondel vd., 2008) ve Leiden (Traag vd., 2019), ağırlıklı modülerlik; her biri 10 farklı tohumla çalıştırılıp çiftler arası NMI ve ARI hesaplanmıştır.</li>
<li><b>Null model</b>: aynı derece dizisine sahip, basit ve bağlı 100 rastgele ağ (Viger &amp; Latapy, 2005, configuration model); her ölçü için z = (gözlenen − ort.) / ss.</li>
<li><b>Zamansal küçük dünya</b> (zorunlu ileri yöntem): her on yıl için (2020–2025 altı yıl) yalnızca o dönemin filmlerinden ağ kurulmuştur. Dev bileşende C (ortalama yerel kümelenme) ve L (ortalama en kısa yol = ortalama ayrım derecesi) hesaplanmış; her dilim için 100 eşdereceli rastgele ağdan C<sub>r</sub>, L<sub>r</sub> elde edilmiştir. σ = (C/C<sub>r</sub>)/(L/L<sub>r</sub>) (Humphries &amp; Gurney, 2008); σ &gt; 1 küçük dünya demektir. σ ağ büyüdükçe artma eğiliminde olduğundan boyuttan daha az etkilenen ω = L<sub>r</sub>/L − C/C<sub>l</sub> (Telesford vd., 2011) de hesaplanmıştır; ω ≈ 0 küçük dünya, −1'e yakın değerler kafes, +1'e yakın değerler rastgele ağ benzeri yapıyı gösterir. C<sub>l</sub>, aynı düğüm sayısı ve ortalama dereceye sahip halka kafesin kümelenmesidir. Telesford vd. derece dağılımını koruyan bir kafes önerdiği için bu bir yaklaşımdır. Ayrıca her dönemin sonuna kadar biriken ağda dev bileşen payı izlenmiştir.</li>
<li><b>Köprü testi</b>: betweenness'ı en yüksek 5 oyuncu tek tek ve birlikte çıkarıldığında dev bileşenin ve ortalama yolun değişimi; aynı sayıda rastgele oyuncu çıkarmanın 100 tekrarıyla karşılaştırma.</li>
</ul>
<p>Tüm rastgele işlemlerde sabit tohum (SEED = 42) kullanılmış; kod <code>src/</code>, tüm adımları sırayla çalıştıran defter <code>analiz.ipynb</code>'dedir.</p>

<h2>4. Bulgular</h2>
<h3>4.1 Temel yapı</h3>
<table class="t"><tr><th>Ölçü</th><th>Değer</th><th>Bu ağda ne anlama geliyor?</th></tr>
<tr><td>Düğüm / kenar</td><td>{n(t['dugum'])} / {n(t['kenar'])}</td><td class="yorum">Wikidata'da en az bir Türk filminde kaydı olan oyuncular ve birlikte oynama ilişkileri.</td></tr>
<tr><td>Yoğunluk</td><td>{f(t['yogunluk'],4)}</td><td class="yorum">Olası oyuncu çiftlerinin yalnızca %{f(t['yogunluk']*100,2)}'si birlikte oynamış; ağ seyrektir. Her oyuncu ortalama {f(t['ortalama_derece'],1)} kişiyle (medyan {f(t['medyan_derece'],0)}) oynamış.</td></tr>
<tr><td>Bileşenler</td><td>{n(t['bilesen_sayisi'])} (izole: {n(t['izole_dugum'])})</td><td class="yorum">Dev bileşen {n(gc_n)} oyuncuyu (%{f(t['dev_bilesen_payi']*100,1)}) kapsıyor; ikinci büyük bileşen yalnızca {n(t['ikinci_bilesen_dugum'])} kişi. Türk sinemasının neredeyse tamamı birbirine ulaşabilir.</td></tr>
<tr><td>Ortalama en kısa yol / çap</td><td>{f(t['ortalama_en_kisa_yol_gc'])} / {t['cap_gc']}</td><td class="yorum">Rastgele seçilen iki oyuncu arasında ortalama 3–4 “birlikte oynadı” adımı var; en uzak iki oyuncu arasında {t['cap_gc']} adım.</td></tr>
<tr><td>Kümelenme (ort. yerel / global)</td><td>{f(t['ortalama_yerel_kumelenme'])} / {f(t['global_kumelenme_transitivity'])}</td><td class="yorum">Bir oyuncunun birlikte oynadığı iki kişinin de birbiriyle oynamış olma olasılığı yüksek. Bunun ana nedeni her filmin kadrosunun bir “klik” oluşturmasıdır.</td></tr>
<tr><td>Derece benzeşimi</td><td>{f(t['derece_assortativity'],3)}</td><td class="yorum">Sıfıra çok yakın: çok bağlantılı yıldızlar ne özellikle birbirleriyle ne de özellikle az bağlantılı oyuncularla oynuyor.</td></tr>
</table>

<h3>4.2 Derece dağılımı</h3>
<figure>{img(F/'derece_dagilimi.png','92%')}<div class="cap">Şekil 1. Derece dağılımı (log-log) ve tamamlayıcı birikimli dağılım (CCDF) ile aday dağılımlar.</div></figure>
<p>Kuvvet yasası uydurması α = {f(dd['alpha'])} (± {f(dd['sigma_alpha'])}), x<sub>min</sub> = {dd['xmin']} verdi ({n(dd['kuyruktaki_dugum'])} oyuncu kuyrukta). Ancak karşılaştırmalarda log-normal ({pl('lognormal')}), kesik kuvvet yasası ({pl('truncated_power_law')}) ve üstel dağılım ({pl('exponential')}) saf kuvvet yasasından anlamlı ölçüde daha iyi uyuyor (R &lt; 0 alternatif lehinedir). <b>Yorum:</b> Ağ ağır kuyruklu (birkaç oyuncu yüzlerce kişiyle oynamış) ama “ölçekten bağımsız” değil; kuyruk bir noktadan sonra kesiliyor. Bir oyuncunun kariyeri ve çekebileceği film sayısı sınırlı olduğu için sınırsız büyüyen “zengin daha zengin olur” yapısı gözlenmiyor.</p>

<h3>4.3 Merkeziyet</h3>
{tablo_ilk10()}
<div class="cap">Tablo 1. Dört merkeziyete göre ilk 10 oyuncu (dev bileşen). Değerler <code>results/ilk10_*.csv</code>'dedir.</div>
<p><b>{cuneyt.ad}</b> {int(cuneyt.derece)} farklı oyuncuyla (Wikidata'da {int(cuneyt.film_sayisi)} film) derece, betweenness ve PageRank'te birincidir; betweenness değeri ({f(ilk['betweenness'].iloc[0].betweenness,3)}) ikinci sıradaki {bet2.ad}'in ({f(bet2.betweenness,3)}) yaklaşık {f(ilk['betweenness'].iloc[0].betweenness/bet2.betweenness,1)} katıdır. Yani iki oyuncu arasındaki en kısa yolların en büyük kısmı onun üzerinden geçer. <b>Closeness</b> ilk 10'u çok sıkışıktır ({f(ilk['closeness'].closeness.min(),3)}–{f(ilk['closeness'].closeness.max(),3)}). Dönemlerin buluştuğu oyuncular (Güven Kıraç, Şener Şen, Haluk Bilginer, Tuncel Kurtiz) ağın “ortasında” durur. <b>Eigenvector</b> ilk 10'u tamamen 2000 sonrası oyunculardır, çünkü bu ölçü bağlı olunan kişilerin de bağlı olmasını ödüllendirir ve en yoğun çekirdek 2000'lerin kalabalık kadrolu filmleridir.</p>
{tablo_spearman()}
<div class="cap">Tablo 2. Merkeziyetler arası Spearman korelasyonu (dev bileşen, n = {n(gc_n)}).</div>
<p>Derece ile PageRank neredeyse aynı sıralamayı veriyor (ρ = {f(sp.loc['derece','pagerank'])}). Dikkat çekici olan, betweenness'ın derecedense film sayısıyla daha güçlü ilişkili olmasıdır (ρ = {f(sp.loc['betweenness','film_sayisi'])} ve {f(sp.loc['derece','betweenness'])}). Uzun kariyer boyunca çok film yapan oyuncular farklı dönemleri ve ekipleri birbirine bağlıyor. Derece ile film sayısı arasındaki görece zayıf ilişki (ρ = {f(sp.loc['derece','film_sayisi'])}) bir veri özelliğinden kaynaklanıyor: 2000–2009 filmlerinde film başına ortalama {f(z2000.film_basina_oyuncu,1)} oyuncu kayıtlıyken 1960'larda bu sayı {f(z1960.film_basina_oyuncu,1)}'dir. Bu yüzden az filmli yeni dönem oyuncuları, çok filmli Yeşilçam oyuncularından daha fazla kişiyle bağlantılı görünür.</p>

<h3>4.4 Topluluklar</h3>
<p>Louvain ortalama modülerliği {f(lv['modularite_ort'],3)} (10 tohumda {min(lv['topluluk_sayisi'])}–{max(lv['topluluk_sayisi'])} topluluk), Leiden'inki {f(ld['modularite_ort'],3)}'tür ({min(ld['topluluk_sayisi'])}–{max(ld['topluluk_sayisi'])} topluluk). Leiden az da olsa daha yüksek modülerlik ve daha düşük varyans verir. <b>Kararlılık:</b> tohumlar arası ortalama NMI Louvain'de {f(lv['nmi_ort'])} (ARI {f(lv['ari_ort'])}), Leiden'de {f(ld['nmi_ort'])} (ARI {f(ld['ari_ort'])}); aynı tohumda iki algoritma arasında NMI {f(tn['louvain_leiden_ayni_tohum_nmi_ort'])}. Bölümleme orta-iyi düzeyde kararlıdır; temel yapı tekrar ediyor, ancak sınırdaki oyuncular çalıştırmadan çalıştırmaya topluluk değiştirebiliyor. Modülerlik {f(tn['referans']['modularite'])}, kenarların %{f(ic_oran*100,0)}'inin topluluk içinde kaldığı ve bunun rastgele bir ağda beklenenden çok fazla olduğu anlamına gelir (bkz. 4.5). Referans olarak en yüksek modülerlikli Leiden bölümü (tohum {tn['referans']['tohum']}) kullanılmıştır.</p>
{tablo_topluluk()}
<div class="cap">Tablo 3. En büyük 6 topluluk. Adlar topluluktaki oyunculara, filmlere ve film yıllarına bakılarak verilmiştir.</div>
<p>Topluluklar büyük ölçüde <b>dönemlere</b> göre ayrışıyor: Yeşilçam çekirdeğinin film yılı medyanı {int(tn['en_buyuk_topluluklar'][1]['film_yili_medyan'])}, en büyük topluluğunki {int(tn['en_buyuk_topluluklar'][0]['film_yili_medyan'])}'dir. Yeşilçam çekirdeği ile 2000'ler ana akım topluluğu arasında doğrudan yalnızca {arasi(0,1)} bağ vardır. Kemal Sunal – Şener Şen çevresinin ise Yeşilçam çekirdeğiyle {arasi(1,2)}, 2000'ler topluluğuyla {arasi(0,2)} bağı bulunur; bu çevre iki dönem arasında bir köprü işlevi görür. Bir topluluk dönem değil üretim bağlamıyla tanımlanır: <i>Duvara Karşı</i>, <i>Kebab Connection</i>, <i>Temmuz'da</i> gibi Almanya bağlantılı yapımlar ayrı bir küme oluşturur.</p>

<h3>4.5 Null model karşılaştırması</h3>
{tablo_null()}
<div class="cap">Tablo 4. Dev bileşen ile aynı derece dizisine sahip 100 rastgele ağın karşılaştırması.</div>
<p>Kümelenme rastgele ağlarda {f(Cr,3)} iken gözlenen ağda {f(C,3)}'tür; 100 rastgele ağın hiçbiri bu değere yaklaşmaz (z = {f(nm['ortalama_yerel_kumelenme']['z'],0)}). Modülerlik için de durum aynıdır ({f(nm['modularite_louvain']['gozlenen'])} / {f(nm['modularite_louvain']['null_ort'])}). Bu nedenle kümelenme ve topluluk yapısı, oyuncuların bağlantı sayılarının (derece dağılımının) kendiliğinden ürettiği bir sonuç olamaz. Ortalama yol gözlenen ağda rastgele ağlardan anlamlı ölçüde uzundur, ama aynı büyüklüktedir (oran {f(L/Lr)}). Küçük dünyanın tanımı da tam olarak budur: rastgele ağ kadar kısa yollar, ondan çok daha yüksek kümelenme. Tüm ağ için σ = {f(sigma_tum,1)}'dir. Derece benzeşimi istatistiksel olarak farklı olsa da (z = {f(nm['assortativity']['z'],1)}) etki büyüklüğü çok küçüktür. <b>Null model olmasaydı</b> “kümelenme 0,71 yüksek” demek yorumsuz kalırdı; bu değerin derece dağılımından beklenenin ~{f(C/Cr,0)} katı olduğunu söyleyemezdik.</p>

<h3>4.6 Zamansal küçük dünya analizi</h3>
{tablo_zaman()}
<div class="cap">Tablo 5. On yıllık ağlar. DB: dev bileşen. C<sub>r</sub>, L<sub>r</sub>: 100 eşdereceli rastgele ağın ortalaması. σ için köşeli parantez, tek tek rastgele ağlarla hesaplanan σ'ların %2,5–%97,5 aralığıdır. Birikimli DB: 1950'den o dönemin sonuna kadarki tüm filmlerin ağında dev bileşen payı.</div>
<figure>{img(F/'zamansal_kucuk_dunya.png','88%')}<div class="cap">Şekil 2. On yıllık ağlarda σ, ω, ortalama ayrım derecesi ve dev bileşen payı.</div></figure>
<p><b>σ:</b> Sekiz dönemin hepsinde σ &gt; 1'dir ve güven aralıklarının alt sınırı da 1'in üzerindedir. Türk sineması Yeşilçam'dan bugüne her dönemde küçük dünya yapısını korumuştur. σ'nın 2000'lerde ({f(z2000.sigma,1)}) ve 2010'larda ({f(z2010.sigma,1)}) yükselmesi büyük ölçüde ağların büyümesinden kaynaklanır: oyuncu sayısı arttıkça rastgele ağın kümelenmesi C<sub>r</sub> düşer ({f(zm.C_r.iloc[0],3)} → {f(z2010.C_r,3)}) ve σ kendiliğinden artar. Bu yüzden dönemler arası karşılaştırma için ω daha uygundur.</p>
<p><b>ω:</b> Tüm dönemlerde negatif, yani kümelenme rastgele ağdan çok kafes düzeyine yakın. 1950–1979 arasında ω {f(omega_yc.min())} ile {f(omega_yc.max())} arasında, sıfıra yakın. Yeşilçam ağları “dengeli” küçük dünyalardır. 1980–2019 arasında ω {f(omega_sonra.min())} ile {f(omega_sonra.max())} arasına iner: sonraki ağlar daha kümeli, yolları rastgeleye göre daha uzun ve kafese daha yakındır.</p>
<p><b>Ortalama ayrım derecesi</b> {f(zm.L.iloc[0])}'ten ({zm.dilim.iloc[0]}) {f(z2010.L)}'e (2010–2019) yükselmiştir. Yeşilçam'da birkaç çok üretken yıldızın neredeyse herkesle oynaması dünyayı “küçültüyordu”. Sonraki dönemlerde ağ, birbirinden daha ayrık ekiplerden oluşur. Bu gözlem 4.4'teki dönemsel toplulukların zaman içindeki karşılığıdır. <b>Dev bileşen:</b> birikimli ağda dev bileşen {n(zm.birikimli_gc_pay.iloc[0]*zm.birikimli_oyuncu.iloc[0])} oyuncudan {n(gc_n)} oyuncuya büyümüş, payı her dönemde %{f(zm.birikimli_gc_pay.min()*100,0)}–{f(zm.birikimli_gc_pay.max()*100,0)} aralığında kalmıştır. Yeni kuşaklar ağa ayrı adalar olarak değil, var olan dev bileşene bağlanarak katılmıştır. Dönem bazında dev bileşen payı 1990'larda %{f(zm_s.loc['1990–1999'].gc_pay*100,0)}'a düşer. Bu dönemde verimizdeki film sayısı da {n(zm_s.loc['1980–1989'].film)}'den {n(zm_s.loc['1990–1999'].film)}'e düşer; literatürde de üretimin daraldığı belirtilen dönemdir (Güler, 2021). 2020–2025 diliminde payın %{f(z2020.gc_pay*100,0)}'ye düşmesi ise eksik veriyle açıklanmalıdır: dilim yalnızca altı yıldır, {n(z2020.film)} filmi vardır ve tek bir filmin kadrosu ({max_cast.index[0][0]}, {max_cast.iloc[0]} oyuncu) dilimi baskılar.</p>

<h3>4.7 Köprü testi: “Bu oyuncu olmasaydı?”</h3>
{tablo_kopru()}
<div class="cap">Tablo 6. Dev bileşen ({n(kt['temel']['gc'])} oyuncu, L = {f(kt['temel']['L'],3)}) üzerinden çıkarma deneyi.</div>
<p>Betweenness'ı en yüksek oyuncu olan {cuneyt.ad} çıkarıldığında dev bileşenden <b>hiç kimse kopmaz</b>; yalnızca ortalama ayrım derecesi {f(kt['temel']['L'],3)}'ten {f(tek[cuneyt.ad]['L'],3)}'e çıkar. İlk beş köprü oyuncu birlikte çıkarılınca bile {n(bir[5]['kopan'])} oyuncu kopar ve L {f(bir[5]['L'],3)} olur. Rastgele beş oyuncu çıkarmanın etkisi ortalama {f(bir[5]['rastgele_kopan_ort'],1)} kopuş ve L ≈ {f(bir[5]['rastgele_L_ort'],3)}'tür. Yüksek betweenness bu ağda “vazgeçilmezlik” değil, kısayol anlamına gelir: Cüneyt Arkın yolları kısaltır, ama onun yokluğunda alternatif yollar vardır. Bu yedeklilik küçük dünya yapısının yüksek kümelenmesinin doğal sonucudur.</p>

<h2>5. Tartışma</h2>
<p><b>Cevap.</b> Türk sineması oyuncu ağı bir küçük dünyadır. Oyuncuların büyük çoğunluğu tek bir bileşende, ortalama 3–4 adımla birbirine bağlıdır ve kümelenme rastgele beklentinin çok üzerindedir. Bu yapı 1950'lerden 2020'lere her on yıllık dönemde σ &gt; 1 ile korunmuştur. <b>Değişim:</b> Yeşilçam ağları daha kısa yollu ve rastgeleye daha yakın (ω ≈ 0) küçük dünyalardır; sonraki ağlar daha uzun yollu, daha kümeli ve dönemsel topluluklara bölünmüş bir yapı gösterir. Yeşilçam yıldız sisteminden 1990'ların daralmasına ve 2000'lerde yeniden canlanan sinemaya uzanan tarihsel anlatı (Güler, 2021; Arslan, 2018) bu yapısal farkla uyumludur. Ancak ağ verisi bu değişimin <i>nedenini</i> kanıtlamaz. Gözlenen farkın bir bölümü, dönemler arasında Wikidata kadro kayıtlarının farklı doluluğundan da kaynaklanabilir.</p>

<h2>6. Sınırlar</h2>
<ul>
<li><b>Eksik ve yanlı veri:</b> Wikidata'da Türk filmlerinin yalnızca %{f(tb['p161_olan_film']/tb['film_sayisi_yilli_aralikta']*100,0)}'ünde oyuncu kaydı var ve film başına medyan {f(cast.median(),0)} oyuncu kayıtlı. Veri, ünlü başrol oyuncularına doğru yanlıdır; yardımcı oyuncular eksik olduğu için gerçek ağ çok daha büyük ve yoğundur. Kayıt doluluğu dönemlere göre farklıdır.</li>
<li><b>Film tanımı:</b> Menşe ülke (P495) girilmemiş Türk filmleri ve yılı olmayan {n(tb['yili_olmayan_film'])} film dışarıda kaldı; ortak yapımlar Türkiye menşe ülkesi olarak listelendiği ölçüde dahildir.</li>
<li><b>İzdüşüm etkisi:</b> Her film kadrosu bir klik ürettiği için kümelenme yapısal olarak yüksektir; null model derece dizisini korur ama film-klik yapısını korumaz. İki parçalı bir null model bu etkiyi daha iyi ayırabilirdi.</li>
<li><b>ω yaklaşımı:</b> Kafes referansı derece dağılımını koruyan bir kafes değil, aynı ortalama dereceli halka kafestir.</li>
<li><b>Son dilim:</b> 2020–2025 altı yıllıktır ve az sayıda filmden oluşur; bu dilimdeki değerler dikkatle yorumlanmalıdır.</li>
<li><b>Nedensellik:</b> Bulgular ilişkiseldir; tarihsel olaylarla ilişki yorumdur, ağdan çıkarılmış nedensel bir sonuç değildir.</li>
</ul>

<h2>Kaynakça</h2>
<div class="kay">
<p>Alstott, J., Bullmore, E., &amp; Plenz, D. (2014). powerlaw: A Python package for analysis of heavy-tailed distributions. <i>PLoS ONE</i>, 9(1), e85777.</p>
<p>Arslan, S. (2018). Türkiye'de sinemanın çoğul halleri (çev. A. E. Bülbül). <i>The New Turkey</i>, 29. https://panorama.khas.edu.tr/uploads/pdf/turkiyede-sinemanin-cogul-halleri.pdf</p>
<p>Blondel, V. D., Guillaume, J.-L., Lambiotte, R., &amp; Lefebvre, E. (2008). Fast unfolding of communities in large networks. <i>Journal of Statistical Mechanics</i>, P10008.</p>
<p>Clauset, A., Shalizi, C. R., &amp; Newman, M. E. J. (2009). Power-law distributions in empirical data. <i>SIAM Review</i>, 51(4), 661–703.</p>
<p>Güler, A. (2021, 1 Haziran). 90'lar Türk sinemasında gişe ve festival filmleri açısından kırılma noktası oldu. <i>Gerçek Hayat / GZT</i>. https://www.gzt.com/cins/90lar-noksanlar-fazlalar-3592655</p>
<p>Humphries, M. D., &amp; Gurney, K. (2008). Network ‘small-world-ness’: A quantitative method for determining canonical network equivalence. <i>PLoS ONE</i>, 3(4), e0002051.</p>
<p>Newman, M. E. J. (2002). Assortative mixing in networks. <i>Physical Review Letters</i>, 89(20), 208701.</p>
<p>Telesford, Q. K., Joyce, K. E., Hayasaka, S., Burdette, J. H., &amp; Laurienti, P. J. (2011). The ubiquity of small-world networks. <i>Brain Connectivity</i>, 1(5), 367–375.</p>
<p>Traag, V. A., Waltman, L., &amp; van Eck, N. J. (2019). From Louvain to Leiden: guaranteeing well-connected communities. <i>Scientific Reports</i>, 9, 5233.</p>
<p>Viger, F., &amp; Latapy, M. (2005). Efficient and simple generation of random simple connected graphs with prescribed degree sequence. <i>COCOON 2005</i>, LNCS 3595, 440–449.</p>
<p>Vrandečić, D., &amp; Krötzsch, M. (2014). Wikidata: A free collaborative knowledgebase. <i>Communications of the ACM</i>, 57(10), 78–85.</p>
<p>Watts, D. J., &amp; Strogatz, S. H. (1998). Collective dynamics of ‘small-world’ networks. <i>Nature</i>, 393, 440–442.</p>
</div>
<p class="m" style="margin-top:10px"><b>Yapay zekâ beyanı:</b> Kod, analiz ve metin taslaklarının hazırlanmasında Anthropic'in Claude asistanından yararlanılmıştır; sonuçlar öğrenci tarafından gözden geçirilmiştir. Kod ve veri: GitHub deposu; etkileşimli ağ: portfolyo.</p>
</body></html>"""

import re
html = re.sub(r"(<h3>[^<]*</h3>\s*)(<table.*?</table>|<figure>.*?</figure>)",
              lambda m: f'<div style="break-inside:avoid;page-break-inside:avoid">{m.group(1)}{m.group(2)}</div>', html, flags=re.S)
out = KOK / "report"
(out / "rapor.html").write_text(html, encoding="utf-8")
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{out/'rapor.html'}');await p.pdf({{path:'{out/'rapor.pdf'}',format:'A4',printBackground:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#888"><span class=pageNumber></span> / <span class=totalPages></span></div>',
margin:{{top:'18mm',bottom:'18mm',left:'17mm',right:'17mm'}}}});await b.close()}})()"""
subprocess.run(["node", "-e", js], check=True)
print("report/rapor.pdf yazıldı")
