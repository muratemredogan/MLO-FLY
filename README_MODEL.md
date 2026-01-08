# ML Model Eğitimi ve Kullanımı

## Model Eğitimi

### Otomatik Eğitim
`başlat.bat` dosyası çalıştırıldığında, eğer model yoksa otomatik olarak eğitilir.

### Manuel Eğitim
Modeli manuel olarak eğitmek için:

```bash
# Virtual environment'ı aktifleştir
venv\Scripts\activate.bat

# Modeli eğit
python train_model.py
```

## Model Detayları

### Kullanılan Algoritma
- **Random Forest Classifier**
- 100 ağaç (n_estimators=100)
- Maksimum derinlik: 20
- Class weight: balanced (dengesiz veri için)

### Özellikler (Features)
1. `DayOfWeek` - Haftanın günü (1-7)
2. `Time` - Kalkış saati (dakika cinsinden, 0-1439)
3. `Length` - Uçuş süresi (dakika)
4. `AirportFrom_Bucket` - Kalkış havaalanı hash bucket (0-99)
5. `AirportTo_Bucket` - Varış havaalanı hash bucket (0-99)
6. `Airline_Encoded` - Havayolu şirketi hash bucket (0-49)

### Model Dosyaları
- `models/model.pkl` - Eğitilmiş model
- `models/model_features.pkl` - Özellik listesi

## API Kullanımı

### Endpoint: POST /predict

**Request:**
```json
{
  "departure_airport": "JFK",
  "arrival_airport": "LAX",
  "airline": "AA",
  "day_of_week": 3,
  "time": 900,
  "length": 300
}
```

**Response:**
```json
{
  "delay_prediction": true,
  "delay_probability": 0.65,
  "confidence": "Orta",
  "message": "Uçuş gecikmesi bekleniyor. Olasılık: 65.0%"
}
```

## Model Performansı

Model eğitildikten sonra terminalde şu bilgiler gösterilir:
- Test Accuracy
- Classification Report
- Confusion Matrix

## Notlar

- Model dosyaları `.gitignore`'da olduğu için git'e eklenmez
- Her yeni dataset ile model yeniden eğitilmelidir
- Model eğitimi birkaç dakika sürebilir (500K+ satır)
