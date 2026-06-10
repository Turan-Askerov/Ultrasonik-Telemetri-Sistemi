import matplotlib
matplotlib.use('Agg')  # Linux Mint arayüz çakışmalarını önler

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print(" Zaman Serisi İleri Analiz ve Görselleştirme Başlatılıyor...")

if not os.path.isfile(CSV_FILE):
    print(f" Hata: '{CSV_FILE}' dosyası bulunamadı!")
    exit()

df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

print(f" Toplam analiz edilen veri satırı: {len(df)}")

# Sütun ismi kontrolü ve güvenceye alma
if 'kapi_durumu' not in df.columns and 'gecis_var_mi' in df.columns:
    df.rename(columns={'gecis_var_mi': 'kapi_durumu'}, inplace=True)

# =========================================================================
# GRAFİK 1: ANLIK MESAFA VE KAPI DURUM KATEGORİLERİ GRAFİĞİ
# =========================================================================
print(" 1. Grafik oluşturuluyor: Mesafe Akış ve Durum Sınıflandırması...")
plt.figure(figsize=(14, 6))

plt.plot(df['zaman'], df['mesafe'], color='#7f8c8d', alpha=0.4, label='Sensör Mesafesi (cm)', linewidth=1.5)

durumlar = {
    0: {"renk": "#27ae60", "etiket": "Kapı Kapalı (Sakin)", "marker": "o", "boyut": 15},
    1: {"renk": "#e74c3c", "etiket": "İNSAN GEÇİŞİ (İHLAL)", "marker": "X", "boyut": 80},
    2: {"renk": "#2980b9", "etiket": "Kapı Tam Açık", "marker": "^", "boyut": 40},
    3: {"renk": "#f39c12", "etiket": "Kapı Aralı Kalmış", "marker": "s", "boyut": 40}
}

for kod, ozellik in durumlar.items():
    alt_df = df[df['kapi_durumu'] == kod]
    if not alt_df.empty:
        plt.scatter(
            alt_df['zaman'], 
            alt_df['mesafe'], 
            color=ozellik['renk'], 
            label=ozellik['etiket'], 
            marker=ozellik['marker'], 
            s=ozellik['boyut'],
            zorder=4
        )

plt.gca().invert_yaxis()  # Hareketi yukarı yönlü göstermek için ters çevrim
plt.title('Blynk IoT Zaman Serisi Mesafe Akışı ve Durum Sınıflandırması', fontsize=13, fontweight='bold')
plt.xlabel('Zaman / Tarih', fontsize=11)
plt.ylabel('Sensör Mesafesi (cm) [Tavan = 0 cm]', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='gray')
plt.tick_params(axis='x', rotation=20)
plt.tight_layout()

plt.savefig('telemetri_mesafe_durum_analizi.png', dpi=300)
print(" -  Grafik kaydedildi: telemetri_mesafe_durum_analizi.png")

# =========================================================================
# GRAFİK 2: DAKİKA BAŞINA KULLANIM YOĞUNLUĞU GRAFİĞİ
# =========================================================================
print(" 2. Grafik oluşturuluyor: Dakikalık Geçiş Yoğunluğu...")
df_resample = df.copy()
df_resample.set_index('zaman', inplace=True)
df_resample['insan_gecisi'] = (df_resample['kapi_durumu'] == 1).astype(int)

zaman_araligi = "1min" 
yogunluk_df = df_resample["insan_gecisi"].resample(zaman_araligi).sum().fillna(0)

plt.figure(figsize=(12, 5))
plt.bar(
    yogunluk_df.index,
    yogunluk_df.to_numpy(),
    width=0.0005,
    color='#8e44ad',
    edgecolor='#9b59b6',
    label='Dakika Başına Toplam Geçiş'
)

plt.title('Zaman Serisi - Dakikalık Kapı Kullanım Yoğunluğu (İnsan Geçiş Sayıları)', fontsize=13, fontweight='bold')
plt.xlabel('Zaman', fontsize=11)
plt.ylabel('Algılanan İnsan Geçiş Sayısı', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.tick_params(axis='x', rotation=20)
plt.legend(loc='upper left')
plt.tight_layout()

plt.savefig('kapi_gecis_yogunluk_zamanserisi.png', dpi=300)
print(" -  Grafik kaydedildi: kapi_gecis_yogunluk_zamanserisi.png")

# =========================================================================
# GRAFİK 3: SON 24 SAATLİK GİRİŞ-ÇIKIŞ YOĞUNLUĞU (15 DK'LIK PENCERELER)
# =========================================================================
print(" 3. Grafik oluşturuluyor: 24 Saatlik Özet Yoğunluk Analizi...")
son_kayit_zamani = df_resample.index.max()
yirmi_dort_saat_oncesi = son_kayit_zamani - pd.Timedelta(hours=24)
son_24s_df = df_resample[df_resample.index >= yirmi_dort_saat_oncesi]

if son_24s_df.empty:
    print(" Rapor Notu: Veri setinde son 24 saate ait kayıt bulunmadığı için Grafik 3 genel veriye göre çiziliyor.")
    son_24s_df = df_resample

pencere_suresi = "15min"
son_24s_yogunluk = son_24s_df["insan_gecisi"].resample(pencere_suresi).sum().fillna(0)

plt.figure(figsize=(14, 5))
plt.bar(
    son_24s_yogunluk.index,
    son_24s_yogunluk.to_numpy(),
    width=0.005,
    color='#e67e22',
    edgecolor='#d35400',
    alpha=0.85,
    label='15 Dakikalık Periyottaki Geçiş Sayısı'
)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
plt.title('Zaman Serisi - Dönemsel Kapı Kullanım Yoğunluğu (15 Dakikalık Bloklar)', fontsize=13, fontweight='bold')
plt.xlabel('Zaman Akışı', fontsize=11)
plt.ylabel('Algılanan Toplam İnsan Geçişi', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.tick_params(axis='x', rotation=30)
plt.legend(loc='upper right')
plt.tight_layout()

plt.savefig('son_24saat_gecis_yogunlugu.png', dpi=300)
print(" -  Grafik kaydedildi: son_24saat_gecis_yogunlugu.png")
print("\n Tüm zaman serisi analiz grafikleri hazırlandı!")