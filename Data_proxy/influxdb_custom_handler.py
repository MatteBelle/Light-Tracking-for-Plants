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
        .tag("device_id", data["tag"]["sampling_rate"])
        .tag("position", data["tag"]["position"])
        .tag("sampling_rate", data["tag"]["sampling_rate"])
    )
    for i in range(len(data["field"]["sensors_values"])):
        point.field(f"sensor_{i+1}_luminosity", data["field"]["sensors_values"][i])
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Data successfully written to InfluxDB: {point}")


# Example usage (replace with actual HTTP handler code)
if __name__ == "__main__":
    # Simulated data received from ESP32
    influx_data = [
        {
            "measurement_name": "light_measurement",  # Example measurement name
            "tag": {
                "device_id": "ESP32_1",          # Example device ID
                "position": "position A",        # Example position
                "sampling_rate": "5000ms",       # Example sampling rate
            },
            "field": {
                "sensors_values": [3218, 2599]   # Example sensor values
            }
            # InfluxDB handles timestamp automatically
        }
    ]
    save_to_influxdb(influx_data)