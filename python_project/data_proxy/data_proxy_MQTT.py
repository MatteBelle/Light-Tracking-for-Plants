import paho.mqtt.client as mqtt
import logging
from configs import *  # Access configuration constants


class DataProxyMQTT:
    def __init__(self):
        """
        Initialize the MQTT client and set up configurations.
        """
        self.client = mqtt.Client()
        self.plant_position = PLANT_POSITION
        self.MQTT_broker = MQTT_BROKER
        self._setup_callbacks()
        self.logger = self._setup_logger()

    def _setup_callbacks(self):
        """
        Set up MQTT client callbacks.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def _setup_logger(self):
        """
        Set up a logger for better debugging and logging.
        """
        logger = logging.getLogger("MQTTDataProxy")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback triggered upon connecting to the MQTT broker.
        """
        if rc == 0:
            self.logger.info("Connected to MQTT Broker successfully.")
        else:
            self.logger.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback triggered when the MQTT client disconnects from the broker.
        """
        self.logger.warning(f"Disconnected from MQTT Broker. Return code: {rc}")

    def on_message(self, client, userdata, msg):
        """
        Callback triggered upon receiving a message from a subscribed topic.
        """
        self.logger.info(f"Received message: {msg.payload.decode()} from topic: {msg.topic}")

    def connect(self):
        """
        Connect the MQTT client to the broker and start its loop.
        """
        self.client.connect(MQTT_BROKER)
        self.client.loop_start()
        self.logger.info(f"MQTT client connected to broker at {MQTT_BROKER}")

    def disconnect(self):
        """
        Stop the MQTT loop and disconnect the client.
        """
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("MQTT client disconnected.")

    def publish_message(self, topic, message):
        """
        Publish a message to a specific MQTT topic.
        """
        self.client.publish(topic, message)
        self.logger.info(f"Published message: {message} to topic: {topic}")

    def change_position(self, new_position):
        """
        Change the plant's position and notify via MQTT.
        """
        self.plant_position = new_position
        self.logger.info(f"Plant position changed to: {self.plant_position}")
        self.publish_message(MQTT_TOPIC_POSITION, self.plant_position)

    def subscribe_topic(self, topic):
        """
        Subscribe to a specific MQTT topic.
        """
        self.client.subscribe(topic)
        self.logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe_topic(self, topic):
        """
        Unsubscribe from a specific MQTT topic.
        """
        self.client.unsubscribe(topic)
        self.logger.info(f"Unsubscribed from topic: {topic}")

    def process_incoming_message(self, topic, payload):
        """
        Process received messages based on their topic.
        Extend this function to handle specific topics or commands.
        """
        if topic == MQTT_TOPIC_POSITION:
            self.logger.info(f"Processing position update: {payload}")
            # Add custom processing for position updates
        elif topic == MQTT_TOPIC_SAMPLING:
            self.logger.info(f"Processing sampling rate update: {payload}")
            # Add custom processing for sampling updates
        else:
            self.logger.info(f"Unhandled topic: {topic} with payload: {payload}")


if __name__ == "__main__":
    try:
        # Example usage
        mqtt_proxy = DataProxyMQTT()
        mqtt_proxy.connect()

        # Publish messages
        mqtt_proxy.publish_message(MQTT_TOPIC_SAMPLING, "5s")  # Example: Set sampling rate to 5 seconds
        mqtt_proxy.change_position("Living Room")  # Example: Change position to Living Room

        # Keep the script running for MQTT to continue
        while True:
            pass

    except KeyboardInterrupt:
        mqtt_proxy.disconnect()
        print("MQTT client disconnected.")