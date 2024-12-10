from influxdb import InfluxDBClient
# to access configuration constants
from configs import *

# Create a connection to the InfluxDB client
client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASSWORD)
client.create_database(INFLUXDB_DATABASE)  # Ensure the database exists
client.switch_database(INFLUXDB_DATABASE)


def save_to_influxdb(json_data):
    """
    Save the ESP32 data to InfluxDB.
    :param json_data: Dictionary containing ESP32 sensor data.
    """
    # Convert json_data to InfluxDB format
    influxdb_data = [
        {
            "measurement": "sensor_data",  # Measurement name
            "tags": {
                "device_id": json_data["device_id"],  # Use device_id as a tag
                "position": json_data["position"]    # Optional: Add position as a tag
            },
            "fields": {
                "sensor_1_value": float(json_data["sensor_1_value"]),
                "sensor_2_value": float(json_data["sensor_2_value"]),
                "sampling_rate": int(json_data["sampling_rate"]),
            },
            "time": json_data["timestamp"]  # Assuming the timestamp is in epoch milliseconds
        }
    ]

    # Write data to InfluxDB
    try:
        client.write_points(influxdb_data)
        print(f"Data successfully written to InfluxDB: {influxdb_data}")
    except Exception as e:
        print(f"Error writing data to InfluxDB: {e}")


# Example usage (replace with actual HTTP handler code)
if __name__ == "__main__":
    # Simulated data received from ESP32
    json_data = {
        "sensor_1_value": 100,
        "sensor_2_value": 200,
        "position": "position A",
        "sampling_rate": 5000,
        "timestamp": "2024-11-19T12:00:00Z",  # ISO 8601 timestamp (adjust format as needed)
        "device_id": "001"
    }
    
    # Save to InfluxDB
    save_to_influxdb(json_data)