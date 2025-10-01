
#include <LiquidCrystal.h>
const int TEMP_PIN = A0;     
const int PULSE_PIN = 3;    
const int BUZZER_PIN = 4;   
const int LED_PIN = 5;       
LiquidCrystal lcd(12, 11, 10, 9, 8, 7);


const int BPM_HISTORY = 4;
float bpmHistory[BPM_HISTORY];
int bpmIndex = 0;
int bpmCount = 0;

unsigned long lastBeatTime = 0;
int lastButtonState = HIGH;   
const unsigned long MIN_BEAT_INTERVAL = 250UL; 
unsigned long lastTempMillis = 0;
const unsigned long TEMP_READ_INTERVAL = 1500UL;

void setup() {
  pinMode(PULSE_PIN, INPUT_PULLUP);  
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  lcd.begin(16, 2);
  Serial.begin(9600);

  lcd.print("Health Monitor");
  delay(1000);
  lcd.clear();
  for (int i = 0; i < BPM_HISTORY; i++) bpmHistory[i] = 0;
}

void loop() {
  int buttonState = digitalRead(PULSE_PIN);
  if (buttonState == LOW && lastButtonState == HIGH) {
    unsigned long now = millis();
    if (lastBeatTime != 0) {
      unsigned long interval = now - lastBeatTime;
      if (interval >= MIN_BEAT_INTERVAL) {
        float thisBPM = 60000.0 / interval;
        bpmHistory[bpmIndex] = thisBPM;
        bpmIndex = (bpmIndex + 1) % BPM_HISTORY;
        if (bpmCount < BPM_HISTORY) bpmCount++;
      }
    }
    lastBeatTime = now;
  }
  lastButtonState = buttonState;

  unsigned long nowMillis = millis();
  if (nowMillis - lastTempMillis >= TEMP_READ_INTERVAL) {
    lastTempMillis = nowMillis;

    // Average BPM
    float avgBPM = 0;
    if (bpmCount > 0) {
      for (int i = 0; i < bpmCount; i++) avgBPM += bpmHistory[i];
      avgBPM /= bpmCount;
    }

    // Read LM35 temperature
    int raw = analogRead(TEMP_PIN);
    float voltage = raw * (5.0 / 1023.0);
    float tempC = voltage * 100.0;

    // ---- ALERT SYSTEM ----
    bool alert = false;
    if (tempC > 38.0 || (bpmCount > 0 && avgBPM > 100)) {
      alert = true;
    }
    if (alert) {
      digitalWrite(BUZZER_PIN, HIGH);
      digitalWrite(LED_PIN, HIGH);
    } else {
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(LED_PIN, LOW);
    }
    Serial.print(millis() / 1000);
    Serial.print(", ");
    Serial.print(tempC, 1);
    Serial.print(", ");
    if (bpmCount > 0) Serial.println(avgBPM, 1);
    else Serial.println("N/A");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp:");
    lcd.print(tempC, 1);
    lcd.print((char)223); 
    lcd.print("C");

    lcd.setCursor(0, 1);
    lcd.print("BPM:");
    if (bpmCount > 0) lcd.print(avgBPM, 0);
    else lcd.print("--");

    if (alert) {
      lcd.setCursor(10, 1);
      lcd.print("ALRT");
    }
  }
}

