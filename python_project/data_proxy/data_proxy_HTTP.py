import json
import datetime
from flask import Flask, request, jsonify
from configs import *  # Access configuration constants
from influxdb_custom_handler import save_to_influxdb  # Custom InfluxDB handler
from prediction.xgb_prediction import LightPredictor


class DataProxyHTTP:
    def __init__(self):
        """Initialize the Flask app and set up configurations."""
        self.app = Flask(__name__)
        self.json_file = JSON_FILE
        self.http_port = HTTP_PORT
        self.http_host = HTTP_HOST
        self.measurement_name = INFLUXDB_MEASUREMENT_NAME
        self.predictor = LightPredictor(XGB_MODEL_PATH, XGB_ENCODER_PATH)
        # Initialize the predicted light level to 0
        self.predicted_light_level = 50  # Default value

        # Define routes
        self._setup_routes()
    
    def normalize_light_value(self, light_value):
        print(light_value, "called normalize_light_value")
        """Normalize the light sensor value to a scale of 0-100."""
        return (light_value / MAX_ABS_LIGHT_VALUE) * MAX_NORMALIZED_LIGHT_VALUE

    def _setup_routes(self):
        """Define the routes for the Flask app."""

        @self.app.route('/sensor_data', methods=['POST'])
        def sensor_data():
            try:
                print("Received sensor data")
                data = request.get_json()
                datetime.datetime.now().hour
                print(data)
                normalized_mean = self.normalize_light_value(sum(data["sensors_values"]) / len(data["sensors_values"]))
                # Prepare data for InfluxDB
                influx_data = {
                        "measurement_name": self.measurement_name,
                        "tag": {
                            "device_id": data["device_id"],
                            "position": data["position"],
                            "sampling_rate": data["sampling_rate"],
                        },
                        "field": {
                            "sensors_mean_normalized": normalized_mean,
                            "predicted_light_level": int(self.predicted_light_level) # uses previous predicted value which will be compared with real one
                        }
                        # InfluxDB handles timestamp automatically
                    }
                # predicts next light level
                print("Predicted light level: ", self.predicted_light_level)
                self.predicted_light_level = self.predictor.predict(datetime.datetime.now().hour, data["position"], normalized_mean)

                # Save data locally to a file
                with open(self.json_file, 'a') as f:
                    json.dump(data, f)
                    f.write('\n')
                
                save_to_influxdb(influx_data)

                return jsonify({"status": "success", "normalized_mean": normalized_mean}), 200

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