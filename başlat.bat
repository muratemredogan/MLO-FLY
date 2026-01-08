@echo off
chcp 65001 >nul
echo ========================================
echo   Flight Delay Prediction API Başlatılıyor
echo ========================================
echo.

REM Python kontrolü
echo [1/6] Python kontrol ediliyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı! Lütfen Python'u yükleyin.
    pause
    exit /b 1
)
python --version
echo ✓ Python bulundu
echo.

REM Bağımlılıkları kontrol et ve kur
echo [2/6] Bağımlılıklar kontrol ediliyor...
if not exist "venv\" (
    echo Virtual environment oluşturuluyor...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo ✓ Virtual environment aktif
echo.

echo [3/6] Paketler kuruluyor...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [HATA] Paket kurulumu başarısız!
    pause
    exit /b 1
)
echo ✓ Paketler kuruldu
echo.

REM Eski API sürecini durdur (varsa)
echo [4/6] Eski API süreçleri temizleniyor...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo ✓ Temizlik tamamlandı
echo.

REM API'yi başlat (arka planda)
echo [5/6] API başlatılıyor...
start "Flight Delay Prediction API" /min cmd /c "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ✓ API başlatıldı
echo.

REM API'nin hazır olmasını bekle
echo [6/6] API'nin hazır olması bekleniyor...
set /a counter=0
:wait_loop
timeout /t 2 /nobreak >nul
python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" >nul 2>&1
if errorlevel 1 (
    set /a counter+=1
    if %counter% lss 15 (
        echo API hazırlanıyor... (%counter%/15)
        goto wait_loop
    ) else (
        echo [UYARI] API yanıt vermiyor, devam ediliyor...
    )
) else (
    echo ✓ API hazır!
)
echo.

REM Test çalıştır
echo ========================================
echo   API Test Ediliyor
echo ========================================
echo.
call venv\Scripts\activate.bat
python test_api.py
echo.

REM Web tarayıcısını aç
echo ========================================
echo   Web Tarayıcısı Açılıyor
echo ========================================
echo.
timeout /t 2 /nobreak >nul
if exist "%~dp0index.html" (
    start "" "%~dp0index.html"
    echo ✓ Web arayüzü açıldı (index.html)
)
start http://localhost:8000/docs
echo ✓ Swagger UI: http://localhost:8000/docs
echo ✓ API Health: http://localhost:8000/health
echo.

echo ========================================
echo   Sistem Hazır!
echo ========================================
echo.
echo API çalışıyor: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo API'yi durdurmak için bu pencereyi kapatın.
echo.
pause
