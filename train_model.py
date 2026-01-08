"""
ML Model Eğitim Scripti
Airlines.csv dataset'ini kullanarak uçuş gecikmesi tahmin modeli eğitir.
"""
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from app.feature_engineering import hash_airport_code
import numpy as np

def load_and_prepare_data(csv_path='Airlines.csv'):
    """Dataset'i yükle ve özellikler hazırla."""
    print("=" * 60)
    print("Dataset Yükleniyor...")
    print("=" * 60)
    
    # Dataset'i yükle
    df = pd.read_csv(csv_path)
    print(f"✓ Dataset yüklendi: {len(df)} satır, {len(df.columns)} kolon")
    
    # Temel istatistikler
    print(f"\nDataset İstatistikleri:")
    print(f"  - Toplam kayıt: {len(df)}")
    print(f"  - Gecikme var (Delay=1): {df['Delay'].sum()} ({df['Delay'].mean()*100:.2f}%)")
    print(f"  - Gecikme yok (Delay=0): {(df['Delay']==0).sum()} ({(df['Delay']==0).mean()*100:.2f}%)")
    
    # Özellik mühendisliği
    print("\n" + "=" * 60)
    print("Özellik Mühendisliği Yapılıyor...")
    print("=" * 60)
    
    # Hash bucket'ları ekle
    df['AirportFrom_Bucket'] = df['AirportFrom'].apply(
        lambda x: hash_airport_code(x, num_buckets=100)
    )
    df['AirportTo_Bucket'] = df['AirportTo'].apply(
        lambda x: hash_airport_code(x, num_buckets=100)
    )
    
    # Havayolu şirketini encode et (basit hash)
    df['Airline_Encoded'] = df['Airline'].apply(
        lambda x: hash_airport_code(x, num_buckets=50)
    )
    
    # Özellikleri seç
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
    
    print(f"✓ Özellikler hazırlandı: {len(features)} özellik")
    print(f"  Özellikler: {', '.join(features)}")
    
    return X, y, features

def train_model(X, y):
    """Model eğit."""
    print("\n" + "=" * 60)
    print("Model Eğitiliyor...")
    print("=" * 60)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  - Eğitim seti: {len(X_train)} örnek")
    print(f"  - Test seti: {len(X_test)} örnek")
    
    # Random Forest modeli
    print("\n  Random Forest modeli eğitiliyor...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Test seti üzerinde değerlendir
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Model eğitildi!")
    print(f"  - Test Accuracy: {accuracy*100:.2f}%")
    
    # Detaylı rapor
    print("\n" + "=" * 60)
    print("Model Performans Raporu")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=['Gecikme Yok', 'Gecikme Var']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"                Tahmin")
    print(f"              Yok  Var")
    print(f"Gerçek Yok   {cm[0][0]:4d} {cm[0][1]:4d}")
    print(f"      Var    {cm[1][0]:4d} {cm[1][1]:4d}")
    
    return model

def save_model(model, features, model_path='model.pkl', features_path='model_features.pkl'):
    """Modeli ve özellik listesini kaydet."""
    print("\n" + "=" * 60)
    print("Model Kaydediliyor...")
    print("=" * 60)
    
    # Model dizinini oluştur
    os.makedirs('models', exist_ok=True)
    
    model_full_path = os.path.join('models', model_path)
    features_full_path = os.path.join('models', features_path)
    
    # Modeli kaydet
    with open(model_full_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model kaydedildi: {model_full_path}")
    
    # Özellik listesini kaydet
    with open(features_full_path, 'wb') as f:
        pickle.dump(features, f)
    print(f"✓ Özellik listesi kaydedildi: {features_full_path}")
    
    return model_full_path, features_full_path

def main():
    """Ana fonksiyon."""
    try:
        # Dataset'i yükle ve hazırla
        X, y, features = load_and_prepare_data('Airlines.csv')
        
        # Modeli eğit
        model = train_model(X, y)
        
        # Modeli kaydet
        model_path, features_path = save_model(model, features)
        
        print("\n" + "=" * 60)
        print("✓ Model Eğitimi Tamamlandı!")
        print("=" * 60)
        print(f"\nModel dosyası: {model_path}")
        print(f"Özellik dosyası: {features_path}")
        print("\nModel API'de kullanıma hazır!")
        
    except FileNotFoundError:
        print("\n[HATA] Airlines.csv dosyası bulunamadı!")
        print("Lütfen dataset dosyasının proje klasöründe olduğundan emin olun.")
    except Exception as e:
        print(f"\n[HATA] Model eğitimi sırasında hata oluştu: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
