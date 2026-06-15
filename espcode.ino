#include <WiFi.h>
#include <WiFiUdp.h>

// ── WiFi credentials ──────────────────────────────────────
const char* SSID     = "B";
const char* PASSWORD = "123456789";
const int   UDP_PORT = 4210;

// ── Motor A pins ──────────────────────────────────────────
#define ENA 14
#define IN1 26
#define IN2 27

// ── Motor B pins ──────────────────────────────────────────
#define ENB 25
#define IN3 32
#define IN4 33

WiFiUDP udp;
bool wifiConnected = false;

// ── Motor helpers ─────────────────────────────────────────
void motorA(int speed, bool forward) {
  speed = constrain(abs(speed), 0, 255);
  digitalWrite(IN1, forward ? HIGH : LOW);
  digitalWrite(IN2, forward ? LOW  : HIGH);
  ledcWrite(ENA, speed);
}

void motorB(int speed, bool forward) {
  speed = constrain(abs(speed), 0, 255);
  digitalWrite(IN3, forward ? HIGH : LOW);
  digitalWrite(IN4, forward ? LOW  : HIGH);
  ledcWrite(ENB, speed);
}

void stopAll() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  ledcWrite(ENA, 0);
  ledcWrite(ENB, 0);
}

void handleCommand(char cmd) {
  switch (cmd) {
    case 'F': motorA(130, true);  motorB(130, true);  break; // Forward medium
    case 'B': motorA(130, false); motorB(130, false); break; // Backward medium
    case 'L': motorA(110, false); motorB(110, true);  break; // Turn left medium
    case 'R': motorA(110, true);  motorB(110, false); break; // Turn right medium
    case 'S': stopAll();                               break; // Stop
    default:  stopAll();                               break;
  }
}

void connectWiFi() {
  Serial.println("\n=== WiFi Debug ===");
  Serial.printf("Connecting to SSID: [%s]\n", SSID);

  WiFi.disconnect(true);
  delay(1000);
  WiFi.mode(WIFI_STA);
  delay(500);

  Serial.println("Scanning for networks...");
  int n = WiFi.scanNetworks();
  Serial.printf("Found %d networks:\n", n);
  bool found = false;
  for (int i = 0; i < n; i++) {
    Serial.printf("  %s (RSSI: %d)\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
    if (WiFi.SSID(i) == SSID) found = true;
  }

  if (!found) {
    Serial.println("✗ Your hotspot was NOT found in scan!");
    Serial.println("  → Turn hotspot OFF and ON again");
    Serial.println("  → Make sure band is 2.4GHz");
    return;
  }

  Serial.println("✓ Hotspot found! Connecting...");
  WiFi.begin(SSID, PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("✓ WiFi Connected!");
    Serial.print("✓ IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.printf("✓ UDP listening on port %d\n", UDP_PORT);
    Serial.println("==================");
    udp.begin(UDP_PORT);
  } else {
    wifiConnected = false;
    int status = WiFi.status();
    Serial.printf("✗ Connection FAILED! Status: %d\n", status);
    if (status == 1) Serial.println("  → Hotspot name wrong");
    if (status == 4) Serial.println("  → Password wrong");
    if (status == 6) Serial.println("  → Try restarting ESP32");
    Serial.println("==================");
  }
}

// ── Setup ─────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  ledcAttach(ENA, 1000, 8);
  ledcAttach(ENB, 1000, 8);
  ledcWrite(ENA, 0);
  ledcWrite(ENB, 0);

  stopAll();
  connectWiFi();
}

// ── Loop ──────────────────────────────────────────────────
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    if (wifiConnected) {
      Serial.println("WiFi lost! Reconnecting...");
      wifiConnected = false;
    }
    connectWiFi();
    delay(5000);
    return;
  }

  int pktSize = udp.parsePacket();
  if (pktSize > 0) {
    char cmd = udp.read();
    Serial.printf("CMD: %c\n", cmd);
    handleCommand(cmd);
  }

  if (Serial.available()) {
    char cmd = Serial.read();
    handleCommand(cmd);
  }
}