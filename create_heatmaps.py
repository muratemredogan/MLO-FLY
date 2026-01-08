"""
Gecikme Oranı Isı Haritaları Oluşturma Scripti
- Havalimanları eşleştirmeleri ile gecikme oranı ısı haritası
- Uçuş süreleri ile gecikme oranı ısı haritası

Kullanım:
    python create_heatmaps.py
    
Gereksinimler:
    pip install matplotlib seaborn
"""
import pandas as pd
import numpy as np
import os
import sys

# Matplotlib ve seaborn import kontrolü
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print("=" * 60)
    print("HATA: Gerekli kütüphaneler yüklü değil!")
    print("=" * 60)
    print("\nLütfen şu komutu çalıştırın:")
    print("  pip install matplotlib seaborn")
    print("\nVeya virtual environment kullanıyorsanız:")
    print("  venv\\Scripts\\activate")
    print("  pip install matplotlib seaborn")
    sys.exit(1)

from pathlib import Path

# Türkçe karakter desteği için
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_data(csv_path='Airlines.csv'):
    """Veriyi yükle ve temel bilgileri göster."""
    print("=" * 60)
    print("Veri Yukleniyor...")
    print("=" * 60)
    
    df = pd.read_csv(csv_path)
    print(f"[OK] Toplam kayit sayisi: {len(df):,}")
    print(f"[OK] Gecikme orani: {df['Delay'].mean()*100:.2f}%")
    
    return df

def create_airport_heatmap(df, top_n=30):
    """
    Havalimanları eşleştirmeleri ile gecikme oranı ısı haritası oluştur.
    
    Args:
        df: DataFrame
        top_n: En çok uçuş yapılan havalimanı çiftlerinin sayısı
    """
    print("\n" + "=" * 60)
    print("Havalimanlari Eslesmeleri Isi Haritasi Olusturuluyor...")
    print("=" * 60)
    
    # Havalimanı çiftlerine göre gecikme oranını hesapla
    airport_pairs = df.groupby(['AirportFrom', 'AirportTo']).agg({
        'Delay': ['mean', 'count']
    }).reset_index()
    
    airport_pairs.columns = ['AirportFrom', 'AirportTo', 'DelayRate', 'FlightCount']
    
    # En çok uçuş yapılan havalimanı çiftlerini seç
    top_pairs = airport_pairs.nlargest(top_n, 'FlightCount')
    
    print(f"[OK] En cokucus yapilan {top_n} havalimani cifti secildi")
    
    # Pivot table oluştur (kalkış havalimanları satır, varış havalimanları sütun)
    # Sadece seçilen çiftleri kullan
    pivot_data = top_pairs.pivot_table(
        values='DelayRate',
        index='AirportFrom',
        columns='AirportTo',
        aggfunc='mean'
    )
    
    # Eksik değerleri 0 ile doldur (o çift için veri yoksa)
    pivot_data = pivot_data.fillna(0)
    
    # Isı haritası oluştur
    plt.figure(figsize=(16, 12))
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn_r',  # Kırmızı (yüksek gecikme) - Yeşil (düşük gecikme)
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Gecikme Oranı'},
        linewidths=0.5,
        linecolor='gray',
        square=False
    )
    
    plt.title(
        f'Gecikme Oranı - Havalimanları Eşleştirmeleri\n(En Çok Uçuş Yapılan {top_n} Havalimanı Çifti)',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    plt.xlabel('Varış Havalimanı (AirportTo)', fontsize=12, fontweight='bold')
    plt.ylabel('Kalkış Havalimanı (AirportFrom)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Kaydet
    output_path = 'heatmap_airport_pairs.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Isi haritasi kaydedildi: {output_path}")
    
    plt.close()

def create_length_heatmap(df):
    """
    Uçuş süreleri ile gecikme oranı ısı haritası oluştur.
    Uçuş sürelerini aralıklara bölerek analiz eder.
    """
    print("\n" + "=" * 60)
    print("Ucus Sureleri Isi Haritasi Olusturuluyor...")
    print("=" * 60)
    
    # Uçuş sürelerini aralıklara böl (30 dakikalık aralıklar)
    max_length = int(df['Length'].max())
    bins = list(range(0, max_length + 60, 30))
    labels = [f"{i}-{i+30}" for i in range(0, max_length, 30)]
    
    # Bin sayısı label sayısından 1 fazla olmalı
    if len(bins) > len(labels) + 1:
        bins = bins[:len(labels) + 1]
    elif len(bins) < len(labels) + 1:
        bins = list(range(0, (len(labels) + 1) * 30, 30))
    
    df['Length_Bin'] = pd.cut(
        df['Length'],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    
    # Haftanın günü ile uçuş süresine göre gecikme oranını hesapla
    length_day_heatmap = df.groupby(['Length_Bin', 'DayOfWeek'])['Delay'].mean().reset_index()
    length_day_heatmap.columns = ['Length_Bin', 'DayOfWeek', 'DelayRate']
    
    # Pivot table oluştur
    pivot_data = length_day_heatmap.pivot_table(
        values='DelayRate',
        index='Length_Bin',
        columns='DayOfWeek',
        aggfunc='mean'
    )
    
    # Eksik değerleri 0 ile doldur
    pivot_data = pivot_data.fillna(0)
    
    # Gün isimleri
    day_names = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
    pivot_data.columns = [f'{day_names[i-1]} ({i})' for i in pivot_data.columns]
    
    # Isı haritası oluştur
    plt.figure(figsize=(14, 10))
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn_r',
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Gecikme Oranı'},
        linewidths=0.5,
        linecolor='gray'
    )
    
    plt.title(
        'Gecikme Oranı - Uçuş Süreleri ve Haftanın Günleri',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    plt.xlabel('Haftanın Günü', fontsize=12, fontweight='bold')
    plt.ylabel('Uçuş Süresi (dakika)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Kaydet
    output_path = 'heatmap_flight_length.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Isi haritasi kaydedildi: {output_path}")
    
    plt.close()

def create_length_time_heatmap(df):
    """
    Uçuş süreleri ile kalkış saatine göre gecikme oranı ısı haritası oluştur.
    """
    print("\n" + "=" * 60)
    print("Ucus Sureleri ve Kalkis Saati Isi Haritasi Olusturuluyor...")
    print("=" * 60)
    
    # Uçuş sürelerini aralıklara böl
    max_length = int(df['Length'].max())
    bins_length = list(range(0, max_length + 60, 30))
    labels_length = [f"{i}-{i+30}" for i in range(0, max_length, 30)]
    
    # Bin sayısı label sayısından 1 fazla olmalı
    if len(bins_length) > len(labels_length) + 1:
        bins_length = bins_length[:len(labels_length) + 1]
    elif len(bins_length) < len(labels_length) + 1:
        bins_length = list(range(0, (len(labels_length) + 1) * 30, 30))
    
    df['Length_Bin'] = pd.cut(
        df['Length'],
        bins=bins_length,
        labels=labels_length,
        include_lowest=True
    )
    
    # Kalkış saatini saat aralıklarına böl (2 saatlik aralıklar)
    df['Time_Hour'] = df['Time'] // 60
    bins_time = list(range(0, 25, 2))
    labels_time = [f"{i:02d}:00-{i+2:02d}:00" for i in range(0, 24, 2)]
    
    df['Time_Bin'] = pd.cut(
        df['Time_Hour'],
        bins=bins_time,
        labels=labels_time,
        include_lowest=True
    )
    
    # Uçuş süresi ve kalkış saatine göre gecikme oranını hesapla
    length_time_heatmap = df.groupby(['Length_Bin', 'Time_Bin'])['Delay'].mean().reset_index()
    length_time_heatmap.columns = ['Length_Bin', 'Time_Bin', 'DelayRate']
    
    # Pivot table oluştur
    pivot_data = length_time_heatmap.pivot_table(
        values='DelayRate',
        index='Length_Bin',
        columns='Time_Bin',
        aggfunc='mean'
    )
    
    # Eksik değerleri 0 ile doldur
    pivot_data = pivot_data.fillna(0)
    
    # Isı haritası oluştur
    plt.figure(figsize=(16, 10))
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn_r',
        center=0.5,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Gecikme Oranı'},
        linewidths=0.5,
        linecolor='gray'
    )
    
    plt.title(
        'Gecikme Oranı - Uçuş Süreleri ve Kalkış Saatleri',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    plt.xlabel('Kalkış Saati', fontsize=12, fontweight='bold')
    plt.ylabel('Uçuş Süresi (dakika)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Kaydet
    output_path = 'heatmap_length_time.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Isi haritasi kaydedildi: {output_path}")
    
    plt.close()

def main():
    """Ana fonksiyon."""
    print("\n" + "=" * 60)
    print("GECIKME ORANI ISI HARITALARI OLUSTURULUYOR")
    print("=" * 60)
    
    # Veriyi yükle
    df = load_data('Airlines.csv')
    
    # 1. Havalimanları eşleştirmeleri ısı haritası
    create_airport_heatmap(df, top_n=30)
    
    # 2. Uçuş süreleri ve haftanın günleri ısı haritası
    create_length_heatmap(df)
    
    # 3. Uçuş süreleri ve kalkış saatleri ısı haritası
    create_length_time_heatmap(df)
    
    print("\n" + "=" * 60)
    print("TUM ISI HARITALARI BASARIYLA OLUSTURULDU!")
    print("=" * 60)
    print("\nOlusturulan dosyalar:")
    print("  - heatmap_airport_pairs.png (Havalimanlari eslesmeleri)")
    print("  - heatmap_flight_length.png (Ucus sureleri ve haftanin gunleri)")
    print("  - heatmap_length_time.png (Ucus sureleri ve kalkis saatleri)")

if __name__ == "__main__":
    main()
