# to access configuration constants
from configs import *
from datetime import datetime
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Function to save data to InfluxDB, atm called by the HTTP handler
def save_to_influxdb(data):
    point = (
        Point(data["measurement_name"])
        .tag("device_id", data["tag"]["device_id"])
        .tag("position", data["tag"]["position"])
        .tag("sampling_rate", data["tag"]["sampling_rate"])
        .field("sensors_mean", data["field"]["sensors_mean_normalized"])
        .field("predicted_light_level", data["field"]["predicted_light_level"])
    )
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Data successfully written to InfluxDB: {point}")