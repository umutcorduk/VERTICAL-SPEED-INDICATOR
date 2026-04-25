# VERTICAL-SPEED-INDICATOR Tek Pencere UI Tasarimi

## Amaç

Mevcut uygulamada VSI gostergesi Tkinter penceresinde calisirken deger girisi ayri bir terminal uzerinden alinmaktadir. Bu tasarim, gostergenin ve kontrol araclarinin tek bir masaustu uygulamasi icinde birlestirilmesini ve terminal bagimliliginin kaldirilmasini hedefler.

Basari kriterleri:

- Uygulama yalnizca tek bir pencere olarak acilmalidir.
- Terminal veya `input()` kullanan ayri bir akis kalmamalidir.
- Kullanici pencere icinden hedef dikey hiz degerini kolayca girebilmelidir.
- Arayuz, teknik olmayan bir kullanicinin da rahatca anlayabilecegi kadar acik ve yonlendirici olmalidir.
- Mevcut gostergenin animasyon davranisi korunmalidir.

## Kapsam

Bu calisma asagidaki degisiklikleri kapsar:

- Terminal thread'inin kaldirilmasi
- Tek pencere icinde yeni bir kontrol paneli olusturulmasi
- Metin alani, slider ve hazir deger butonlari ile kullanici girdisinin desteklenmesi
- Gecersiz girdiler icin pencere ici durum mesaji gosterilmesi
- Pencere kapatma davranisinin yumusatilmasi

Bu calisma asagidakileri kapsamaz:

- Harici veri kaynagi baglantilari
- Coklu pencere veya coklu cihaz senaryolari
- Farkli GUI kutuphanelerine gecis

## Onerilen Yaklasim

Arayuz iki ana bolumden olusur:

1. Sol panelde mevcut analog VSI gostergesi korunur.
2. Sag panelde kullanici ile etkilesim icin modernize edilmis kontrol alani bulunur.

Bu yapi, mevcut cizim mantigini bozmadan deneyimi sade bir bicimde iyilestirir. Gostergenin yeniden yazilmasi yerine, mevcut canvas tabanli cizim korunur ve pencere yerlesimi yeniden duzenlenir.

## Arayuz Yapisi

### Sol bolum: Gostergenin kendisi

- Mevcut canvas ve ibre animasyonu korunur.
- Gostergenin gorsel dili mevcut koyu tema etrafinda kalir.
- Sol bolum uygulamanin odak noktasi olmaya devam eder.

### Sag bolum: Kontrol paneli

Kontrol paneli su bilesenleri icerir:

- Baslik ve kisa kullanim aciklamasi
- FPM degeri icin sayisal giris alani
- `Uygula` butonu
- `Sifirla` butonu
- `-6000` ile `6000` arasinda slider
- Hizli secim butonlari: `-3000`, `-1500`, `0`, `1500`, `3000`
- Anlik hedef degeri gosteren bilgi alani
- Gecersiz giris veya basarili guncelleme icin durum mesaji

Kontrol paneli, konsol kullanimina alisik olmayan bir kullanicinin dahi degeri girebilmesini saglayacak sekilde yonlendirici etiketler ve tutarli bosluklarla duzenlenir.

## Davranis ve Etkilesim

### Deger girisi

- Kullanici metin alanina bir FPM degeri girip `Uygula` butonuna basabilir.
- Kullanici `Enter` tusu ile de ayni islemi tetikleyebilir.
- Slider uzerindeki degisim dogrudan hedef degeri gunceller.
- Hizli secim butonlari tek tikla on tanimli degerleri uygular.
- `Sifirla`, hedef degeri `0` yapar ve ilgili kontrolleri es zamanli gunceller.

### Senkronizasyon

Asagidaki kontroller tek bir hedef deger kaynagina baglanir:

- Metin alani
- Slider
- Hizli secim butonlari
- Hedef deger etiketi
- Ibre animasyonu

Boylece herhangi bir kontrol uzerinden yapilan guncelleme diger gorunumleri de uyumlu tutar.

### Girdi dogrulama

- Metin girdisi sayiya cevrilemezse pencere icinde acik bir hata mesaji gosterilir.
- Gecerli ama aralik disi degerler `-6000` ile `6000` araligina sinirlanir.
- Kullaniciya uygulanan nihai deger acikca gosterilir.

## Mimari Degisiklikler

Kod, mevcut tek dosya yapisi icinde kalabilir; ancak sorumluluklar daha belirgin hale getirilmelidir:

- Deger ayrıştırma ve sinirlama icin kucuk yardimci fonksiyonlar
- Gostergenin cizim ve animasyon sorumlulugu
- UI kontrol paneli kurulumu
- Tek bir merkezden hedef deger guncelleme akisi

Terminale bagli `threading`, `input()` ve sert cikis icin kullanilan `os._exit(0)` kaldirilir. Pencere kapatma davranisi `destroy()` tabanli normal Tkinter akisina donusturulur.

## Hata Yonetimi

- Gecersiz sayisal giris durumunda uygulama kapanmaz.
- Hata mesaji kontrol panelinde gorunur.
- Beklenen kullanici hatalari exception olarak terminale yazdirilmak yerine UI uzerinden iletilir.

## Test Stratejisi

UI kodu dogrudan otomasyona uygun olmadigi icin testler davranissal yardimci fonksiyonlara odaklanir:

- Metin girdisinin `float` degerine cevrilmesi
- Degerin izin verilen aralikta sinirlanmasi
- Uygulanacak mesaj formatinin beklenen degerleri yansitmasi

TDD akisi ile once bu yardimci davranislar icin failing testler yazilir, sonra minimum uretim kodu eklenir. Son olarak uygulama manuel olarak calistirilip tek pencere acilisi, slider senkronizasyonu, butonlar ve `Enter` ile uygulama akisları dogrulanir.

## Kabul Kriterleri

- `python vsi.py` calistirildiginda yalnizca tek GUI penceresi acilir.
- Konsol uzerinden girdi beklenmez.
- Kullanici metin alani, slider veya hizli butonlarla ibreyi hareket ettirebilir.
- Gecersiz metin girdisi uygulamayi bozmaz, pencere icinde anlasilir mesaj verir.
- Pencere kapatildiginda uygulama temiz sekilde sonlanir.

## Uygulama Sirasi

1. Deger ayrıştırma ve sinirlama yardimcilarini tanimla.
2. Bu yardimcilar icin failing testleri yaz.
3. Testleri gecirecek minimum yardimci kodu ekle.
4. Tkinter yerlesimini gostergesi + kontrol paneli olacak sekilde yeniden kur.
5. Terminal thread'ini kaldir ve tum girdileri UI kontrol akisina bagla.
6. Durum mesaji ve girdi dogrulamasini ekle.
7. Uygulamayi manuel olarak calistirip akis dogrulamasini yap.
