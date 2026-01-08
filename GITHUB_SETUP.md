# GitHub'a Bağlama Talimatları

## Adım 1: GitHub'da Yeni Repository Oluştur

1. GitHub.com'a git ve giriş yap
2. Sağ üstteki "+" butonuna tıkla → "New repository"
3. Repository adı: `mlops-hw2` (veya istediğin isim)
4. Description: "MLOps Homework 2 - CI/CD Pipeline Implementation"
5. Public veya Private seç (önerilen: Public)
6. **ÖNEMLİ:** "Initialize with README" seçme (zaten var)
7. "Create repository" butonuna tıkla

## Adım 2: Remote Repository Ekle ve Push Et

GitHub'da repository oluşturduktan sonra, GitHub sana bir URL verecek. 
Örnek: `https://github.com/KULLANICI_ADIN/mlops-hw2.git`

Aşağıdaki komutları çalıştır (URL'yi kendi repository URL'inle değiştir):

```bash
# Remote repository ekle
git remote add origin https://github.com/KULLANICI_ADIN/mlops-hw2.git

# Branch'i main olarak ayarla (GitHub default)
git branch -M main

# GitHub'a push et
git push -u origin main
```

## Alternatif: SSH Kullanıyorsan

```bash
git remote add origin git@github.com:KULLANICI_ADIN/mlops-hw2.git
git branch -M main
git push -u origin main
```

## Adım 3: GitHub Actions'ı Aktifleştir

1. GitHub repository sayfasına git
2. "Actions" tab'ına tıkla
3. İlk kez açıyorsan "I understand my workflows, go ahead and enable them" butonuna tıkla
4. `.github/workflows/main.yml` dosyası otomatik olarak çalışacak

## Test Et

1. Herhangi bir dosyada küçük bir değişiklik yap
2. Commit ve push et:
   ```bash
   git add .
   git commit -m "Test commit"
   git push
   ```
3. GitHub'da "Actions" tab'ına git
4. Pipeline'ın çalıştığını göreceksin!

## Sorun Giderme

### Authentication Hatası
- GitHub Personal Access Token kullanman gerekebilir
- Settings → Developer settings → Personal access tokens → Generate new token
- Token'ı şifre olarak kullan

### Branch Hatası
- Eğer "main" branch yoksa: `git branch -M main`
- Eğer "master" kullanıyorsan: `git push -u origin master`

