import network
import urequests
import utime
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Set the ID of the ESP32/ARDUINO, so that data is placed in the right bucket.
DEVICE_ID = "ESP32_1"

# Wi-Fi credentials (alternating options)
WIFI_CREDENTIALS = [
    #("MatteoBellettiAifon", "dopoladico"),
    ("FASTWEB-BellMant", "teladicodopo")
]

# Server and MQTT broker details (alternating options)
SERVER_URLS = [
    "http://192.168.1.92:5000/sensor_data",  # macOS
    "http://192.168.1.67:5000/sensor_data"  # Windows
]

MQTT_SERVERS = [
    "192.168.1.92",
    "192.168.1.67"  # Windows
]

MQTT_PORT = 1883
MQTT_TOPIC_SAMPLING = "plant/sampling_rate"
MQTT_TOPIC_POSITION = "plant/change_position"

# ESP32 pin configuration
LIGHT_SENSOR_PIN1 = 36  # GPIO 36
LIGHT_SENSOR_PIN2 = 39  # GPIO 39
LED_PIN = Pin(5, Pin.OUT)

# Default sampling rate and position
sampling_rate = 5000  # milliseconds
current_position = "bedroom"

# Wi-Fi connection setup
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for ssid, password in WIFI_CREDENTIALS:
        print(f"[WiFi] Trying to connect to {ssid}...")
        wlan.connect(ssid, password)
        attempts = 10
        while not wlan.isconnected() and attempts > 0:
            print(f"[WiFi] Waiting for connection to {ssid}...")
            utime.sleep(1)
            attempts -= 1

        if wlan.isconnected():
            print(f"[WiFi] Connected to {ssid}")
            print(f"IP: {wlan.ifconfig()[0]}")
            return True

    print("[WiFi] Failed to connect to any network.")
    return False

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
    global SERVER_URL, MQTT_SERVER
    client = None

    for mqtt_server, server_url in zip(MQTT_SERVERS, SERVER_URLS):
        print(f"Trying MQTT server: {mqtt_server} and HTTP server: {server_url}")
        try:
            client = MQTTClient("ESP32Client", mqtt_server, port=MQTT_PORT)
            client.set_callback(mqtt_callback)
            client.connect()
            print(f"Connected to MQTT server: {mqtt_server}")
            client.subscribe(MQTT_TOPIC_SAMPLING)
            client.subscribe(MQTT_TOPIC_POSITION)
            global SERVER_URL
            SERVER_URL = server_url
            return client
        except Exception as e:
            print(f"Failed to connect to MQTT server: {mqtt_server}, Error: {e}")

    print("Failed to connect to any MQTT server.")
    return None

# Read sensor values
def read_sensors():
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    ldr1.atten(ADC.ATTN_11DB)
    ldr2.atten(ADC.ATTN_11DB)
    return ldr1.read(), ldr2.read()

# Read sensor values
def read_sensors_u16():
    #val = adc.read_u16()  # read a raw analog value in the range 0-65535
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    return ldr1.read_u16(), ldr2.read_u16()

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

# Main function
def main():
    if not connect_wifi():
        print("[WiFi] Unable to connect to any network. Exiting...")
        return

    client = setup_mqtt()
    if not client:
        print("[MQTT] Unable to connect to any broker. Exiting...")
        return

    while True:
        LED_PIN.off()
        # MQTT check
        client.check_msg()
        
        # Read sensors
        ldr1_value, ldr2_value = read_sensors_u16()
        timestamp = utime.ticks_ms()
        
        # Interpret light levels
        interpret_light(ldr1_value, 1)
        interpret_light(ldr2_value, 2)

        # Data to send via HTTP
        data = {
            "sensors_values": [ldr1_value, ldr2_value],
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
