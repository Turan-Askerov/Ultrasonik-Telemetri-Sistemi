import matplotlib
matplotlib.use('Agg') 
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings

# Sürüm ve matplotlib uyarılarını terminali kirletmesin diye gizle
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print(" CSV Verisi yükleniyor...")

# Yol Kontrolü (Alt klasör karmaşasını çözmek için)
if not os.path.isfile(CSV_FILE):
    if os.path.isfile("../" + CSV_FILE):
        CSV_FILE = "../" + CSV_FILE
    else:
        print(f" Hata: '{CSV_FILE}' dosyası bulunamadı. Lütfen önce biraz veri toplayın!")
        exit()

# 1. Veriyi Yükleme
df = pd.read_csv(CSV_FILE)

# 'zaman' sütununu gerçek bir Tarih-Saat (Datetime) nesnesine çeviriyoruz
if 'zaman' in df.columns:
    df['zaman'] = pd.to_datetime(df['zaman'])
    df.set_index('zaman', inplace=True)  # Zaman serisi analizi için indekse alıyoruz
elif df.index.name != 'zaman':
    df.index = pd.to_datetime(df.index)

print("\n--- İlk Ham Veriler (İlk 5 Satır) ---")
print(df.head())

# --- Akıllı Sütun Kontrolü (CSV silinmediyse hem eskiyi hem yeniyi kurtarma) ---
if 'kapi_durumu' in df.columns:
    # Yeni kod yapısında sadece gerçek geçişleri (1) filtreleyip sayıyoruz
    df['gecis_filtresi'] = (df['kapi_durumu'] == 1).astype(int)
elif 'gecis_var_mi' in df.columns:
    # Eski kod yapısı aktifse doğrudan sütunu alıyoruz
    df['gecis_filtresi'] = df['gecis_var_mi']
else:
    print("Hata: CSV dosyasında 'kapi_durumu' veya 'gecis_var_mi' sütunu bulunamadı!")
    exit()

# 2. Zaman Serisi Yeniden Örneklendirme (Resampling)
# '5min' -> 5 Dakikalık pencereler demektir. İstersen '1min' (1 Dakika) yapabilirsin.
zaman_araligi = "5min"  
yoğunluk_df = df["gecis_filtresi"].resample(zaman_araligi).sum().fillna(0)

print(f"\n--- {zaman_araligi} Sıklığa Göre Gruplanmış Giriş-Çıkış Sayıları ---")
print(yoğunluk_df[yoğunluk_df > 0].head(10))  # Sadece hareket olan pencerelerden kesit göster

# 3. Grafik Çizdirme ve Kaydetme
print("\n Zaman serisi yoğunluk grafiği oluşturuluyor...")
plt.figure(figsize=(10, 5))
plt.plot(
    yoğunluk_df.index,
    yoğunluk_df.to_numpy(),  
    marker="o",
    linestyle="-",
    color="b",
    linewidth=1.5
)
plt.title(f"Zaman Serisi - {zaman_araligi} Aralıklı Kapı Yoğunluğu Analizi", fontsize=12, fontweight='bold')
plt.xlabel("Zaman", fontsize=10)
plt.ylabel("Toplam Geçiş Sayısı", fontsize=10)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(rotation=30)
plt.tight_layout()

# Grafik çıktısını klasöre kaydet (Raporuna doğrudan ekleyebilirsin)
plt.savefig('kapi_gecis_yogunluk_zamanserisi.png', dpi=300)
print(" Grafik başarıyla kaydedildi: kapi_gecis_yogunluk_zamanserisi.png")
print("\n[BAŞARILI] Analiz ve grafik üretimi tamamlandı.")