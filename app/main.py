"""
FastAPI REST API for Flight Delay Prediction service.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from app.feature_engineering import hash_airport_code
import os
from datetime import datetime

app = FastAPI(
    title="Flight Delay Prediction API",
    description="MLOps Homework 2 - CI/CD Pipeline Demo",
    version="1.0.0"
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm origin'lere izin ver (production'da kısıtlayın)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    """Request model for /predict endpoint."""
    departure_airport: str = Field(..., description="IATA airport code (e.g., 'JFK')")


class PredictionResponse(BaseModel):
    """Response model for /predict endpoint."""
    bucket: int = Field(..., description="Hash bucket index (0 to 99)")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(default="ok", description="Service status")


@app.get("/")
async def root():
    """Ana sayfa - HTML arayüzünü döndür."""
    # Proje kök dizinini bul
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    html_path = os.path.join(project_root, "index.html")
    
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    return {"message": "Flight Delay Prediction API", "docs": "/docs"}


@app.get("/health", status_code=200)
async def health_check(request: Request):
    """
    Health check endpoint - Sistem sağlık kontrolü.
    
    PRENSİP:
    1. API'nin çalışıp çalışmadığını kontrol eder
    2. Sistem bileşenlerinin durumunu kontrol eder
    3. Zaman damgası ile son kontrol zamanını gösterir
    
    Şu anda kontrol edilenler:
    - API servisi (çalışıyor mu?)
    - Python modülleri (yüklü mü?)
    - Hash fonksiyonu (çalışıyor mu?)
    
    Gelecekte eklenebilecekler:
    - Veritabanı bağlantısı
    - Dış API servisleri
    - Disk alanı
    - Bellek kullanımı
    
    Returns JSON or HTML based on Accept header.
    """
    # Sistem bileşenlerini kontrol et
    checks = {
        "api": {"status": "ok", "message": "API servisi çalışıyor"},
        "python_modules": {"status": "ok", "message": "Gerekli modüller yüklü"},
        "hash_function": {"status": "ok", "message": "Hash fonksiyonu çalışıyor"}
    }
    
    # Hash fonksiyonunu test et
    try:
        test_bucket = hash_airport_code("TEST", num_buckets=100)
        if not isinstance(test_bucket, int) or test_bucket < 0 or test_bucket >= 100:
            checks["hash_function"]["status"] = "error"
            checks["hash_function"]["message"] = "Hash fonksiyonu beklenmeyen değer döndürüyor"
    except Exception as e:
        checks["hash_function"]["status"] = "error"
        checks["hash_function"]["message"] = f"Hash fonksiyonu hatası: {str(e)}"
    
    # Genel durum: Tüm kontroller başarılı mı?
    overall_status = "ok" if all(c["status"] == "ok" for c in checks.values()) else "degraded"
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "service": "Flight Delay Prediction API",
        "version": "1.0.0",
        "checks": checks,
        "uptime_info": "Sistem çalışıyor - Tüm bileşenler aktif"
    }
    
    # Eğer tarayıcıdan geliyorsa HTML döndür
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header or "html" in accept_header.lower():
        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Health Check - Flight Delay Prediction API</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    padding: 40px;
                    max-width: 600px;
                    width: 100%;
                    text-align: center;
                }}
                h1 {{
                    color: #28a745;
                    margin-bottom: 20px;
                    font-size: 2.5em;
                }}
                .status {{
                    font-size: 1.2em;
                    color: #28a745;
                    margin-bottom: 30px;
                    font-weight: 600;
                }}
                .info {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: left;
                }}
                .info-item {{
                    margin: 10px 0;
                    padding: 10px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .info-item:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: 600;
                    color: #333;
                }}
                .value {{
                    color: #666;
                    margin-left: 10px;
                }}
                .links {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
                .links a {{
                    color: #667eea;
                    text-decoration: none;
                    margin: 0 15px;
                    font-weight: 600;
                    display: inline-block;
                    margin-top: 10px;
                }}
                .links a:hover {{
                    text-decoration: underline;
                }}
                .checkmark {{
                    font-size: 4em;
                    color: #28a745;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="checkmark">✓</div>
                <h1>API Sağlık Durumu</h1>
                <div class="status">Sistem Çalışıyor</div>
                <div class="info">
                    <div class="info-item">
                        <span class="label">Genel Durum:</span>
                        <span class="value" style="color: {'#28a745' if health_data['status'] == 'ok' else '#ffc107'}; font-weight: bold;">{health_data['status'].upper()}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Servis:</span>
                        <span class="value">{health_data['service']}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Versiyon:</span>
                        <span class="value">{health_data['version']}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Kontrol Zamanı:</span>
                        <span class="value">{health_data['timestamp']}</span>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                    <h3 style="margin-bottom: 15px; color: #333;">Bileşen Kontrolleri:</h3>
                    {''.join([f'''
                    <div style="padding: 10px; margin: 5px 0; background: white; border-radius: 5px; border-left: 4px solid {'#28a745' if check['status'] == 'ok' else '#dc3545'};">
                        <strong>{name.upper()}:</strong> 
                        <span style="color: {'#28a745' if check['status'] == 'ok' else '#dc3545'};">
                            {'✓' if check['status'] == 'ok' else '✗'} {check['message']}
                        </span>
                    </div>
                    ''' for name, check in health_data['checks'].items()])}
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 10px; border-left: 4px solid #2196F3;">
                    <h4 style="color: #1976D2; margin-bottom: 10px;">ℹ️ Health Check Prensibi:</h4>
                    <p style="color: #555; font-size: 0.9em; line-height: 1.6;">
                        <strong>Nasıl Çalışıyor?</strong><br>
                        Health check endpoint'i sistemin tüm kritik bileşenlerini kontrol eder:
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            <li>API servisinin çalışıp çalışmadığı</li>
                            <li>Python modüllerinin yüklü olup olmadığı</li>
                            <li>Hash fonksiyonunun düzgün çalışıp çalışmadığı</li>
                        </ul>
                        <strong style="margin-top: 10px; display: block;">Sadece API mi kontrol ediyor?</strong><br>
                        Hayır! Şu anda API, modüller ve hash fonksiyonu kontrol ediliyor. 
                        Gelecekte veritabanı, dış servisler ve sistem kaynakları da eklenebilir.
                    </p>
                </div>
                <div class="links">
                    <a href="/">🏠 Ana Sayfa</a>
                    <a href="/docs">📚 Swagger UI</a>
                    <a href="/health?format=json">📄 JSON Format</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # JSON format isteği veya varsayılan
    return JSONResponse(content=health_data)


@app.post("/predict", response_model=PredictionResponse, status_code=200)
async def predict(request: PredictionRequest):
    """
    Predict hash bucket for departure airport code.
    
    Args:
        request: PredictionRequest with departure_airport field
    
    Returns:
        PredictionResponse with bucket index
    
    Raises:
        HTTPException: If airport code is invalid
    """
    try:
        bucket = hash_airport_code(request.departure_airport, num_buckets=100)
        return {"bucket": bucket}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

