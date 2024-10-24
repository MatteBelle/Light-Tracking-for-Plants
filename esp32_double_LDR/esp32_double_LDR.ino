#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>

// Wi-Fi credentials/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/esp32_double_LDR/esp32_double_LDR.ino
const char* ssid = "MatteoBellettiAifon";
const char* password = "dopoladico";

// Laptop IP and HTTP server endpoint
const char* serverUrl = "http://172.20.10.2:5000/sensor_data";  // Replace with your laptop's IP address

// MQTT broker details
//const char* mqtt_server = "172.20.10.2"; // Replace with the IP where the MQTT broker runs 127.0.0.1
const char* mqtt_server = "127.0.0.1";  // Replace with the IP where the MQTT broker runs
const char* mqtt_topic_sampling = "plant/sampling_rate";
const char* mqtt_topic_position = "plant/change_position";

// WiFiClient and PubSubClient objects
WiFiClient espClient;
PubSubClient client(espClient);

#define LIGHT_SENSOR_PIN1 36  // ESP32 pin GIOP36 (ADC0)
#define LIGHT_SENSOR_PIN2 39  // ESP32 pin GIOP39 (ADC0)

int sampling_rate = 5000;                // Default to 5000ms (5 seconds)
String current_position = "position A";  // Default position

// Function to connect to WiFi
void setup_wifi() {
  delay(1000);
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] Connecting to ");
  Serial.println(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nConnected to the WiFi network");
  get_network_info();
}

// Function to print WiFi details
void get_network_info() {
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("[*] Network information for " + String(ssid));
    Serial.println("[+] BSSID : " + WiFi.BSSIDstr());
    Serial.print("[+] Gateway IP : ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("[+] Subnet Mask : ");
    Serial.println(WiFi.subnetMask());
    Serial.println("[+] RSSI : " + String(WiFi.RSSI()) + " dB");
    Serial.print("[+] ESP32 IP : ");
    Serial.println(WiFi.localIP());
  }
}

// MQTT callback function to handle incoming messages
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  if (String(topic) == mqtt_topic_sampling) {
    sampling_rate = message.toInt() * 1000;  // multiplied by 1000 as it takes needs to convert milliseconds to seconds
    Serial.println("Sampling rate updated: " + String(sampling_rate) + " ms");
  }

  if (String(topic) == mqtt_topic_position) {
    current_position = message;
    Serial.println("position updated: " + current_position);
  }
}

// Function to setup MQTT client
void setup_mqtt() {
  client.setServer(mqtt_server, 1883);
  client.setCallback(mqtt_callback);

  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      client.subscribe(mqtt_topic_sampling);
      client.subscribe(mqtt_topic_position);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

// SETUP function
void setup() {
  Serial.begin(9600);

  // Initialize WiFi and MQTT
  setup_wifi();
  //setup_mqtt();

  // Set the ADC attenuation to 11 dB (up to ~3.3V input)
  analogSetAttenuation(ADC_11db);
}

// LOOP function
void loop() {
  // if (!client.connected()) {
  //   setup_mqtt();
  // }
  //client.loop();

  // Read values from analog pins
  int LDR1_pin = analogRead(LIGHT_SENSOR_PIN1);
  int LDR2_pin = analogRead(LIGHT_SENSOR_PIN2);
  long timestamp = millis();  // Get timestamp for the data

  // JSON payload with sensor data, timestamp, and current position
  String jsonData = "{\"sensor_1_value\":" + String(LDR1_pin) + ",\"sensor_2_value\":" + String(LDR2_pin) + ",\"position\":\"" + String(current_position) + "\"" + ",\"sampling_rate\":\"" + String(sampling_rate) + "\"" + ",\"timestamp\":" + String(timestamp) + "}";

  // Print light conditions based on threshold
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

      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
    }

    http.end();
  }

  // Delay based on the current sampling rate
  delay(sampling_rate);
}
