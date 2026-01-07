# MLOps Homework 2 - CI/CD Pipeline

Flight Delay Prediction servisi için MLOps CI/CD pipeline implementasyonu.

## Proje Yapısı

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI REST API
│   └── feature_engineering.py  # Hashing logic
├── tests/
│   ├── test_unit_hashing.py    # Unit tests (fast, pure)
│   └── test_component_fs.py    # Component tests (filesystem)
├── scripts/
│   └── smoke_test.py           # End-to-end smoke test
├── Dockerfile
├── requirements.txt
└── .github/workflows/main.yml
```

## Pipeline Aşamaları

1. **Build** - Python dependencies kurulumu
2. **Unit Test** - Hızlı, bağımlılıksız unit testler
3. **Lint** - Kod kalitesi kontrolü (flake8)
4. **Package** - Docker container build
5. **Smoke Test** - Container başlatma ve HTTP 200 kontrolü

## Lokal Çalıştırma

### 1. Dependencies Kurulumu

```bash
pip install -r requirements.txt
```

### 2. Testleri Çalıştır

```bash
pytest tests/
```

### 3. Lint Kontrolü

```bash
flake8 app/ tests/
```

### 4. API'yi Lokal Çalıştır

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Docker ile Çalıştır

```bash
# Build
docker build -t mlops-hw2 .

# Run
docker run -d -p 8000:8000 --name mlops-hw2-container mlops-hw2

# Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"departure_airport":"JFK"}'

# Cleanup
docker stop mlops-hw2-container
docker rm mlops-hw2-container
```

### 6. Smoke Test Çalıştır

```bash
python scripts/smoke_test.py
```

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### POST /predict
Airport kodunu hash bucket'a çevirir.

**Request:**
```json
{
  "departure_airport": "JFK"
}
```

**Response:**
```json
{
  "bucket": 42
}
```

## Stop-the-Line Demo

Pipeline'ın hata durumunda deployment'ı durdurduğunu göstermek için:

1. Bir bug ekle (örn: `app/feature_engineering.py` içinde `return bucket + 1000`)
2. Commit ve push yap
3. GitHub Actions'da pipeline'ın fail olduğunu göster
4. Bug'ı düzelt ve tekrar push yap
5. Pipeline'ın başarılı olduğunu göster

