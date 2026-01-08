@echo off
chcp 65001 >nul
echo ========================================
echo   Flight Delay Prediction API Başlatılıyor
echo ========================================
echo.

REM Python kontrolü - hem python hem py komutlarını dene
echo [1/6] Python kontrol ediliyor...
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Önce python komutunu dene
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    python --version
    echo ✓ Python bulundu (python komutu ile)
) else (
    REM py launcher'ı dene
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        set PYTHON_FOUND=1
        py --version
        echo ✓ Python bulundu (py komutu ile)
    )
)

REM Python bulunamadıysa hata ver
if "%PYTHON_FOUND%"=="0" (
    echo [HATA] Python bulunamadı!
    echo.
    echo Python yüklü görünüyor ama komut satırından erişilemiyor.
    echo.
    echo Çözüm önerileri:
    echo 1. Python'u yeniden yükleyin ve "Add Python to PATH" seçeneğini işaretleyin
    echo 2. Veya manuel olarak PATH'e ekleyin
    echo 3. Veya py launcher kullanın: py --version
    echo.
    echo Şu anda çalışan komutları test edin:
    python --version
    py --version
    echo.
    pause
    exit /b 1
)

REM PYTHON_CMD'in set edildiğini kontrol et
if "%PYTHON_CMD%"=="" (
    echo [HATA] Python komutu belirlenemedi!
    pause
    exit /b 1
)
echo.

REM Bağımlılıkları kontrol et ve kur
echo [2/6] Bağımlılıklar kontrol ediliyor...
if not exist "venv\" (
    echo Virtual environment oluşturuluyor...
    echo Komut: %PYTHON_CMD% -m venv venv
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [HATA] Virtual environment oluşturulamadı!
        echo.
        echo Lütfen şunu manuel olarak deneyin:
        echo %PYTHON_CMD% -m venv venv
        echo.
        pause
        exit /b 1
    )
    echo ✓ Virtual environment oluşturuldu
) else (
    echo ✓ Virtual environment zaten mevcut
)

REM Virtual environment'ı aktifleştir
if not exist "venv\Scripts\activate.bat" (
    echo [HATA] Virtual environment düzgün oluşturulmamış!
    echo venv klasörünü silip tekrar deneyin.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [HATA] Virtual environment aktifleştirilemedi!
    pause
    exit /b 1
)

REM Venv içinde python'un çalıştığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Virtual environment içinde Python bulunamadı!
    echo venv klasörünü silip tekrar deneyin.
    pause
    exit /b 1
)
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

REM Model kontrolü ve eğitimi
echo [3.5/6] Model kontrol ediliyor...
if not exist "models\model.pkl" (
    echo Model bulunamadı, eğitiliyor...
    if exist "Airlines.csv" (
        call venv\Scripts\activate.bat
        python train_model.py
        if errorlevel 1 (
            echo [UYARI] Model eğitimi başarısız, ancak devam ediliyor...
        ) else (
            echo ✓ Model eğitildi ve kaydedildi
        )
    ) else (
        echo [UYARI] Airlines.csv bulunamadı, model eğitilemedi!
        echo Model olmadan API çalışacak ama tahmin yapamayacak.
    )
) else (
    echo ✓ Model mevcut
)
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
call venv\Scripts\activate.bat
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
if errorlevel 1 (
    echo [UYARI] Test sırasında bazı hatalar olabilir, ancak devam ediliyor...
)
echo.

REM Web tarayıcısını aç
echo ========================================
echo   Web Tarayıcısı Açılıyor
echo ========================================
echo.
timeout /t 3 /nobreak >nul
start http://localhost:8000
echo ✓ Web arayüzü açıldı: http://localhost:8000
timeout /t 1 /nobreak >nul
start http://localhost:8000/docs
echo ✓ Swagger UI: http://localhost:8000/docs
echo ✓ API Health: http://localhost:8000/health
echo.

echo ========================================
echo   Sistem Hazır!
echo ========================================
echo.
echo ✓ Web Arayüzü: http://localhost:8000
echo ✓ Swagger UI: http://localhost:8000/docs
echo ✓ Health Check: http://localhost:8000/health
echo.
echo NOT: API'yi durdurmak için bu pencereyi kapatın.
echo      Veya arka planda çalışan "Flight Delay Prediction API" penceresini kapatın.
echo.
pause
