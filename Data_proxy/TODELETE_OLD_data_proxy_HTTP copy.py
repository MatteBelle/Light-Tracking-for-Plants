import json
import time
from flask import Flask, request, jsonify
from influxdb import InfluxDBClient
import os
from datetime import datetime
from influxdb_custom_handler import save_to_influxdb
# to access configuration constants
from configs import *
app = Flask(__name__)

def set_up_and_run():
    app = Flask(__name__)
    # Run the Flask app on localhost and port 5000 (set in configs.py)
    app.run(host='0.0.0.0', port=HTTP_PORT)

# Endpoint to receive sensor data via HTTP, received as request
@app.route('/sensor_data', methods=['POST'])
def sensor_data():
    try:
        data = request.get_json()
        # Get the current date and time
        now = datetime.now()

        # TODO 1: Delete formatted time unless used to save information locally (influxdb is already saving the timestamp)
        # Format the date and time
        formatted_time = now.strftime("%Y/%m/%d/%H:%M:%S")
        print(f"Formatted date and time: {formatted_time}")

        # Prepare data for InfluxDB
        influx_data = [
            {
                "measurement": INFLUXDB_MEASUREMENT_NAME,
                "tag": {
                    "device_id": data["device_id"],
                    "position": data["position"],
                    "sampling_rate": data["sampling_rate"],
                },
                "field": {
                    # TODO 2: CHECK IF THIS WORKS AS I RECENTLY MODIFIED IT
                    "sensors_values": data["sensors_values"]
                }
                #"timestamp": formatted_time
            }
        ]
        #save_data_to_influxdb(influx_data)

        # Save data locally to a file
        with open(JSON_FILE, 'a') as f:
            json.dump(data, f)
            f.write('\n')
         
        # Write to InfluxDB (if needed)
        # client.write_points(influx_data)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# TODO 3: ADAPT DATA SHOWING PROCESS AS IT WAS MODIFIED
# I create a dynamic web page to display the last data received via http post on sensor_data, and update every 3 seconds
@app.route('/')
def index():
    try:
        with open(JSON_FILE, 'r') as f:
            lines = f.readlines()
            last_line = lines[-1]
            data = json.loads(last_line)
            
            # TODO 4: CHECK IF THIS WORKS AS I RECENTLY MODIFIED IT
            # Generate HTML for sensor values
            sensor_values_html = ''.join(
                f"<p>Sensor {i + 1} value: {value}</p>"
                for i, value in enumerate(data["sensors_values"].values())
            )

            return f'''
            <html>
            <head>
            <meta http-equiv="refresh" content="3">
            </head>
            <body>
            <h1>Plant Light Sensor Data</h1>
            <p>Last data received:</p>
            {sensor_values_html}
            <p>Position: {data["position"]}</p>
            </body>
            </html>
            '''
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=HTTP_PORT)