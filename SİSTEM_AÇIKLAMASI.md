# Flight Delay Prediction API - Sistem Açıklaması

## 🔍 Health Check Nasıl Çalışıyor?

### Prensip:
Health check endpoint'i (`/health`), sistemin sağlığını kontrol eden bir mekanizmadır. 

### Şu Anda Kontrol Edilenler:
1. **API Servisi**: API'nin çalışıp çalışmadığını kontrol eder
2. **Python Modülleri**: Gerekli modüllerin yüklü olup olmadığını kontrol eder
3. **Hash Fonksiyonu**: Hash fonksiyonunun düzgün çalışıp çalışmadığını test eder

### Nasıl Çalışır?
- Her istekte sistem bileşenleri kontrol edilir
- Her bileşen için durum (ok/error) belirlenir
- Genel durum tüm bileşenlerin durumuna göre belirlenir
- Sonuçlar hem JSON hem HTML formatında döndürülür

### Gelecekte Eklenebilecekler:
- Veritabanı bağlantı kontrolü
- Dış API servisleri kontrolü
- Disk alanı kontrolü
- Bellek kullanımı kontrolü
- CPU kullanımı kontrolü

---

## ❓ Sadece API mi Kontrol Ediyor?

**Hayır!** Health check şu anda şunları kontrol ediyor:
- ✅ API servisi
- ✅ Python modülleri
- ✅ Hash fonksiyonu

Bu bir **kapsamlı sistem kontrolü**dür, sadece API değil.

---

## 🎯 Sistem Neyi Tahmin Ediyor?

### Önemli Açıklama:
Bu sistem şu anda **gerçek bir uçuş gecikmesi tahmini yapmıyor**. 

### Sistem Ne Yapıyor?
Sistem, havaalanı kodlarını (IATA) **hash bucket** değerlerine çeviriyor.

### Hash Bucket Nedir?
- Hash bucket, makine öğrenmesi modellerinde kullanılan bir tekniktir
- Verileri gruplamak ve kategorize etmek için kullanılır
- Aynı havaalanı kodu her zaman aynı bucket değerini verir
- 0-99 arası bir değer döndürür (100 bucket)

### Örnek:
```
Girdi: "IST" (İstanbul Havalimanı)
Çıktı: Hash Bucket: 2

Girdi: "JFK" (New York JFK)
Çıktı: Hash Bucket: 42

Girdi: "LAX" (Los Angeles)
Çıktı: Hash Bucket: 15
```

### Neden Hash Bucket?
Bu bir **MLOps ödev/demo projesi**dir. Gerçek bir uçuş gecikmesi tahmini için:
1. Tarihsel uçuş verileri gerekir
2. Makine öğrenmesi modeli eğitilmelidir
3. Hava durumu, trafik, mevsim gibi faktörler eklenmelidir

Şu anki sistem, bu tür bir modelin **feature engineering** (özellik mühendisliği) aşamasındaki bir bileşenidir.

### Nasıl Kullanılır?
Hash bucket değerleri, gelecekte eğitilecek bir ML modelinde **kategorik özellik** olarak kullanılabilir:
- Her havaalanı bir bucket'a atanır
- Model, bucket değerlerine göre öğrenir
- Bu sayede binlerce havaalanı yerine 100 kategori ile çalışılır

---

## 📊 Sistem Mimarisi

```
Kullanıcı → Web Arayüzü → FastAPI → Hash Fonksiyonu → Hash Bucket
                ↓
         Health Check (Sistem Kontrolü)
```

---

## 🔧 Teknik Detaylar

### Hash Algoritması:
- **MD5** hash kullanılıyor
- Deterministik: Aynı girdi → Aynı çıktı
- Modulo işlemi ile 0-99 arası değere indirgeniyor

### API Endpoints:
- `GET /` - Ana sayfa (Web arayüzü)
- `GET /health` - Health check (Sistem sağlık kontrolü)
- `POST /predict` - Hash bucket tahmini
- `GET /docs` - Swagger UI (API dokümantasyonu)

---

## 💡 Özet

1. **Health Check**: Sistemin tüm bileşenlerini kontrol eder (sadece API değil)
2. **Tahmin**: Gerçek uçuş gecikmesi değil, hash bucket değeri döndürür
3. **Amaç**: MLOps pipeline ve feature engineering demo'su
