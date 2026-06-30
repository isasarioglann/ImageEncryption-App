# ImageEncryption-App
# 📷 Canlı Görüntü Şifreleme ve İşleme Uygulaması

Bu proje, bilgisayar kamerasından alınan anlık görüntü akışını, ardışık matematiksel ve kriptografik katmanlardan geçirerek eş zamanlı (real-time) olarak şifreleyen ve güvenli bir şekilde veritabanında saklayan modern arayüzlü bir **Python** uygulamasıdır.

## 🚀 Özellikler ve İşlevler
- **Anlık Kamera Akışı:** OpenCV ile entegre, gecikmesiz çalışan video yakalama modu.
- **Ardışık Şifreleme Hattı (Pipeline):** Görüntü pikselleri 5 farklı aşamadan geçerek tamamen tanınmaz hale getirilir.
- **Veritabanı Entegrasyonu:** Şifrelenmiş görseller, orijinal halleri ve sayısal piksel özetleri (BPM/Sum verileri) MySQL/SQLite üzerinde `LONGBLOB` olarak saklanır.
- **Deşifre Etme Modülü:** Veritabanından çağrılan şifreli görüntüler, arayüz üzerinden seçilerek geri çözülebilir.
- **Modern UI:** Kullanıcı dostu, karanlık mod (dark theme) destekli ve akan bilgi paneline sahip GUI tasarımı.

## 🛠 Şifreleme Adımları ve Algoritmalar
1. **Dijital Kilit (XOR):** Her piksel değeri, belirlenen gizli anahtar ile bit düzeyinde XOR işlemine tabi tutulur.
2. **Ayna Selfie (Yansıma):** Matris yatay eksende ters çevrilerek geometrik manipülasyon sağlanır.
3. **Frekans Dansı (FFT Modülasyonu):** Hızlı Fourier Dönüşümü (FFT) kullanılarak görüntü frekans uzayına taşınır, düşük frekans bileşenleri modüle edilerek yapısal bütünlük bozulur.
4. **Blok Yer Değiştirme:** Matris 10x10'luk bloklara bölünür ve sahte-rastgele (pseudo-random) algoritmalarla blokların konumları karıştırılır.
5. **Yaş & BPM Piksel Modülasyonu:** 5x5 piksel gruplarına rastgele ağırlıklar (yaş/BPM) atanarak RGB kanallarına dinamik kaymalar eklenir.

## 📦 Kurulum ve Çalıştırma

1. Projeyi bilgisayarınıza klonlayın:
   ```bash
   git clone [https://github.com/kullanici-adiniz/goruntu-sifreleme-app.git](https://github.com/kullanici-adiniz/goruntu-sifreleme-app.git)
   cd goruntu-sifreleme-app


   Gerekli kütüphaneleri yükleyin:

Bash
pip install -r requirements.txt
database/backup.sql dosyasını yerel MySQL sunucunuzda içe aktarın (Kullanıcı adı ve şifrenizi src/main.py içinden güncellemeyi unutmayın).

Uygulamayı başlatın:

Bash
python src/main.py

---

## 4. Adım: Kod İçindeki Küçük Bir Hatayı Düzeltme
`s.py` dosyasını `main.py` olarak kaydederken satır **19-20** civarındaki `step_descriptions` listesinde küçük bir string birleştirme hatası (virgül eksikliği) var. Projenin hatasız açılması için orayı şu şekilde güncelleyebilirsin:

```python
step_descriptions = [
    "1. Dijital Kilit (XOR): Her pikselin değeri gizli bir anahtar ile kilitlenir.",
    "2. Ayna Selfie (Yansıma): Görüntü yatayda ayna gibi ters çevrilir.",
    "3. Elektromanyetık Yük Atamaları: Her piksele (+) veya (-) yük atar.", # Virgül eklendi
    "4. Frekans Dansı (Modülasyon): Görüntüdeki pikseller frekans alanında karıştırılır.",
    "5. Blok Tetris (Yer Değiştirme): 10x10'luk bloklar yer değiştirir.",
    "6. Yaş & BPM Partisi: 5x5 piksel gruplarına rastgele modülasyon uygulanır."
