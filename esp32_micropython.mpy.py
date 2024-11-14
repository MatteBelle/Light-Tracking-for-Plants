import network
import urequests
import utime
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Wi-Fi credentials
ssid = "MatteoBellettiAifon"
password = "dopoladico"

# Server and MQTT broker details
server_url = "http://172.20.10.2:5000/sensor_data"
mqtt_server = "172.20.10.2"
mqtt_port = 1883
mqtt_topic_sampling = "plant/sampling_rate"
mqtt_topic_position = "plant/change_position"

# ESP32 pin configuration
LIGHT_SENSOR_PIN1 = 36  # GPIO 36
LIGHT_SENSOR_PIN2 = 39  # GPIO 39

# Default sampling rate and position
sampling_rate = 5000  # milliseconds
current_position = "position A"

# Wi-Fi connection setup
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print(f"[WiFi] Connecting to {ssid}...")
    
    while not wlan.isconnected():
        print(f"[WiFi] waiting for connection to {ssid}...")
        utime.sleep(1)
    print("\nConnected to WiFi")
    print(f"IP: {wlan.ifconfig()[0]}")

# MQTT callback function
def mqtt_callback(topic, msg):
    global sampling_rate, current_position
    if topic == mqtt_topic_sampling.encode():
        sampling_rate = int(msg.decode()) * 1000  # Convert to milliseconds
        print(f"Sampling rate updated: {sampling_rate} ms")
    elif topic == mqtt_topic_position.encode():
        current_position = msg.decode()
        print(f"Position updated: {current_position}")

# Setup MQTT client
def setup_mqtt():
    client = MQTTClient("ESP32Client", mqtt_server, port=mqtt_port)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(mqtt_topic_sampling)
    client.subscribe(mqtt_topic_position)
    print("Connected to MQTT and subscribed to topics")
    return client

# Read sensor values
def read_sensors():
    ldr1 = ADC(Pin(LIGHT_SENSOR_PIN1))
    ldr2 = ADC(Pin(LIGHT_SENSOR_PIN2))
    ldr1.atten(ADC.ATTN_11DB)
    ldr2.atten(ADC.ATTN_11DB)
    return ldr1.read(), ldr2.read()

# Interpret light level
def interpret_light(value, sensor_id):
    if value < 40:
        print(f" => Dark{sensor_id}")
    elif value < 800:
        print(f" => Dim{sensor_id}")
    elif value < 2000:
        print(f" => Light{sensor_id}")
    elif value < 3200:
        print(f" => Bright{sensor_id}")
    else:
        print(f" => Very bright{sensor_id}")

# Main function
def main():
    connect_wifi()
    client = setup_mqtt()

    while True:
        # MQTT check
        client.check_msg()
        
        # Read sensors
        ldr1_value, ldr2_value = read_sensors()
        timestamp = utime.ticks_ms()
        
        # Interpret light levels
        interpret_light(ldr1_value, 1)
        interpret_light(ldr2_value, 2)

        # JSON data for HTTP
        json_data = {
            "sensor_1_value": ldr1_value,
            "sensor_2_value": ldr2_value,
            "position": current_position,
            "sampling_rate": sampling_rate,
            "timestamp": timestamp
        }

        # Send data via HTTP
        try:
            response = urequests.post(server_url, json=json_data)
            print("Response:", response.text)
            response.close()
        except Exception as e:
            print("Error sending POST:", e)

        # Delay based on the sampling rate
        utime.sleep_ms(sampling_rate)

# Run the main loop
main()