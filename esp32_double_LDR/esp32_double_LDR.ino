/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-light-sensor
 */

// USING "ALKS ESP32" as esp32 board.

#define LIGHT_SENSOR_PIN1 36 // ESP32 pin GIOP36 (ADC0)
#define LIGHT_SENSOR_PIN2 39 // ESP32 pin GIOP39 (ADC0)

//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------
#include <WiFi.h>
#include <HTTPClient.h>

// Access Point credentials
const char* ssid = "ESP32_AP";
const char* password = "12345678";  // A password is required by ESP32 for AP mode

// Server details (laptop's IP and port)
const char* serverUrl = "http://<laptop-IP>:5000/sensor_data";
//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------

void setup() {
//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------
  // Start the Access Point
  WiFi.softAP(ssid, password);

  Serial.println("Access Point Started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------

  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);

  // set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
}

void loop() {
  // reads the input on analog pin (value between 0 and 4095)
  int LDR1_pin = analogRead(LIGHT_SENSOR_PIN1);
  int LDR2_pin = analogRead(LIGHT_SENSOR_PIN2);
  long timestamp = millis();  // Get timestamp for the data

  // Serial.print("Analog Value = ");
  // Serial.print(LDR1_pin);   // the raw analog reading

  // We'll have a few threshholds, qualitatively determined
  if (LDR1_pin < 40) {
    Serial.println(" => Dark1");
  } else if (LDR1_pin < 800) {
    Serial.println(" => Dim1");
  } else if (LDR1_pin < 2000) {
    Serial.println(" => Light1");
  } else if (LDR1_pin < 3200) {
    Serial.println(" => Bright1");
  } else {
    Serial.println(" => Very bright1");
  }

    if (LDR2_pin < 40) {
    Serial.println(" => Dark2");
  } else if (LDR2_pin < 800) {
    Serial.println(" => Dim2");
  } else if (LDR2_pin < 2000) {
    Serial.println(" => Light2");
  } else if (LDR2_pin < 3200) {
    Serial.println(" => Bright2");
  } else {
    Serial.println(" => Very bright2");
  }

//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------
  // JSON payload
  String jsonData = "{\"sensor_1_value\":" + String(LDR1_pin) + ",\"sensor_2_value\":" + String(LDR2_pin) + ",\"timestamp\":" + String(timestamp) + "}";

  // Send data via HTTP
  if(WiFi.softAPgetStationNum() > 0) {  // Check if there's any connected client
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);
    
    if(httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response from server: " + response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("No client connected to AP");
  }
//ESP32 WIFI CONNECTION PART -------------------------------------------------------------------------------

  delay(500);
}

