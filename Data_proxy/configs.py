import os
# to load the environment variables saved in the ".env" file. This is done not to leave sensible data clear in the code.
from dotenv import load_dotenv
load_dotenv()

# Shared configs
JSON_FILE = "local_sensor_data.json"
PLANT_POSITION = "bedside table"

# Configs for HTTP
HTTP_PORT = 5000
HTTP_HOST='0.0.0.0'

# Configs for MQTT
# MQTT Broker connection settings
MQTT_BROKER = "localhost"
MQTT_TOPIC_SAMPLING = "plant/sampling_rate"
MQTT_TOPIC_POSITION = "plant/change_position"
# I create a local variable to store the standard position of the plant sensor

# Configs for InfluxDB
# Set up InfluxDB connection details
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = "LightTrackingHome"
INFLUXDB_USER = "MatteBelle"
INFLUXDB_PASSWORD = os.getenv("INFLUXDB_PASSWORD")
#INFLUXDB_BUCKET = "0366cbedcba5db79" #bucket id for LightTrackingHome
#INFLUXDB_ORG = "e3711f89ded12e10" #org id for Light IOT-Light-Tracking
INFLUXDB_ORG = "IOT-Light-Tracking"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN") #"MatteBelle's Token"
INFLUXDB_BUCKET = "LightTrackingHome"
INFLUXDB_URL = f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}"
INFLUXDB_MEASUREMENT_NAME = "light_tracking"