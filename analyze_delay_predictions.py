"""
Gecikme Tahminlerini Analiz Et
Modelin tahmin ettiği gecikme oranını kontrol eder.
"""
import pandas as pd
import pickle
import os
import numpy as np
from app.feature_engineering import hash_airport_code

def analyze_predictions(sample_size=5000):
    """Model tahminlerini analiz et."""
    print("=" * 70)
    print("GECİKME TAHMİN ORANI ANALİZİ")
    print("=" * 70)
    
    # Modeli yükle
    model_path = os.path.join('models', 'model.pkl')
    features_path = os.path.join('models', 'model_features.pkl')
    
    if not os.path.exists(model_path):
        print("❌ Model bulunamadı! Lütfen train_model.py çalıştırın.")
        return
    
    print("\n[1/4] Model yükleniyor...")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(features_path, 'rb') as f:
        model_features = pickle.load(f)
    print("✓ Model yüklendi")
    
    # Veriyi yükle
    print(f"\n[2/4] Veri yükleniyor ({sample_size} örnek)...")
    df = pd.read_csv('Airlines.csv')
    
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
    
    # Gerçek gecikme oranı
    real_delay_rate = df['Delay'].mean()
    real_delay_count = df['Delay'].sum()
    
    print(f"✓ Veri yüklendi: {len(df)} örnek")
    print(f"\n📊 GERÇEK VERİ İSTATİSTİKLERİ:")
    print(f"   Gecikme var: {real_delay_count} ({real_delay_rate*100:.2f}%)")
    print(f"   Gecikme yok: {len(df) - real_delay_count} ({(1-real_delay_rate)*100:.2f}%)")
    
    # Özellikleri hazırla
    print(f"\n[3/4] Özellikler hazırlanıyor...")
    df['AirportFrom_Bucket'] = df['AirportFrom'].apply(
        lambda x: hash_airport_code(x, num_buckets=100)
    )
    df['AirportTo_Bucket'] = df['AirportTo'].apply(
        lambda x: hash_airport_code(x, num_buckets=100)
    )
    df['Airline_Encoded'] = df['Airline'].apply(
        lambda x: hash_airport_code(x, num_buckets=50)
    )
    
    features = [
        'DayOfWeek',
        'Time',
        'Length',
        'AirportFrom_Bucket',
        'AirportTo_Bucket',
        'Airline_Encoded'
    ]
    
    X = df[features].values
    y = df['Delay'].values
    print("✓ Özellikler hazırlandı")
    
    # Tahminler yap
    print(f"\n[4/4] Tahminler yapılıyor...")
    probabilities = model.predict_proba(X)[:, 1]
    
    # Farklı eşik değerleri ile test
    thresholds = [0.5, 0.6, 0.65, 0.7]
    
    print(f"\n" + "=" * 70)
    print("TAHMIN SONUÇLARI (Farklı Eşik Değerleri)")
    print("=" * 70)
    
    results = []
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)
        pred_rate = predictions.mean()
        pred_count = predictions.sum()
        difference = abs(pred_rate - real_delay_rate) * 100
        
        results.append({
            'threshold': threshold,
            'pred_rate': pred_rate,
            'pred_count': pred_count,
            'difference': difference
        })
        
        status = "✓" if difference < 5 else "⚠️" if difference < 10 else "❌"
        print(f"\n{status} Eşik = {threshold:.2f}:")
        print(f"   Tahmin edilen gecikme: {pred_count} ({pred_rate*100:.2f}%)")
        print(f"   Gerçek gecikme: {real_delay_count} ({real_delay_rate*100:.2f}%)")
        print(f"   Fark: {difference:.2f}%")
    
    # En iyi eşik değerini bul
    best_threshold = min(results, key=lambda x: x['difference'])
    
    print(f"\n" + "=" * 70)
    print("ÖNERİ")
    print("=" * 70)
    print(f"✓ En iyi eşik değeri: {best_threshold['threshold']:.2f}")
    print(f"   Bu eşik ile tahmin oranı: {best_threshold['pred_rate']*100:.2f}%")
    print(f"   Gerçek oran: {real_delay_rate*100:.2f}%")
    print(f"   Fark: {best_threshold['difference']:.2f}%")
    
    # Mevcut kodda kullanılan eşik (0.6)
    current_threshold = 0.6
    current_pred = (probabilities >= current_threshold).astype(int)
    current_rate = current_pred.mean()
    current_diff = abs(current_rate - real_delay_rate) * 100
    
    print(f"\n📌 MEVCUT AYAR (Eşik=0.6):")
    print(f"   Tahmin oranı: {current_rate*100:.2f}%")
    print(f"   Gerçek oran: {real_delay_rate*100:.2f}%")
    print(f"   Fark: {current_diff:.2f}%")
    
    if current_rate > real_delay_rate * 1.15:
        print(f"\n⚠️  UYARI: Model hala gerçekten %{((current_rate/real_delay_rate - 1)*100):.1f} daha fazla gecikme tahmin ediyor!")
        print(f"   Önerilen eşik: {best_threshold['threshold']:.2f}")
    elif current_rate < real_delay_rate * 0.85:
        print(f"\n⚠️  UYARI: Model gerçekten %{((1 - current_rate/real_delay_rate)*100):.1f} daha az gecikme tahmin ediyor!")
    else:
        print(f"\n✓ Model tahminleri gerçek orana yakın görünüyor.")

if __name__ == "__main__":
    try:
        analyze_predictions(sample_size=10000)
    except FileNotFoundError as e:
        print(f"\n❌ HATA: {e}")
        print("Lütfen Airlines.csv dosyasının mevcut olduğundan emin olun.")
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
