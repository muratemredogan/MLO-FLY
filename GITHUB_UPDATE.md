# GitHub Güncelleme Komutları

Terminal'e sırayla yapıştırın:

## 1. Tüm değişiklikleri ekle
```bash
git add .
```

## 2. Commit yap
```bash
git commit -m "ML model entegrasyonu: Gerçek uçuş gecikmesi tahmin sistemi eklendi"
```

## 3. GitHub'a gönder
```bash
git push origin main
```

---

## Alternatif: Tek tek eklemek isterseniz

```bash
# Değiştirilmiş dosyalar
git add .gitignore
git add app/main.py
git add başlat.bat
git add index.html
git add requirements.txt

# Yeni dosyalar
git add README_MODEL.md
git add train_model.py

# Commit
git commit -m "ML model entegrasyonu: Gerçek uçuş gecikmesi tahmin sistemi eklendi"

# Push
git push origin main
```

---

**Not:** Airlines.csv dosyası .gitignore'da olduğu için otomatik olarak eklenmeyecek (dosya çok büyük).
