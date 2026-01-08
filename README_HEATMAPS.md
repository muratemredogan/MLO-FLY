# Gecikme Oranı Isı Haritaları

Bu script, Airlines.csv verisini kullanarak gecikme oranı ile ilgili ısı haritaları oluşturur.

## Oluşturulan Isı Haritaları

1. **Havalimanları Eşleştirmeleri Isı Haritası** (`heatmap_airport_pairs.png`)
   - Kalkış ve varış havalimanları arasındaki gecikme oranlarını gösterir
   - En çok uçuş yapılan 30 havalimanı çifti analiz edilir

2. **Uçuş Süreleri ve Haftanın Günleri Isı Haritası** (`heatmap_flight_length.png`)
   - Uçuş süreleri (30 dakikalık aralıklar) ve haftanın günlerine göre gecikme oranlarını gösterir

3. **Uçuş Süreleri ve Kalkış Saatleri Isı Haritası** (`heatmap_length_time.png`)
   - Uçuş süreleri ve kalkış saatlerine göre gecikme oranlarını gösterir

## Kullanım

### 1. Gerekli Kütüphaneleri Yükleyin

Virtual environment kullanıyorsanız:
```bash
venv\Scripts\activate
pip install matplotlib seaborn
```

Veya doğrudan:
```bash
pip install matplotlib seaborn
```

### 2. Scripti Çalıştırın

```bash
python create_heatmaps.py
```

Veya virtual environment ile:
```bash
venv\Scripts\activate
python create_heatmaps.py
```

## Çıktı Dosyaları

Script çalıştırıldığında aşağıdaki PNG dosyaları oluşturulur:

- `heatmap_airport_pairs.png` - Havalimanları eşleştirmeleri
- `heatmap_flight_length.png` - Uçuş süreleri ve haftanın günleri
- `heatmap_length_time.png` - Uçuş süreleri ve kalkış saatleri

## Notlar

- Tüm ısı haritaları 300 DPI çözünürlükte kaydedilir
- Kırmızı renkler yüksek gecikme oranını, yeşil renkler düşük gecikme oranını gösterir
- Her hücrede gecikme oranı (0.00-1.00 arası) gösterilir
