import network
import urequests
import utime
import machine
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Set the ID of the ESP32/ARDUINO, so that data is placed in the right bucket.
DEVICE_ID = "ESP32_1"

# Wi-Fi credentials
#WIFI_SSID = "MatteoBellettiAifon"
#WIFI_PASSWORD = "dopoladico"
WIFI_SSID = "FASTWEB-BellMant"
WIFI_PASSWORD = "teladicodopo"

# Server and MQTT broker details
SERVER_URL = "http://172.20.10.2:5000/sensor_data"
MQTT_SERVER = "172.20.10.2"
MQTT_PORT = 1883
MQTT_TOPIC_SAMPLING = "plant/sampling_rate"
MQTT_TOPIC_POSITION = "plant/change_position"

# ESP32 pin configuration
LIGHT_SENSOR_PIN1 = 36  # GPIO 36
LIGHT_SENSOR_PIN2 = 39  # GPIO 39
LED_PIN = Pin(5, Pin.OUT)

# Default sampling rate and position
sampling_rate = 5000  # milliseconds
current_position = "bedsidetable"

# Wi-Fi connection setup
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"[WiFi] Connecting to {WIFI_SSID}...")
    
    while not wlan.isconnected():
        print(f"[WiFi] waiting for connection to {WIFI_SSID}...")
        utime.sleep(3)
    print("\nConnected to WiFi")
    print(f"IP: {wlan.ifconfig()[0]}")

# MQTT callback function
def mqtt_callback(topic, msg):
    global sampling_rate, current_position
    if topic == MQTT_TOPIC_SAMPLING.encode():
        sampling_rate = int(msg.decode()) * 1000  # Convert to milliseconds
        print(f"Sampling rate updated: {sampling_rate} ms")
    elif topic == MQTT_TOPIC_POSITION.encode():
        current_position = msg.decode()
        print(f"Position updated: {current_position}")

# Setup MQTT client
def setup_mqtt():
    client = MQTTClient("ESP32Client", MQTT_SERVER, port=MQTT_PORT)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC_SAMPLING)
    client.subscribe(MQTT_TOPIC_POSITION)
    print("Connected to MQTT and subscribed to topics")
    return client

# Read sensor values
def read_sensors():
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    ldr1.atten(ADC.ATTN_11DB)
    ldr2.atten(ADC.ATTN_11DB)
    return ldr1.read(), ldr2.read()

# FOR DEBUGGING -> Interpret light level
def interpret_light(value, sensor_id):
    if value < 40:
        print(f" => Dark{sensor_id}: {value}")
    elif value < 800:
        print(f" => Dim{sensor_id}: {value}")
    elif value < 2000:
        print(f" => Light{sensor_id}: {value}")
    elif value < 3200:
        print(f" => Bright{sensor_id}: {value}")
    else:
        print(f" => Very bright{sensor_id}: {value}")

#TODELETE
def blink():
    while True:
        # Blink the LED
        LED_PIN.on()  # Turn on (HIGH)
        utime.sleep(1)  # Wait for 1 second
        LED_PIN.off()  # Turn off (LOW)
        utime.sleep(1)  # Wait for 1 second

# Main function
def main():
    connect_wifi()
    client = setup_mqtt()

    while True:
        LED_PIN.off()
        # MQTT check
        client.check_msg()
        
        # Read sensors
        ldr1_value, ldr2_value = read_sensors()
        timestamp = utime.ticks_ms()
        
        # Interpret light levels
        interpret_light(ldr1_value, 1)
        interpret_light(ldr2_value, 2)

        # data to send to HTTP
        data = {
            #TODO check this out: recently modified sensor values to be a vector
            "sensors_values": [ldr1_value,ldr2_value],
            "position": current_position,
            "sampling_rate": sampling_rate,
            "timestamp": timestamp,
            "device_id": DEVICE_ID
        }
        LED_PIN.on()
        # Send data via HTTP
        try:
            response = urequests.post(SERVER_URL, json=data)
            print("Response:", response.text)
            response.close()
        except Exception as e:
            print("Error sending POST:", e)

        # Delay based on the sampling rate
        utime.sleep_ms(sampling_rate)

# Run the main loop
main()
