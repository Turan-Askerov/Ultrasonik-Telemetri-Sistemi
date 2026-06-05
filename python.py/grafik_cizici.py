import matplotlib
matplotlib.use('Agg')  # Linux Mint arayüz çakışmasını engeller, arka planda çizer

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

# Sürüm uyarılarını tamamen gizle
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

# 1. Dosya Kontrolü
if not os.path.isfile(CSV_FILE):
    print(f"Hata: '{CSV_FILE}' bulunamadı. Lütfen klasörü kontrol edin!")
    exit()

# 2. Veriyi Yükleme ve Zaman Formatına Çevirme
df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

# 3. Akıllı Sütun Kontrolü (CSV'yi silmeden hem eskiyi hem yeniyi kurtarma)
if 'kapi_durumu' in df.columns:
    # Yeni kod formatı aktifse
    durum_sutunu = 'kapi_durumu'
    durum_haritasi = {
        0: 'Sakin / Kapalı',
        1: 'İnsan Geçişi',
        2: 'Kapı Tam Açık',
        3: 'Kapı Aralık'
    }
elif 'gecis_var_mi' in df.columns:
    # Eski kod formatı aktifse
    durum_sutunu = 'gecis_var_mi'
    durum_haritasi = {
        0: 'Sakin / Kapalı',
        1: 'İnsan Geçişi'
    }
else:
    print("Hata: CSV dosyasında 'kapi_durumu' veya 'gecis_var_mi' sütunlarından biri bulunamadı!")
    exit()

# Durum kodlarını metne dönüştür
df['durum_adi'] = df[durum_sutunu].map(durum_haritasi)

# Görsel tema ayarı
sns.set_theme(style="darkgrid")

# --- GRAFİK 1: Zaman İçinde Mesafe Değişimi (Çizgi Grafik) ---
plt.figure(figsize=(12, 5))
plt.plot(df['zaman'], df['mesafe'], color='royalblue', linewidth=1.5, label='Ölçülen Mesafe')

# Geçiş anlarını grafikte kırmızı noktalarla işaretle
gecisler = df[df[durum_sutunu] == 1]
if not gecisler.empty:
    plt.scatter(gecisler['zaman'], gecisler['mesafe'], color='crimson', zorder=5, label='İnsan Geçişi')

plt.title('Zamana Göre Ultrasonik Sensör Mesafe Değişimi (Telemetri Logu)', fontsize=14, fontweight='bold')
plt.xlabel('Zaman', fontsize=12)
plt.ylabel('Mesafe (cm)', fontsize=12)
plt.xticks(rotation=15)
plt.legend(loc='upper right')
plt.tight_layout()

