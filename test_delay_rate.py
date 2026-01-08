"""
Gecikme Oranı Test Scripti
Modelin tahmin ettiği gecikme oranını gerçek verilerle karşılaştırır.
"""
import pandas as pd
import pickle
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from app.feature_engineering import hash_airport_code

def load_model():
    """Modeli yükle."""
    model_path = os.path.join('models', 'model.pkl')
    features_path = os.path.join('models', 'model_features.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        print("❌ Model dosyası bulunamadı! Lütfen train_model.py çalıştırın.")
        return None, None
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(features_path, 'rb') as f:
        model_features = pickle.load(f)
    
    return model, model_features

def prepare_test_data(csv_path='Airlines.csv', sample_size=10000):
    """Test verilerini hazırla."""
    print("=" * 60)
    print("Test Verileri Hazırlanıyor...")
    print("=" * 60)
    
    df = pd.read_csv(csv_path)
    
    # Örnekleme (hızlı test için)
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
        print(f"✓ {sample_size} örnek seçildi (toplam {len(pd.read_csv(csv_path))} kayıttan)")
    
    # Gerçek gecikme oranı
    real_delay_rate = df['Delay'].mean()
    print(f"\n📊 Gerçek Veri İstatistikleri:")
    print(f"  - Toplam örnek: {len(df)}")
    print(f"  - Gecikme var (Delay=1): {df['Delay'].sum()} ({real_delay_rate*100:.2f}%)")
    print(f"  - Gecikme yok (Delay=0): {(df['Delay']==0).sum()} ({(1-real_delay_rate)*100:.2f}%)")
    
    # Özellik mühendisliği
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
    
    return X, y, real_delay_rate

def test_model_predictions(model, model_features, X, y, threshold=0.5):
    """Model tahminlerini test et."""
    print("\n" + "=" * 60)
    print(f"Model Tahminleri Test Ediliyor (Eşik={threshold})...")
    print("=" * 60)
    
    # Olasılık tahminleri
    probabilities = model.predict_proba(X)[:, 1]
    
    # Farklı eşik değerleri ile tahminler
    predictions_05 = (probabilities >= threshold).astype(int)
    predictions_06 = (probabilities >= 0.6).astype(int)
    predictions_07 = (probabilities >= 0.7).astype(int)
    
    # Tahmin edilen gecikme oranları
    pred_rate_05 = predictions_05.mean()
    pred_rate_06 = predictions_06.mean()
    pred_rate_07 = predictions_07.mean()
    
    print(f"\n📈 Tahmin Edilen Gecikme Oranları:")
    print(f"  - Eşik 0.5: {pred_rate_05*100:.2f}% ({predictions_05.sum()} gecikme)")
    print(f"  - Eşik 0.6: {pred_rate_06*100:.2f}% ({predictions_06.sum()} gecikme)")
    print(f"  - Eşik 0.7: {pred_rate_07*100:.2f}% ({predictions_07.sum()} gecikme)")
    
    # Confusion matrix (0.5 eşik ile)
    cm = confusion_matrix(y, predictions_05)
    print(f"\n📊 Confusion Matrix (Eşik=0.5):")
    print(f"                Tahmin")
    print(f"              Yok  Var")
    print(f"Gerçek Yok   {cm[0][0]:4d} {cm[0][1]:4d}")
    print(f"      Var    {cm[1][0]:4d} {cm[1][1]:4d}")
    
    # Sınıflandırma raporu
    print(f"\n📋 Detaylı Performans Raporu (Eşik=0.5):")
    print(classification_report(y, predictions_05, target_names=['Gecikme Yok', 'Gecikme Var']))
    
    return {
        'threshold_05': pred_rate_05,
        'threshold_06': pred_rate_06,
        'threshold_07': pred_rate_07,
        'real_rate': y.mean(),
        'probabilities': probabilities
    }

def analyze_probability_distribution(probabilities, y):
    """Olasılık dağılımını analiz et."""
    print("\n" + "=" * 60)
    print("Olasılık Dağılımı Analizi")
    print("=" * 60)
    
    # Olasılık aralıkları
    bins = [0, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0]
    labels = ['0-0.3', '0.3-0.4', '0.4-0.5', '0.5-0.6', '0.6-0.7', '0.7-1.0']
    
    print("\n📊 Olasılık Dağılımı:")
    for i in range(len(bins)-1):
        mask = (probabilities >= bins[i]) & (probabilities < bins[i+1])
        count = mask.sum()
        if count > 0:
            actual_delays = y[mask].sum()
            actual_rate = actual_delays / count if count > 0 else 0
            print(f"  {labels[i]}: {count:5d} örnek ({count/len(probabilities)*100:5.2f}%), "
                  f"Gerçek gecikme: {actual_delays:4d} ({actual_rate*100:5.2f}%)")

def find_optimal_threshold(probabilities, y):
    """Optimal eşik değerini bul."""
    print("\n" + "=" * 60)
    print("Optimal Eşik Değeri Analizi")
    print("=" * 60)
    
    from sklearn.metrics import f1_score, precision_score, recall_score
    
    thresholds = np.arange(0.3, 0.8, 0.05)
    results = []
    
    for thresh in thresholds:
        pred = (probabilities >= thresh).astype(int)
        f1 = f1_score(y, pred)
        precision = precision_score(y, pred)
        recall = recall_score(y, pred)
        pred_rate = pred.mean()
        
        results.append({
            'threshold': thresh,
            'f1': f1,
            'precision': precision,
            'recall': recall,
            'pred_rate': pred_rate
        })
    
    # En iyi F1 skoru
    best_f1 = max(results, key=lambda x: x['f1'])
    
    print(f"\n🎯 En İyi F1 Skoru:")
    print(f"  Eşik: {best_f1['threshold']:.2f}")
    print(f"  F1: {best_f1['f1']:.4f}")
    print(f"  Precision: {best_f1['precision']:.4f}")
    print(f"  Recall: {best_f1['recall']:.4f}")
    print(f"  Tahmin Edilen Gecikme Oranı: {best_f1['pred_rate']*100:.2f}%")
    
    # Gerçek orana en yakın eşik
    real_rate = y.mean()
    closest_to_real = min(results, key=lambda x: abs(x['pred_rate'] - real_rate))
    
    print(f"\n📊 Gerçek Orana En Yakın Eşik:")
    print(f"  Eşik: {closest_to_real['threshold']:.2f}")
    print(f"  Tahmin Edilen Oran: {closest_to_real['pred_rate']*100:.2f}%")
    print(f"  Gerçek Oran: {real_rate*100:.2f}%")
    print(f"  Fark: {abs(closest_to_real['pred_rate'] - real_rate)*100:.2f}%")
    
    return best_f1, closest_to_real

def main():
    """Ana fonksiyon."""
    print("=" * 60)
    print("GECİKME ORANI TEST SCRIPTİ")
    print("=" * 60)
    
    # Modeli yükle
    model, model_features = load_model()
    if model is None:
        return
    
    # Test verilerini hazırla
    X, y, real_delay_rate = prepare_test_data('Airlines.csv', sample_size=20000)
    
    # Model tahminlerini test et
    results = test_model_predictions(model, model_features, X, y, threshold=0.5)
    
    # Olasılık dağılımını analiz et
    analyze_probability_distribution(results['probabilities'], y)
    
    # Optimal eşik değerini bul
    best_f1, closest_to_real = find_optimal_threshold(results['probabilities'], y)
    
    # Özet
    print("\n" + "=" * 60)
    print("ÖZET")
    print("=" * 60)
    print(f"Gerçek Gecikme Oranı: {real_delay_rate*100:.2f}%")
    print(f"Tahmin Edilen Oran (Eşik=0.5): {results['threshold_05']*100:.2f}%")
    print(f"Fark: {abs(results['threshold_05'] - real_delay_rate)*100:.2f}%")
    
    if results['threshold_05'] > real_delay_rate * 1.1:
        print("\n⚠️  UYARI: Model gerçekten daha fazla gecikme tahmin ediyor!")
        print(f"   Önerilen eşik değeri: {closest_to_real['threshold']:.2f}")
    elif results['threshold_05'] < real_delay_rate * 0.9:
        print("\n⚠️  UYARI: Model gerçekten daha az gecikme tahmin ediyor!")
    else:
        print("\n✓ Model tahminleri gerçek orana yakın görünüyor.")

if __name__ == "__main__":
    main()
