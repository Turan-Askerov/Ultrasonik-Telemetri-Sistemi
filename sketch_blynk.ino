#include <ESP8266WiFi.h>       
#include <ESP8266HTTPClient.h> 
#include <WiFiClient.h>

// --- Kablosuz Ağ Ayarları ---
const char *ssid = "Electromagnetic Field";    
const char *password = "P3R3VFRFMFYJ"; 

// --- Python Flask Sunucu Ayarları ---
// Az önce bulduğumuz yerel IP adresini ve Flask portunu buraya tam olarak gömdük
const char *serverUrl = "http://192.168.1.89:5000/veri_yukle";

// --- Sensör Pin Tanımlamaları ---
const int trigPin = D1; // Kendi breadboard bağlantına göre pinleri kontrol et
const int echoPin = D2;

void setup()
{
  Serial.begin(115200);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Wi-Fi Bağlantı Süreci
  WiFi.begin(ssid, password);
  Serial.print(" Yerel Ağ sunucusuna bağlanılıyor...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n Bağlantı kuruldu!");
  Serial.print("Kartın Yerel IP Adresi: ");
  Serial.println(WiFi.localIP());
}

void loop()
{
  // 1. Ultrasonik Sensör ile Mesafe Ölçümü (Mikrosaniyeler içinde donanımsal ölçüm)
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.0343 / 2; // Sesi hızına göre cm cinsinden hesaplama

  // Hatalı/Gürültülü okumaları (0 veya çok uçuk değerleri) filtrele
  if (distance > 0 && distance < 400)
  {
    Serial.print(" Ölçülen Mesafe: ");
    Serial.print(distance);
    Serial.println(" cm");

    // 2. Wi-Fi üzerinden Bilgisayardaki Flask Sunucusuna Veri Gönderme
    if (WiFi.status() == WL_CONNECTED)
    {
      WiFiClient client;
      HTTPClient http;

      http.begin(client, serverUrl);
      http.addHeader("Content-Type", "application/json");

      // JSON formatında veriyi hazırlıyoruz
      String jsonPayload = "{\"mesafe\":" + String(distance) + "}";

      // Veriyi yerel sunucuya fırlatıyoruz (Milisaniyeler içinde ulaşır)
      int httpResponseCode = http.POST(jsonPayload);

      if (httpResponseCode > 0)
      {
        String response = http.getString();
        Serial.print(" Sunucu Yanıtı: ");
        Serial.println(response); // Sunucudan gelen başarı mesajı ve mod bilgisi
      }
      else
      {
        Serial.print(" Sunucuya gönderim hatası, Kod: ");
        Serial.println(httpResponseCode);
      }
      http.end(); // Tüneli kapat
    }
    else
    {
      Serial.println(" Wi-Fi bağlantısı koptu, yeniden bağlanılıyor...");
    }
  }

  // 3. 1 Saniyelik Kesintisiz Örnekleme Döngüsü
  // İnternet gecikmesi kalktığı için artık tam 1 saniyede bir insan geçişlerini kaçırmadan yakalayacak!
  delay(1000);
}