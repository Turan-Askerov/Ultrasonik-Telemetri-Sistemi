import matplotlib
matplotlib.use('Agg')  # Linux Mint grafik arayüz çakışmalarını önler

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import os
import warnings

# Gereksiz kütüphane uyarılarını gizle
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print("🤖 Yapay Zeka Tabanlı Anomali Tespit Modeli Başlatılıyor...")

# Dosya Mevcutluk Kontrolü
if not os.path.isfile(CSV_FILE):
    print(f"❌ Hata: '{CSV_FILE}' bulunamadı! Lütfen önce yerel sunucuya veri akışı sağlayın.")
    exit()

# 1. CSV Verisini Pandas ile Yükleme
df = pd.read_csv(CSV_FILE)

if len(df) < 10:
    print("⚠️ Uyarı: Yapay zeka analizi için CSV dosyasında çok az veri var (En az 10 satır önerilir).")
    print("Mevcut veri üzerinden analiz deneniyor...")

df['zaman'] = pd.to_datetime(df['zaman'])

# 2. Yapay Zeka Modeli (Isolation Forest) Entegrasyonu
# Mesafe değerlerini ve kapının durum kodlarını analiz eder
X = df[['mesafe', 'kapi_durumu']]

# Kontaminasyon %5 (Verilerin %5'ini sıra dışı/anomali kabul eder)
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# 1 = Normal Durum, -1 = Yapay Zeka Tarafından Saptanan Anomali
df['anomali_skoru'] = model.predict(X)
anomaliler = df[df['anomali_skoru'] == -1]

print(f"\n📊 --- ML Analiz Sonuçları ---")
print(f"Loglanan Toplam Örnek Sayısı: {len(df)}")
print(f"Tehdit/Anomali Olarak Sınıflandırılan Durum Sayısı: {len(anomaliler)}")

if not anomaliler.empty:
    print("\n🚨 [KRİTİK] Yakalanan Bazı Anomali Örnekleri:")
    print(anomaliler[['zaman', 'mesafe', 'kapi_durumu']].head())

# 3. Grafik Çizimi ve Kaydetme
plt.figure(figsize=(12, 5))
plt.plot(df['zaman'], df['mesafe'], color='royalblue', alpha=0.5, label='Normal Mesafe Takibi', linewidth=1.5)

# Yapay zekanın yakaladığı anomali noktalarını grafikte kırmızı 'X' ile işaretle
if not anomaliler.empty:
    plt.scatter(anomaliler['zaman'], anomaliler['mesafe'], color='crimson', marker='X', s=100, zorder=5, label='AI Anomali Tehdit Tespiti')

plt.title('Geliştirilen Yerel Sunucu Sisteminde Yapay Zeka Destekli Tehdit/Anomali Analizi', fontsize=12, fontweight='bold')
plt.xlabel('Zaman Damgasi')
plt.ylabel('Sensör Mesafesi (cm)')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Grafiği kaydet
plt.savefig('ai_anomali_tespit_grafigi.png', dpi=300)
print("\n📈 Grafik başarıyla oluşturuldu ve kaydedildi: 'ai_anomali_tespit_grafigi.png'")
print("[BAŞARILI] İşlem tamamlandı.")