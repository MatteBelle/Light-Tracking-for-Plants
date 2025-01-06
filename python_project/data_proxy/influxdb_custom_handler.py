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
    
# TO TEST
def get_average_light_last_7_days():
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -7d)
      |> filter(fn: (r) => r._measurement == "{INFLUXDB_MEASUREMENT_NAME}")
      |> filter(fn: (r) => exists r.position)
      |> group(columns: ["position"])
      |> mean(column: "sensors_mean_normalized")
    '''

    try:
        result = client.query_api().query(org=INFLUXDB_ORG, query=query)
        averages = {}
        for table in result:
            for record in table.records:
                position = record.values["position"]
                avg_light = record.get_value()
                averages[position] = avg_light
        
        print("Average light values over the last 7 days by position:")
        for position, avg_light in averages.items():
            print(f"{position}: {avg_light}")
        
        return averages
    except Exception as e:
        print(f"Error while querying InfluxDB: {e}")
        return None
    
# TO TEST
def get_daily_average_light_by_position():
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: 0) // Include all available data
      |> filter(fn: (r) => r._measurement == "{INFLUXDB_MEASUREMENT_NAME}")
      |> filter(fn: (r) => exists r.position)
      |> group(columns: ["position"])
      |> aggregateWindow(every: 1d, fn: mean, column: "sensors_mean_normalized", createEmpty: false)
      |> yield(name: "daily_average")
    '''

    try:
        result = client.query_api().query(org=INFLUXDB_ORG, query=query)
        daily_averages = {}

        for table in result:
            for record in table.records:
                position = record.values["position"]
                date = record.get_time().strftime("%Y-%m-%d")  # Format as 'YYYY-MM-DD'
                avg_light = record.get_value()
                
                # Organize results in a dictionary
                if position not in daily_averages:
                    daily_averages[position] = {}
                daily_averages[position][date] = avg_light

        print("Daily average light values by position:")
        for position, averages in daily_averages.items():
            print(f"{position}:")
            for date, avg_light in averages.items():
                print(f"  {date}: {avg_light}")

        return daily_averages
    except Exception as e:
        print(f"Error while querying InfluxDB: {e}")
        return None