import paho.mqtt.client as mqtt
# to access configuration constants
from configs import *

mqtt_client = mqtt.Client()

# MQTT connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

# Setup MQTT
def mqtt_setup():
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_BROKER)
    mqtt_client.loop_start()  # Start the MQTT client loop

# Function to publish MQTT messages
def publish_mqtt(topic, message):
    mqtt_client.publish(topic, message)
    print(f"Published message: {message} to topic: {topic}")

# Function to change the position of the plant sensor
def change_position(new_position):
    global plant_position
    plant_position = new_position
    print(f"Plant position changed to: {plant_position}")
    publish_mqtt(MQTT_TOPIC_POSITION, plant_position)

if __name__ == "__main__":
    # Initialize MQTT setup
    mqtt_setup()

    # Example: publishing sampling rate change
    publish_mqtt(MQTT_TOPIC_SAMPLING, 3)  # Change sampling rate to 2 seconds
    
    # Example: publishing position change
    publish_mqtt(MQTT_TOPIC_POSITION, "Bedroom Desk")  # Change position to position B
    
    # Keep the script running for MQTT to continue
    while True:
        pass
