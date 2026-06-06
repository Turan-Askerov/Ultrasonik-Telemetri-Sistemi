import matplotlib
matplotlib.use('Agg')  # Linux Mint arayüz çakışmalarını önler

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import datetime
import os

app = Flask(__name__)
CSV_FILE = "sensor_veri_log.csv"

# Global Hafıza Modeli
sistem_durumu = {
    "guvenlik_modu": 0,  # 0: Evdeyim, 1: Dışarıdayım
    "son_mesafe": 0.0,
    "son_sinif": 0,
    "son_zaman": "Veri bekleniyor..."
}

if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["zaman", "mesafe", "guvenlik_modu", "kapi_durumu"])
    df_init.to_csv(CSV_FILE, index=False)

def durum_siniflandir(mesafe):
    if mesafe >= 125: return 0  # Kapalı
    elif mesafe < 75: return 1  # İnsan Geçişi
    elif 110 <= mesafe < 125: return 2  # Tam Açık
    elif 75 <= mesafe < 110: return 3  # Aralık
    return 0

# =========================================================================
# WEB ARAYÜZÜ (HTML + CSS + JAVASCRIPT) - DASHBOARD
# =========================================================================
WEB_ARAYUZU = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IoT Ultrasonik Telemetri Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a24; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 800px; width: 100%; }
        h1 { text-align: center; color: #3498db; margin-bottom: 30px; font-weight: 600; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #242533; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center; border-bottom: 4px solid #3498db; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); }
        .card h3 { margin: 0 0 10px 0; font-size: 14px; color: #bbb; text-transform: uppercase; letter-spacing: 1px; }
        .card .value { font-size: 28px; font-weight: bold; margin-top: 5px; }
        
        /* Dinamik Durum Renkleri */
        .durum-0 { border-color: #27ae60; color: #27ae60; } /* Kapalı */
        .durum-1 { border-color: #e74c3c; color: #e74c3c; animation: pulse 1s infinite; } /* Geçiş */
        .durum-2 { border-color: #2980b9; color: #2980b9; } /* Açık */
        .durum-3 { border-color: #f39c12; color: #f39c12; } /* Aralık */
        
        .btn-group { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; }
        button { padding: 12px 24px; font-size: 15px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
        .btn-ev { background-color: #2ecc71; color: white; }
        .btn-disari { background-color: #e74c3c; color: white; }
        button:hover { opacity: 0.9; transform: scale(1.05); }
        .active-mod { box-shadow: 0 0 15px currentColor; border: 2px solid #fff; }
        .footer { text-align: center; font-size: 12px; color: #666; margin-top: 20px; }
        
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class="container">
        <h1> Ultrasonik Telemetri Sistemi Canlı Takip Paneli</h1>
        
        <div class="btn-group">
            <button id="btnMod0" class="btn-ev" onclick="modDegistir(0)">🏠 EVDEYİM (Sessiz)</button>
            <button id="btnMod1" class="btn-disari" onclick="modDegistir(1)">🚨 DIŞARIDAYIM (Alarm)</button>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Son Mesafe</h3>
                <div id="txtMesafe" class="value">0.0 cm</div>
            </div>
            <div id="cardDurum" class="card durum-0">
                <h3>Kapı Durumu</h3>
                <div id="txtDurum" class="value">Veri Bekleniyor</div>
            </div>
            <div class="card">
                <h3>Son Güncelleme</h3>
                <div id="txtZaman" class="value" style="font-size: 16px; margin-top:15px;">-</div>
            </div>
        </div>
        
        <div class="footer">Kocaeli Üniversitesi - Bilgi Sistemleri Mühendisliği © 2026</div>
    </div>

    <script>
        // Sayfa yenilenmeden her 800 milisaniyede bir Python'dan güncel verileri çeken fonksiyon
        async function canliVeriYenile() {
            try {
                let response = await fetch('/anlik_durum_api');
                let data = await response.json();
                
                // Değerleri bas
                document.getElementById('txtMesafe').innerText = data.son_mesafe.toFixed(1) + " cm";
                document.getElementById('txtZaman').innerText = data.son_zaman;
                
                // Durum kartını ve metnini güncelle
                let cardDurum = document.getElementById('cardDurum');
                let txtDurum = document.getElementById('txtDurum');
                cardDurum.className = "card durum-" + data.son_sinif;
                
                let durumMetinleri = ["Kapı Kapalı", "İNSAN GEÇİŞİ 🚨", "Kapı Tam Açık", "Kapı Aralık ⚠️"];
                txtDurum.innerText = durumMetinleri[data.son_sinif];
                
                // Aktif buton görselini güncelle
                if(data.guvenlik_modu == 1) {
                    document.getElementById('btnMod1').classList.add('active-mod');
                    document.getElementById('btnMod0').classList.remove('active-mod');
                } else {
                    document.getElementById('btnMod0').classList.add('active-mod');
                    document.getElementById('btnMod1').classList.remove('active-mod');
                }
            } catch (err) {
                console.log("Veri çekme hatası:", err);
            }
        }

        async function modDegistir(yeniMod) {
            await fetch('/mod_degistir?mod=' + yeniMod);
            canliVeriYenile();
        }

        // İlk açılışta çalıştır ve her 800ms'de bir tekrarla (Saniyede 1 gelen veriyi yakalamak için)
        canliVeriYenile();
        setInterval(canliVeriYenile, 800);
    </script>
</body>
</html>
"""

# =========================================================================
# FLASK TÜNELLERİ (ROUTES)
# =========================================================================

@app.route('/')
def ana_sayfa():
    """ Tarayıcıdan girildiğinde şık paneli gösterir """
    return render_template_string(WEB_ARAYUZU)

@app.route('/anlik_durum_api', methods=['GET'])
def anlik_durum_api():
    """ Web arayüzünün arka planda çaktırmadan veri çekeceği tünel """
    return jsonify(sistem_durumu)

@app.route('/veri_yukle', methods=['POST'])
def veri_yukle():
    try:
        data = request.get_json()
        if not data or 'mesafe' not in data:
            return jsonify({"status": "hata", "mesaj": "Eksik parametre"}), 400
        
        mesafe = float(data['mesafe'])
        zaman_damgasi = datetime.datetime.now().strftime('%H:%M:%S')
        
        sinif_kodu = durum_siniflandir(mesafe)
        mod_bilgisi = sistem_durumu["guvenlik_modu"]
        
        # Canlı izleme arayüzü için RAM hafızasını güncelle
        sistem_durumu["son_mesafe"] = mesafe
        sistem_durumu["son_sinif"] = sinif_kodu
        sistem_durumu["son_zaman"] = zaman_damgasi
        
        # Terminal Bildirimleri
        if mod_bilgisi == 1 and sinif_kodu == 1:
            print(f"🚨 [ALARM] {zaman_damgasi} - İNSAN GEÇİŞİ! {mesafe} cm")
        elif mod_bilgisi == 0 and sinif_kodu == 1:
            print(f"🤫 [SESSİZ LOG] İnsan geçti. {mesafe} cm")

        # CSV Kaydı (Append moduyla hafif kayıt)
        zaman_tam = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yeni_satir = pd.DataFrame([[zaman_tam, mesafe, mod_bilgisi, sinif_kodu]])
        yeni_satir.to_csv(CSV_FILE, mode='a', header=False, index=False)
        
        return jsonify({"status": "basarili", "guvenlik_modu": mod_bilgisi}), 200
    except Exception as e:
        return jsonify({"status": "hata", "mesaj": str(e)}), 500

@app.route('/mod_degistir', methods=['GET'])
def mod_degistir():
    yeni_mod = request.args.get('mod', type=int)
    if yeni_mod in [0, 1]:
        sistem_durumu["guvenlik_modu"] = yeni_mod
        return jsonify({"status": "basarili", "guncel_mod": yeni_mod}), 200
    return jsonify({"status": "hata", "mesaj": "Geçersiz mod"}), 400

if __name__ == '__main__':
    print("\n==============================================")
    print("🚀 Canlı Dashboard'lu IoT Sunucusu Başlatıldı")
    print("👉 Tarayıcıdan şuraya gir: http://127.0.0.1:5000")
    print("==============================================\n")
    app.run(host='0.0.0.0', port=5000, debug=False)