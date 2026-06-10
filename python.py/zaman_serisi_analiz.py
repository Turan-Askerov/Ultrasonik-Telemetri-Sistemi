import matplotlib
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

CSV_FILE = "sensor_veri_log.csv"

print(" Analiz Grafikleri Başlatılıyor...")

if not os.path.isfile(CSV_FILE):
    print(f" Hata: '{CSV_FILE}' dosyası bulunamadı!")
    exit()

df = pd.read_csv(CSV_FILE)
df['zaman'] = pd.to_datetime(df['zaman'])

# Durum etiketleri için isimlendirme
durum_isimleri = {
    0: "Kapı Kapalı (Sakin)",
    1: "İnsan Geçişi (İhlal)",
    2: "Kapı Tam Açık",
    3: "Kapı Aralı Kalmış"
}
df['durum_adi'] = df['kapi_durumu'].map(durum_isimleri)

# =========================================================================
# GRAFİK 1: ANA TELEMETRİ GRAFİĞİ - MESAFE AKIŞI VE DURUM SINIFLANDIRMASI
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

plt.gca().invert_yaxis()
plt.title('Blynk IoT Zaman Serisi Mesafe Akışı ve Durum Sınıflandırması', fontsize=13, fontweight='bold')
plt.xlabel('Zaman / Tarih', fontsize=11)
plt.ylabel('Sensör Mesafesi (cm) [Tavan = 0 cm]', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='gray')
plt.tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig('telemetri_mesafe_durum_analizi.png', dpi=300)
print(" -  Grafik başarıyla güncellendi: telemetri_mesafe_durum_analizi.png")

# =========================================================================
# YENİ GRAFİK 2: KAPI DURUMLARININ DAĞILIMI (PASTA GRAFİĞİ)
# =========================================================================
print(" 2. Grafik oluşturuluyor: Kapı Durum Dağılımı (Pasta Grafiği)...")
plt.figure(figsize=(8, 6))

durum_sayilari = df['durum_adi'].value_counts()
renkler = ['#27ae60', '#e74c3c', '#2980b9', '#f39c12']
aktif_renkler = [renkler[list(durum_isimleri.values()).index(idx)] for idx in durum_sayilari.index]

plt.pie(
    durum_sayilari.to_numpy(), 
    labels=durum_sayilari.index.to_list(), 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=aktif_renkler,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2, 'antialiased': True}
)
plt.title('Tüm Zaman Serisi Boyunca Kapı Durumlarının Oransal Dağılımı', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('kapi_durum_pasta_grafigi.png', dpi=300)
print(" - Grafik başarıyla kaydedildi: kapi_durum_pasta_grafigi.png")


print("\n Grafikler hazırlandı !")