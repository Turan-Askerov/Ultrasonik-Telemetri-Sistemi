#define BLYNK_TEMPLATE_ID   "TMPL6NuzQNjV"
#define BLYNK_TEMPLATE_NAME "UltraSonic"
#define BLYNK_AUTH_TOKEN    "SU3bw9xtNGz-MiEZ5-_uyagc64AXcufC"
#define BLYNK_PRINT Serial

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

char ssid[] = "Electromagnetic Field";
char pass[] = "P3R3VFRFMFYJ";

#define TRIG_PIN D1
#define ECHO_PIN D2

BlynkTimer timer;
bool aktif = true;

// Bu fonksiyonu BLYNK_WRITE(V1) nin üstüne ekle
BLYNK_CONNECTED() 
{
  Blynk.syncVirtual(V1);  // bağlanınca switch durumunu çek
}
// V1 switch'i dinle
BLYNK_WRITE(V1) {
  aktif = param.asInt();  // 1=açık, 0=kapalı
  if (aktif) Serial.println("Anahtar AÇIK");
  else Serial.println(" Anahtar KAPALI");
}

int mesafeOlc() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long sure = pulseIn(ECHO_PIN, HIGH, 30000);
  
  Serial.print("Ham sure degeri: ");  // debug için
  Serial.println(sure);

  int mesafe = sure * 0.034 / 2;

  if (mesafe <= 0 || mesafe > 400) return -1;
  return mesafe;
}

void sendData() {
  if (!aktif) return;  // switch kapalıysa dur

  int mesafe = mesafeOlc();
  if (mesafe == -1) {
    Serial.println("Sensör okunamadı!");
    return;
  }

  Serial.print("Mesafe: ");
  Serial.print(mesafe);
  Serial.println(" cm");

  Blynk.virtualWrite(V0, mesafe);  // sadece V0 gauge'a gidiyor
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.println("\n--- ESP BAŞLADI ---");

  WiFi.begin(ssid, pass);
  Serial.print("WiFi bağlanıyor");

  int t = 0;
  while (WiFi.status() != WL_CONNECTED && t < 20) {
    delay(500);
    Serial.print(".");
    t++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi BAĞLANDI!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi BAĞLANAMADI!");
    return;
  }

  Blynk.config(BLYNK_AUTH_TOKEN);
  Blynk.connect();

  timer.setInterval(2000L, sendData);
}

void loop() {
  Blynk.run();
  timer.run();
}