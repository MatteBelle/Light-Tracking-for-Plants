import json
import time
from flask import Flask, request, jsonify
from influxdb import InfluxDBClient
from datetime import datetime
from configs import *  # Access configuration constants
from influxdb_custom_handler import save_to_influxdb  # Custom InfluxDB handler


class DataProxyHTTP:
    def __init__(self):
        """Initialize the Flask app and set up configurations."""
        self.app = Flask(__name__)
        self.json_file = JSON_FILE
        self.http_port = HTTP_PORT
        self.http_host = HTTP_HOST
        self.measurement_name = INFLUXDB_MEASUREMENT_NAME

        # Define routes
        self._setup_routes()

    def _setup_routes(self):
        """Define the routes for the Flask app."""

        @self.app.route('/sensor_data', methods=['POST'])
        def sensor_data():
            try:
                data = request.get_json()
                print("A")
                now = datetime.now()
                print(data)
                # Prepare data for InfluxDB
                influx_data = {
                        "measurement_name": self.measurement_name,
                        "tag": {
                            "device_id": data["device_id"],
                            "position": data["position"],
                            "sampling_rate": data["sampling_rate"],
                        },
                        "field": {
                            "sensors_values": data["sensors_values"]
                        }
                        # InfluxDB handles timestamp automatically
                    }
                print("AA")

                # Save data locally to a file
                with open(self.json_file, 'a') as f:
                    json.dump(data, f)
                    f.write('\n')
                print("AAA")
                

                # Optional: Save to InfluxDB (uncomment if needed)
                save_to_influxdb(influx_data)
                print("AAAA")

                return jsonify({"status": "success"}), 200

            except Exception as e:
                print(f"Error in /sensor_data: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 500

        @self.app.route('/')
        def index():
            try:
                with open(self.json_file, 'r') as f:
                    lines = f.readlines()
                    last_line = lines[-1]
                    data = json.loads(last_line)

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
                print(f"Error in /index: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 500

    def run(self):
        """Run the Flask application."""
        self.app.run(host=self.http_host, port=self.http_port)


# Entry point when running this file directly
if __name__ == '__main__':
    http_proxy = DataProxyHTTP()
    http_proxy.run()