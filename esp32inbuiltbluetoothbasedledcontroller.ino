#esp32 inbuilt bluetooth use. 
#include <BluetoothSerial.h>
BluetoothSerial SerialBT;

const int ledPin = 2; // Pin connected to the built-in LED (usually pin 2 on ESP32)

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_BT"); // Bluetooth device name
  pinMode(ledPin, OUTPUT);    // Set the LED pin as an output
  digitalWrite(ledPin, HIGH); // Set the LED to its default state (off)
}

void loop() {
  if (SerialBT.available()) {
    char incoming = SerialBT.read();
    Serial.println(incoming);

    if (incoming == '1') {
      Serial.println("Received: 1");
      digitalWrite(ledPin, HIGH); // Turn on the LED (active low)
      delay(2000);
      digitalWrite(ledPin, LOW);
    } else if (incoming == '0') {
      Serial.println("Received: 0");
    }
  }
}
