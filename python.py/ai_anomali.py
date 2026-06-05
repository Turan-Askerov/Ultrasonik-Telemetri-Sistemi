import matplotlib
matplotlib.use('Agg')  # Linux Mint arayüz çakışmasını engeller

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import os
import warnings

# Uyarıları gizle
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print("🤖 Yapay Zeka Tabanlı Anomali Tespit Modeli Yükleniyor...")

# Yol Kontrolü
if not os.path.isfile(CSV_FILE):
    if os.path.isfile("../" + CSV_FILE):
        CSV_FILE = "../" + CSV_FILE
    else:
        print(f" Hata: '{CSV_FILE}' bulunamadı!")
        exit()

# 1. Veriyi Yükleme
df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

# --- Akıllı Sütun Kontrolü (Hata Veren Kısmın Çözümü) ---
if 'kapi_durumu' in df.columns:
    durum_sutunu = 'kapi_durumu'
elif 'gecis_var_mi' in df.columns:
    durum_sutunu = 'gecis_var_mi'
else:
    print("Hata: CSV dosyasında geçerli veri sütunu bulunamadı!")
    exit()

# 2. Makine Öğrenmesi Modeli (Isolation Forest ile Anomali Tespiti)
# Mesafe ve durum verilerini kullanarak sistemdeki olağandışı hareketleri yakalar
X = df[['mesafe', durum_sutunu]]

# Modeli tanımlıyoruz (Kontaminasyon oranı %5: verilerin yaklaşık %5'ini sıra dışı kabul eder)
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# Tahmin yapılıyor: 1 = Normal Veri, -1 = Anomali (Sıra dışı durum)
df['anomali_skoru'] = model.predict(X)

# Anomalileri filtreleyelim
anomaliler = df[df['anomali_skoru'] == -1]

print(f"\n--- Analiz Tamamlandı ---")
print(f"Toplam Veri Noktası: {len(df)}")
print(f"Yapay Zeka Tarafından Yakalanan Anomali Sayısı: {len(anomaliler)}")

if len(anomaliler) > 0:
    print("\n--- Yakalanan İlk 5 Kritik Anomali Örneği ---")
    print(anomaliler[['zaman', 'mesafe', durum_sutunu]].head())

# 3. Yapay Zeka Anomali Grafiğini Çizdirme
plt.figure(figsize=(12, 5))
plt.plot(df['zaman'], df['mesafe'], color='gray', alpha=0.6, label='Normal Mesafe Akışı')

# Anomalileri grafikte parlak kırmızı yıldızlarla işaretleyelim (Hoca buna bayılır!)
if not anomaliler.empty:
    plt.scatter(anomaliler['zaman'], anomaliler['mesafe'], color='crimson', marker='X', s=80, zorder=5, label='AI Tarafından Saptanan Anomali')

plt.title('Yapay Zeka (Isolation Forest) Destekli Anomali ve Tehdit Algılama Grafiği', fontsize=12, fontweight='bold')
plt.xlabel('Zaman')
plt.ylabel('Mesafe (cm)')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Grafiği kaydet
plt.savefig('ai_anomali_tespit_grafigi.png', dpi=300)
print("\n🤖 1. Grafik başarıyla kaydedildi: ai_anomali_tespit_grafigi.png")
print("[BAŞARILI] Yapay zeka motoru sorunsuz çalıştı.")