"""
Diyabet Risk Tahmin Modeli - Eğitim Scripti
BRFSS 2015 veri seti kullanılarak Random Forest modeli eğitilir.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import pickle
import os

print("=" * 60)
print("  Diyabet Risk Tahmin Modeli Eğitimi Başlıyor...")
print("=" * 60)

# Veri yükleme
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "archive", "diabetes_binary_health_indicators_BRFSS2015.csv")
print(f"\n[1/5] Veri yükleniyor: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"      Veri boyutu: {df.shape[0]:,} satır, {df.shape[1]} sütun")

# Özellikler ve hedef değişken
# Kaldırılanlar: AnyHealthcare, NoDocbcCost, Education, Income
# (diyabetle dolaylı ilişkili, sosyoekonomik göstergeler)
FEATURES = [
    'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
    'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
    'HvyAlcoholConsump', 'GenHlth', 'MentHlth', 'PhysHlth',
    'DiffWalk', 'Sex', 'Age'
]
TARGET = 'Diabetes_binary'

X = df[FEATURES]
y = df[TARGET]

print(f"\n[2/5] Veri bölünüyor (80% eğitim, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"      Eğitim seti: {X_train.shape[0]:,} örnek")
print(f"      Test seti  : {X_test.shape[0]:,} örnek")

# Ölçeklendirme
print(f"\n[3/5] Veriler ölçeklendiriliyor...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model eğitimi
print(f"\n[4/5] Random Forest modeli eğitiliyor (bu biraz sürebilir)...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
model.fit(X_train_scaled, y_train)
print("      Model eğitimi tamamlandı!")

# Değerlendirme
print(f"\n[5/5] Model değerlendiriliyor...")
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

print(f"\n{'='*60}")
print(f"  MODEL PERFORMANSI")
print(f"{'='*60}")
print(f"  Doğruluk (Accuracy): {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  AUC-ROC Skoru     : {auc:.4f}")
print(f"\n  Sınıflandırma Raporu:")
print(classification_report(y_test, y_pred, target_names=['Diyabet Yok', 'Diyabet Var']))

# Özellik önem sıralaması
feature_importance = pd.DataFrame({
    'Özellik': FEATURES,
    'Önem': model.feature_importances_
}).sort_values('Önem', ascending=False)

print(f"\n  En Önemli 10 Özellik:")
for i, row in feature_importance.head(10).iterrows():
    print(f"    {row['Özellik']:25s}: {row['Önem']:.4f}")

# Model ve scaler kaydetme
save_dir = os.path.dirname(__file__)
model_path = os.path.join(save_dir, "diabetes_model.pkl")
scaler_path = os.path.join(save_dir, "diabetes_scaler.pkl")
features_path = os.path.join(save_dir, "diabetes_features.pkl")

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)

with open(features_path, 'wb') as f:
    pickle.dump({
        'features': FEATURES,
        'accuracy': accuracy,
        'auc': auc,
        'feature_importance': feature_importance.to_dict('records')
    }, f)

print(f"\n{'='*60}")
print(f"  Dosyalar kaydedildi:")
print(f"    - diabetes_model.pkl")
print(f"    - diabetes_scaler.pkl")
print(f"    - diabetes_features.pkl")
print(f"{'='*60}")
print(f"\n  Model eğitimi başarıyla tamamlandı!")
print(f"  Şimdi 'diabetes_app.py' dosyasını çalıştırabilirsiniz.")
print(f"{'='*60}\n")
