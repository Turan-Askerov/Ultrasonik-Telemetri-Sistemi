import matplotlib
matplotlib.use('Agg')  # Linux Mint arayüz çakışmalarını önler

import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # Modülü doğrudan çağırarak hatayı engelliyoruz
import pandas as pd
import os
import warnings

# Terminal temiz kalsın diye gereksiz uyarıları gizle
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print("📊 Gelişmiş Zaman Serisi Veri Analizi Başlatılıyor...")

# Yol Kontrolü (Alt klasör karmaşasını çözmek için)
if not os.path.isfile(CSV_FILE):
    if os.path.isfile("../" + CSV_FILE):
        CSV_FILE = "../" + CSV_FILE
    else:
        print(f"❌ Hata: '{CSV_FILE}' dosyası bulunamadı. Lütfen önce yerel sunucuyu çalıştırıp veri toplayın!")
        exit()

# 1. Veriyi Yükleme ve Zaman Serisi Hazırlığı
df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

print(f"📂 Toplam loglanan veri satırı: {len(df)}")

# Sütun ismi kontrolü (Yeni sunucu kodu kapi_durumu kullanıyor)
if 'kapi_durumu' not in df.columns:
    if 'gecis_var_mi' in df.columns:
        df.rename(columns={'gecis_var_mi': 'kapi_durumu'}, inplace=True)
    else:
        print("❌ Hata: CSV dosyasında durum sütunu bulunamadı!")
        exit()

# =========================================================================
# GRAFİK 1: ANLIK MESAFA VE KAPI DURUM KATEGORİLERİ GRAFİĞİ (AŞAĞIDAN YUKARI)
# =========================================================================
print("📈 1. Grafik oluşturuluyor: Aşağıdan Yukarıya Doğru Mesafe Analizi...")
plt.figure(figsize=(14, 6))

# Ana mesafe çizgisi
plt.plot(df['zaman'], df['mesafe'], color='#7f8c8d', alpha=0.4, label='Sensör Mesafesi (cm)', linewidth=1.5)

# Durumlara göre verileri filtreleyip grafiğe özel renklerle basıyoruz
durumlar = {
    0: {"renk": "#27ae60", "etiket": "Kapı Kapalı (Sakin)", "marker": "o", "boyut": 15},
    1: {"renk": "#e74c3c", "etiket": "İNSAN GEÇİŞİ (ANOMALİ)", "marker": "X", "boyut": 80},
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

# Y eksenini ters çevirerek hareket anında grafiğin yukarı fırlamasını sağlıyoruz
plt.gca().invert_yaxis()

plt.title('Zaman Serisi Mesafe Akışı ve Yapay Zeka Kapı Durum Sınıflandırması (Aşağıdan Yukarı Perspektif)', fontsize=13, fontweight='bold')
plt.xlabel('Zaman / Tarih', fontsize=11)
plt.ylabel('Sensör Mesafesi (cm) [Üst Tavan = 0 cm]', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='gray')
plt.tick_params(axis='x', rotation=20)
plt.tight_layout()

# İlk grafiği kaydet
plt.savefig('telemetri_mesafe_durum_analizi.png', dpi=300)
print("✅ 1. Grafik kaydedildi: telemetri_mesafe_durum_analizi.png")

# =========================================================================
# GRAFİK 2: ZAMAN ARALIKLI GEÇİŞ YOĞUNLUĞU GRAFİĞİ (Resampling)
# =========================================================================
print("📉 2. Grafik oluşturuluyor: Zaman Aralıklı Geçiş Yoğunluğu...")

# Zaman serisi gruplaması için zamanı indekse alıyoruz
df_resample = df.copy()
df_resample.set_index('zaman', inplace=True)

# Sadece insan geçişlerini (Sınıf 1) filtreleyip sayalım
df_resample['insan_gecisi'] = (df_resample['kapi_durumu'] == 1).astype(int)

# Saniyede 1 veri aktığı için 1 dakikalık (1min) pencereler
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

plt.title(f'Zaman Serisi - {zaman_araligi} Aralıklı Kapı Kullanım Yoğunluğu (İnsan Geçiş Sayıları)', fontsize=13, fontweight='bold')
plt.xlabel('Zaman', fontsize=11)
plt.ylabel('Algılanan İnsan Geçiş Sayısı', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.4, axis='y')
plt.tick_params(axis='x', rotation=20)
plt.legend(loc='upper left')
plt.tight_layout()

# İkinci grafiği kaydet
plt.savefig('kapi_gecis_yogunluk_zamanserisi.png', dpi=300)
print("✅ 2. Grafik kaydedildi: kapi_gecis_yogunluk_zamanserisi.png")

# =========================================================================
# GRAFİK 3: SON 24 SAATLİK GİRİŞ-ÇIKIŞ YOĞUNLUĞU (15 DK'LIK PENCERELER)
# =========================================================================
print("\n📊 3. Grafik oluşturuluyor: Son 24 Saatlik Detaylı Yoğunluk Analizi...")

son_kayit_zamani = df_resample.index.max()
yirmi_dort_saat_oncesi = son_kayit_zamani - pd.Timedelta(hours=24)

# Veriyi son 24 saate göre filtrele
son_24s_df = df_resample[df_resample.index >= yirmi_dort_saat_oncesi]

if son_24s_df.empty:
    print("⚠️ Uyarı: Veri setinde son 24 saate ait kayıt bulunamadı! Grafik 3 atlanıyor.")
else:
    pencere_suresi = "15min"
    son_24s_yogunluk = son_24s_df["insan_gecisi"].resample(pencere_suresi).sum().fillna(0)

    plt.figure(figsize=(14, 5))
    
    plt.bar(
        son_24s_yogunluk.index,
        son_24s_yogunluk.to_numpy(),
        width=0.008,
        color='#e67e22',
        edgecolor='#d35400',
        alpha=0.85,
        label='15 Dakikalık Periyottaki Geçiş Sayısı'
    )

    # Kırmızı çizgiye sebep olan yer düzeltildi: matplotlib.dates yerine mdates kullanıldı
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
    
    plt.title(f'Son 24 Saatlik Detaylı Kapı Kullanım Yoğunluğu ({pencere_suresi} Periyotlu)', fontsize=13, fontweight='bold')
    plt.xlabel(f'Zaman Akışı (Son Kayıt: {son_kayit_zamani.strftime("%d-%m %H:%M")})', fontsize=11)
    plt.ylabel('Algılanan Toplam İnsan Geçişi', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.4, axis='y')
    plt.tick_params(axis='x', rotation=30)
    plt.legend(loc='upper right')
    plt.tight_layout()

    # Üçüncü grafiği kaydet
    plt.savefig('son_24saat_gecis_yogunlugu.png', dpi=300)
    print("✅ 3. Grafik başarıyla kaydedildi: son_24saat_gecis_yogunlugu.png")

print("\n🚀 [MÜKEMMEL] Tüm veri analiz süreçleri ve görselleştirmeler sıfır hatayla tamamlandı!")