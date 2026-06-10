import time
from datetime import datetime
import os
import pandas as pd
import requests

# --- BLYNK AYARLARI ---
BLYNK_AUTH_TOKEN = "jFtNYbPzaaca7qn9LqBEb6vV0WxhIxSK"
PIN_MESAFE = "V0"
PIN_GUVENLIK = "V1" 

URL_MESAFE = f"https://fra1.blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{PIN_MESAFE}"
URL_GUVENLIK = f"https://fra1.blynk.cloud/external/api/get?token={BLYNK_AUTH_TOKEN}&{PIN_GUVENLIK}"

CSV_FILE = "sensor_veri_log.csv"

# --- EŞİK DEĞERLERİ ---
ESIK_GECIS = 75.0       # 75 cm altı kesin insan geçişi: durum 1
ESIK_ARALIK = 110.0     # 75 - 110 cm arası kapı aralı bırakılmış: durum 2
ESIK_TAM_ACIK = 125.0   # 110 - 125 cm arası kapı tamamen açık: durum 3

def blynk_guvenlik_modu_oku():
    try:
        response = requests.get(URL_GUVENLIK, timeout=1.5)
        if response.status_code == 200:
            return response.text.strip() == "1"  # Güvenlik Aktif
        return False
    except Exception:
        return False

def blynk_mesafe_oku():
    try:
        response = requests.get(URL_MESAFE, timeout=1.5)
        if response.status_code == 200:
            return float(response.text.strip())
        return None
    except Exception:
        return None

def veriyi_csv_kaydet(zaman, mesafe, durum_kodu):
    yeni_veri = pd.DataFrame(
        [{"zaman": zaman, "mesafe": mesafe, "kapi_durumu": durum_kodu}]
    )
    if not os.path.isfile(CSV_FILE):
        yeni_veri.to_csv(CSV_FILE, index=False)
    else:
        yeni_veri.to_csv(CSV_FILE, mode="a", header=False, index=False)

print("=" * 60)
print("  Blynk Tabanlı IoT Telemetri ve Veri Toplama Sistemi Başlatıldı...")
print("=" * 60)

try:
    mevcut_durum = "SAKIN"  
    son_kaydedilen_dakika = -1
    evden_cikildi_mi = blynk_guvenlik_modu_oku()
    print(f"Sistem Aktif. Mod: {' YÜKSEK GÜVENLİK' if evden_cikildi_mi else ' EVDEYİSİNİZ (Sessiz Takip)'}\n")

    while True:
        mesafe = blynk_mesafe_oku()

        if mesafe is not None and mesafe > 0:
            su_an_dt = datetime.now()
            su_an_str = su_an_dt.strftime("%Y-%m-%d %H:%M:%S")
            mevcut_dakika = su_an_dt.minute

            # Dakika başında Blynk modunu kontrol et
            if mevcut_dakika != son_kaydedilen_dakika:
                evden_cikildi_mi = blynk_guvenlik_modu_oku()

            # --- EĞER V1 AKTİFSE ---
            if evden_cikildi_mi:
                if mesafe < ESIK_GECIS:
                    if mevcut_durum != "GECIS":
                        print(f"[{su_an_str}]  GÜVENLİK İHLALİ! İnsan Geçişi! Mesafe: {mesafe} cm")
                        veriyi_csv_kaydet(su_an_str, mesafe, 1)  # 1 = Kritik İhlal
                        mevcut_durum = "GECIS"
                elif mesafe < ESIK_ARALIK:
                    if mevcut_durum != "ARALIK":
                        print(f"[{su_an_str}]  KAPI ARALIK BIRAKILDI! Mesafe: {mesafe} cm")
                        veriyi_csv_kaydet(su_an_str, mesafe, 2)
                        mevcut_durum = "ARALIK"
                elif mesafe < ESIK_TAM_ACIK:
                    if mevcut_durum != "ACIK":
                        print(f"[{su_an_str}]  KAPI TAM AÇIK BIRAKILDI! Mesafe: {mesafe} cm")
                        veriyi_csv_kaydet(su_an_str, mesafe, 3)
                        mevcut_durum = "ACIK"
                else:
                    if mevcut_durum != "SAKIN":
                        mevcut_durum = "SAKIN"
                    
                    # Her saniye terminali kirletmemek için saniyede 1 okur, dakikada 1 kez SAKIN durumunu kaydeder
                    if mevcut_dakika != son_kaydedilen_dakika:
                        veriyi_csv_kaydet(su_an_str, mesafe, 0)
                        son_kaydedilen_dakika = mevcut_dakika
                        print(f"[{su_an_str}]  Sistem Stabil. Durum: Kapalı/Sakin | Mesafe: {mesafe} cm")

            # --- EĞER V1 PASİFSE (EVDEYSENİSİNİZ) ---
            else:
                mevcut_durum = "SAKIN"
                if mevcut_dakika != son_kaydedilen_dakika:
                    veriyi_csv_kaydet(su_an_str, mesafe, 0)
                    son_kaydedilen_dakika = mevcut_dakika
                    print(f"[{su_an_str}]  Ev Modu (Sessiz Veri Loglama)... Mesafe: {mesafe} cm")

        # Blynk sunucusunu darlamamak için ideal bekleme süresi
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\n Veri toplama başarıyla durduruldu.")