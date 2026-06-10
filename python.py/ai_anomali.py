import matplotlib
matplotlib.use('Agg') 

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print("Yapay Zeka Anomali Tespit Modeli Başlatılıyor...")

if not os.path.isfile(CSV_FILE):
    print(f" Hata: '{CSV_FILE}' bulunamadı! Lütfen önce veri toplayıcıyı çalıştırın.")
    exit()

df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

# 1. Aşama: Gelişmiş Isolation Forest (Yapay Zeka Kararı)
X = df[['mesafe', 'kapi_durumu']]
model = IsolationForest(contamination=0.04, random_state=42)
model.fit(X)
df['ai_skoru'] = model.predict(X)

# 2. Aşama: Uzman Sistem 
# Yapay zekanın geometrik olarak şaşırdığı yerleri, gerçek kritik geçiş kurallarıyla (Mesafe < 75 ve kapi_durumu == 1) eğitiyoruz
# Böylece ortadaki kararsız geçiş çizgileri yerine tam uç tepe noktaları hedeflenir.
df['gercek_anomali'] = (df['ai_skoru'] == -1) & (df['kapi_durumu'] == 1) | (df['mesafe'] < 75.0)

anomaliler = df[df['gercek_anomali'] == True]

print(f"\n --- ML Analiz Sonuçları ---")
print(f"Loglanan Toplam Örnek Sayısı: {len(df)}")
print(f"Sistem Tarafından Onaylanan Gerçek Tehdit/Anomali Sayısı: {len(anomaliler)}")

if not anomaliler.empty:
    print("\n Tam Uç Noktalarda Yakalanan Bazı Tehdit Örnekleri:")
    print(anomaliler[['zaman', 'mesafe', 'kapi_durumu']].head())

# Grafik Oluşturma
plt.figure(figsize=(12, 5))
plt.plot(df['zaman'], df['mesafe'], color='#34495e', alpha=0.35, label='Normal Telemetri Takibi', linewidth=1.5)

if not anomaliler.empty:
    plt.scatter(
        anomaliler['zaman'], 
        anomaliler['mesafe'], 
        color='#e74c3c', 
        marker='X', 
        s=120, 
        zorder=5, 
        label='AI Saptanan Kritik Tehdit (Uç Nokta Tespiti)'
    )

plt.title(' Yapay Zeka Destekli Hassas Tehdit/Anomali Analizi', fontsize=12, fontweight='bold')
plt.xlabel('Zaman Damgası')
plt.ylabel('Sensör Mesafesi (cm)')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig('ai_anomali_tespit_grafigi.png', dpi=300)
print("\n Grafik kaydedildi: 'ai_anomali_tespit_grafigi.png'")