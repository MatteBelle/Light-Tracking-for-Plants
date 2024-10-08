#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-light-sensor
 */

// USING "ALKS ESP32" as esp32 board.

const char* ssid = "MatteoBellettiAifon";
const char* password = "dopoladico";
// Laptop IP and HTTP server endpoint
const char* serverUrl = "http://172.20.10.2:5000/sensor_data";  // replace <laptop_IP> with the laptop's IP address (retrieved through cmd it has no '/16')
//const char* serverUrl = "http://172.20.10.2:5000/sensor_data";  // replace <laptop_IP> with the laptop's IP address (retrieved through settings it has a '/16')

// MQTT broker details
const char* mqtt_server = "<laptop_IP>"; // Replace with the IP where the MQTT broker runs
const char* mqtt_topic_sampling = "plant/sampling_rate";
const char* mqtt_topic_position = "plant/change_position";

// WiFiClient espClient;
// PubSubClient client(espClient);

#define LIGHT_SENSOR_PIN1 36  // ESP32 pin GIOP36 (ADC0)
#define LIGHT_SENSOR_PIN2 39  // ESP32 pin GIOP39 (ADC0)

int sampling_rate = 5000; // Default to 10 seconds

void setup_wifi() {
  delay(1000);
  //WiFi.mode(WIFI_STA); //Optional
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Connecting to ");
  Serial.println(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nConnected to the WiFi network");

  //print wifi information
  get_network_info();
}

//WIFT WIFI WIFI WIFI WIFI WIFI WIFT WIFI WIFI WIFI WIFI WIFI WIFT
void get_network_info() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("[*] Network information for ");
    Serial.println(ssid);

    Serial.println("[+] BSSID : " + WiFi.BSSIDstr());
    Serial.print("[+] Gateway IP : ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("[+] Subnet Mask : ");
    Serial.println(WiFi.subnetMask());
    Serial.println((String) "[+] RSSI : " + WiFi.RSSI() + " dB");
    Serial.print("[+] ESP32 IP : ");
    Serial.println(WiFi.localIP());
  }
}
//WIFT WIFI WIFI WIFI WIFI WIFI WIFT WIFI WIFI WIFI WIFI WIFI WIFT

// void mqtt_callback(char* topic, byte* payload, unsigned int length) {
//   String message;
//   for (int i = 0; i < length; i++) {
//     message += (char)payload[i];
//   }

//   if (String(topic) == mqtt_topic_sampling) {
//     sampling_rate = message.toInt();
//     Serial.println("Sampling rate updated: " + String(sampling_rate));
//   }

//   if (String(topic) == mqtt_topic_position) {
//     // Handle position update logic (if needed)
//     Serial.println("Received new position: " + message);
//   }
// }

// void setup_mqtt() {
//   client.setServer(mqtt_server, 1883);
//   client.setCallback(mqtt_callback);
  
//   while (!client.connected()) {
//     Serial.print("Connecting to MQTT...");
//     if (client.connect("ESP32Client")) {
//       Serial.println("connected");
//       client.subscribe(mqtt_topic_sampling);
//       client.subscribe(mqtt_topic_position);
//     } else {
//       Serial.print("failed, rc=");
//       Serial.print(client.state());
//       delay(5000);
//     }
//   }
// }

// ACTUAL SETUP CALL
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);

  // Initialize WiFi and MQTT
  setup_wifi();
  //setup_mqtt();

  // set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
}

void loop() {
  // if (!client.connected()) {
  //   setup_mqtt();
  // }
  // client.loop();

  // reads the input on analog pin (value between 0 and 4095)
  int LDR1_pin = analogRead(LIGHT_SENSOR_PIN1);
  int LDR2_pin = analogRead(LIGHT_SENSOR_PIN2);
  long timestamp = millis();  // Get timestamp for the data

    // JSON payload
  String jsonData = "{\"sensor_1_value\":" + String(LDR1_pin) + 
                    ",\"sensor_2_value\":" + String(LDR2_pin) + 
                    ",\"timestamp\":" + String(timestamp) + "}";

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

  // Send data to the laptop via HTTP
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error sending POST: " + String(httpResponseCode));
    }

    http.end();
  }

  delay(sampling_rate); // Delay based on the current sampling rate
}