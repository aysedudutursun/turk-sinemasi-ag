# Sunum Konuşma Notları — Türk Sineması Oyuncu Ağı

Toplam süre: **6 dakika** (9 slayt × ~40 sn). Tüm sayılar `results/` klasöründeki çıktılardan gelir.
Not okumadan anlatabilmek için her slaytın **tek cümlelik özü** kalın yazıldı. Önce onu söyle, sonra ayrıntıya geç.

---

## 1 · Soru (≈30 sn)
**"Türk sinemasında herkes herkese birkaç adım uzakta mı?"**
- Sorum: Türk sineması bir "küçük dünya" mı, ve Yeşilçam'dan bugüne bu yapı nasıl değişti?
- Küçük dünya iki özelliğin bir arada olması demek: oyuncular sıkı ekipler hâlinde (yüksek kümelenme) ve buna rağmen herkes herkese birkaç adımda ulaşıyor (kısa yol).
- Kısa cevabı başlıkta veriyorum: 2.070 oyuncu ortalama 3,44 adımla birbirine bağlı.

## 2 · Veri ve ağ kurma (≈40 sn)
**"Veriyi script ile Wikidata'dan çektim ve iki adımda ağa çevirdim."**
- Wikidata SPARQL: menşe ülkesi Türkiye olan filmler, 1950–2025, oyuncu bilgisi P161. Veri CC0 lisanslı.
- Yılı belli 2.961 filmden yalnızca 1.954'ünde oyuncu bilgisi var. Önce film ↔ oyuncu iki parçalı ağını kurdum, sonra aynı filmde oynayan iki oyuncuyu birbirine bağladım: 16.073 bağ.
- Bağın yönü yok çünkü birlikte oynamak karşılıklı. Ağırlık ortak film sayısı. En güçlü bağ 16 ortak film: Cüneyt Arkın ile Aydın Haberdar.

## 3 · Temel yapı (≈45 sn)
**"Oyuncuların %87'si birbirine ulaşabiliyor ve bu ulaşım ortalama 3,44 adım sürüyor."**
- Dev bileşen 1.795 oyuncu. Geri kalanlar ağa bağlanmayan küçük film kadroları.
- 3,44 şu demek: rastgele seçtiğim iki oyuncu arasında ortalama 3–4 kişilik bir "birlikte oynadı" zinciri var. En uzak iki oyuncu arası (çap) 8 adım.
- Kümelenme 0,71: bir oyuncunun iki partneri büyük olasılıkla birbiriyle de oynamış. Bu, sette sürekli birlikte çalışan ekipler olduğunu gösteriyor.
- Derece benzeşimi ≈ 0: çok bağlı yıldızlar özellikle birbirini seçmiyor, herkesle oynuyorlar.
- Derece dağılımı: kuvvet yasası testini yaptım ama log-normal belirgin şekilde daha iyi uydu. Yani ağ "ölçekten bağımsız" değil, çok bağlı oyuncuların sayısı sınırlı.

## 4 · Merkeziyet + canlı gösterim (≈50 sn)
**"Cüneyt Arkın ağın merkezinde, ama o olmasa da ağ dağılmıyor."**
- Cüneyt Arkın 239 farklı partnerle derece sıralamasında birinci. Köprü (betweenness) değeri ikinci sıradaki Şener Şen'in yaklaşık 2,8 katı. Yani oyuncular arasındaki en kısa yolların çok büyük kısmı ondan geçiyor.
- Hocanın "durak kapanırsa" örneğinin karşılığı: onu ağdan sildim. **Kimse kopmadı**, sadece ortalama yol 3,44'ten 3,51'e uzadı. İlk 5 köprü oyuncuyu birlikte silince 8 kişi kopuyor. Rastgele 5 oyuncu silince bu sayı ortalama 0,8.
- ▶ **Canlı:** etkileşimli ağda "Cüneyt Arkın"ı ara → mavi Yeşilçam topluluğu, en sık partnerleri. Sonra "Şener Şen" → yeşil topluluk; partnerleri hem Yeşilçam hem 2000'ler tarafında.

## 5 · Topluluklar (≈45 sn)
**"Ağ dönemlere bölünüyor ve iki dönemi Kemal Sunal – Şener Şen çevresi birbirine bağlıyor."**
- Leiden ile 19 topluluk buldum. En büyükleri: 2000'ler ana akım (388 oyuncu, film yılı ortancası 2011), Yeşilçam çekirdeği (376, ortanca 1973), Kemal Sunal – Şener Şen çevresi (185, ortanca 1986), Almanya-Türkiye ortak yapımları (*Duvara Karşı*, *Kebab Connection*).
- Adları her topluluğun en bağlı oyuncularına ve en çok üyesinin oynadığı filmlere bakarak verdim.
- Yeşilçam ile 2000'ler arasında doğrudan yalnızca 78 bağ var. Sunal–Şen çevresinin Yeşilçam'la 291, 2000'lerle 436 bağı var. Köprü onlar.
- Modülerlik 0,60 (Leiden), 0,59 (Louvain). 10 farklı tohumla kararlılık NMI ≈ 0,68, yani orta-iyi.

## 6 · Null model (≈40 sn)
**"Herkes aynı sayıda partnere sahip olsaydı bile bu kümelenme kendiliğinden çıkmazdı."**
- Aynı derece dizisine sahip 100 rastgele ağ ürettim (configuration model).
- Kümelenme: gerçek 0,71, rastgele 0,04 → z = 439. Modülerlik: 0,59'a 0,20 → z = 189. Rastgele ağların hiçbiri gerçek değere yaklaşmadı.
- Ortalama yol: 3,44'e 2,92. Gerçek ağ biraz daha uzun ama aynı büyüklükte. Küçük dünya tanımı da tam olarak bunu söyler.

## 7 · İleri yöntem: σ ve ω (≈45 sn)
**"σ, ağın rastgele ağa göre ne kadar kümeli ama yine de kısa yollu olduğunu tek sayıda ölçüyor."**
- Şekil: soldaki kafeste herkes yalnızca komşusunu tanıyor; kümeli ama yollar uzun (L = 4,14). Sağdaki rastgele ağda yollar kısa ama kümelenme yok. Ortadaki küçük dünyada birkaç uzun bağ yolları kısaltıyor, kümelenme ise kalıyor.
- σ = (C / C_rastgele) ÷ (L / L_rastgele). 1'den büyükse küçük dünya. Tüm ağ için ≈ 15,8.
- σ ağ büyüdükçe kendiliğinden büyür. Bu yüzden ω'yı da hesapladım: 0'a yakınsa küçük dünya, −1'e yakınsa kafes, +1'e yakınsa rastgele.
- Her on yıl için: o on yılın filmleriyle ağ kur → dev bileşeni al → 100 rastgele ağ ve bir halka kafesle kıyasla.

## 8 · Zamansal sonuç (≈45 sn)
**"Yeşilçam'dan bugüne her on yılda σ 1'in üstünde: küçük dünya hiç kaybolmamış."**
- σ en düşük 3,6, en yüksek 12,7. 2000'ler ve 2010'lardaki yükselişin büyük kısmı ağın büyümesinden geliyor: ağ büyüdükçe rastgele kümelenme 0,15'ten 0,05'e düşüyor, bu da σ'yı şişiriyor.
- Ayrım derecesi Yeşilçam'da 2,5–2,7 adım, 2010'larda 3,4. Dünya küçük kaldı ama biraz "uzadı". Yeşilçam'da birkaç çok üretken yıldız herkesi birbirine yaklaştırıyordu.
- ω hep negatif: ağ rastgele ağdan çok kümeli, kafese yakın tarafta.

## 9 · Cevap ve sınırlar (≈40 sn)
**"Evet, Türk sineması bir küçük dünya. Yapısı dönemlere bölündü ama bağlantısı kopmadı."**
- Her on yılda σ > 1. Kümelenme rastgelenin ≈19 katı. Yollar rastgele ağ kadar kısa.
- Sınırlar: Wikidata'da kadrolar eksik, film başına ortanca 2 oyuncu kayıtlı. Bu yüzden veri başrollere ve ünlülere doğru yanlı. 2020–2025 dilimi yarım ve parçalı. σ boyuta duyarlı. Ağ ilişki gösterir, nedensellik iddia etmez.

---

## Olası sorular ve cevaplar

**"Bu ağda modülerlik 0,60 ne demek?"**
Bağların topluluk içinde kalma oranı, aynı derecelere sahip rastgele bir ağda beklenenden belirgin şekilde fazla. Modülerlik bu farkı ölçer, 0 "rastgeleden farksız" demektir. Bizim ağda kenarların yaklaşık %74'ü topluluk içinde. Aynı derece dizisine sahip rastgele ağlarda modülerlik ancak 0,20'ye çıkıyor. Yani oyuncular gerçekten dönem ve ekip gruplarında çalışıyor.

**"Null model olmasaydı ne iddia edemezdik?"**
0,71 kümelenmenin "yüksek" olduğunu söyleyemezdik. Bazı oyuncuların çok fazla partneri olması tek başına da kümelenme yaratabilir. Aynı derece dizisiyle kurulan 100 rastgele ağ ortalama yalnızca 0,04 verdi (z = 439). Bu sayede yüksek kümelenmenin derece dağılımından değil, gerçek ekip yapısından geldiğini söyleyebiliyoruz. Modülerlik ve σ için de aynısı geçerli.

**"σ neden boyuta duyarlı, ω'yı neden ekledin?"**
Rastgele ağın kümelenmesi kabaca ortalama derece / düğüm sayısı kadardır. Ağ büyüdükçe bu değer küçülür ve σ'nın payını büyütür. Nitekim bizde C_r 0,15'ten 0,05'e indi ve σ 12,7'ye çıktı. ω kümelenmeyi rastgele ağla değil kafesle kıyasladığı için −1 ile +1 arasında kalır ve dönemleri karşılaştırmaya daha uygundur. Bir uyarı: ω'daki kafes, aynı boyut ve ortalama derecede bir halka kafes. Bu bir yaklaşım, raporda belirttim.

**"Cüneyt Arkın'ın betweenness'i bu kadar yüksekken onu çıkarınca ağ neden kopmadı?"**
Betweenness, en kısa yolların ne kadarının o kişiden geçtiğini ölçer. Bu yolların tek yol olup olmadığını ölçmez. Cüneyt Arkın çıkınca yollar 3,44'ten 3,51'e uzuyor ama alternatif yollar var. Kümelenme yüksek olduğu için ağda yedek bağlantı bol. Kimse kopmuyor. İlk 5 köprü oyuncu birlikte çıkınca bile yalnızca 8 kişi kopuyor.

**"Kuvvet yasası neden reddedildi?"**
`powerlaw` paketiyle kuyruğa (derece ≥ 16, 709 oyuncu) kuvvet yasası uydurdum: α ≈ 2,61. Olabilirlik oranı testinde log-normal (R = −4,86, p < 0,001), kesik kuvvet yasası ve üstel dağılım daha iyi uydu. Yorumu: çok bağlı oyuncu sayısı kuvvet yasasının öngördüğünden az. Bir oyuncunun kariyeri ve çekebileceği film sayısı sınırlı.

**"Veri yanlı değil mi?"**
Evet, en önemli sınır bu. Wikidata'da kadrolar eksik girilmiş: film başına ortanca 2 oyuncu kayıtlı. 1.007 filmin hiç oyuncu bilgisi yok. Bu yüzden ağ başrol oyuncularına ve ünlülere yanlı. Gerçek ağ büyük ihtimalle daha yoğun ve daha da küçük dünya. Sonuçları "Wikidata'da kayıtlı Türk sineması" için geçerli sayıyorum.

**"2020–2025 dilimi neden farklı?"**
Dilim yarım (6 yıl) ve yalnızca 67 film içeriyor. Dev bileşen oyuncuların yalnızca %20'si (288 oyuncudan 57'si). Ayrıca tek bir film (*Franz*, 2025) 44 oyuncuyla kayıtlı ve geri kalan ağa hiç bağlanmayan ayrı bir bileşen oluşturuyor. Bu dilimdeki en büyük üç bileşen 57, 49 ve 44 oyuncu; yani tek bir dev bileşen yok. Bu yüzden bu dilimdeki düşüşü bir eğilim olarak yorumlamıyorum. Wikidata'nın yeni filmleri henüz eksik işlemiş olması daha olası.

**"Louvain ile Leiden'ın farkı ne?"**
İkisi de modülerliği artırmaya çalışır. Louvain bazen içi kopuk (bağlı olmayan) topluluklar üretebilir. Leiden bir iyileştirme adımı ekleyerek toplulukların içten bağlı olmasını garanti eder. Bizde sonuçlar çok yakın: modülerlik 0,59 ve 0,60. Aynı tohumla iki algoritma arasında NMI ≈ 0,65. Leiden tohumlar arasında biraz daha kararlı (NMI 0,68'e 0,67).
