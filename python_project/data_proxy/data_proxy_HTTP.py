import json
import datetime
from flask import Flask, request, jsonify, render_template_string
from configs import *  # Access configuration constants
from influxdb_custom_handler import save_to_influxdb  # Custom InfluxDB handler
import sys

# This is needed as VSCode wouldn't otherwise find the module
sys.path.append('/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Light-Tracking-for-Plants/python_project/')
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
        self.config_plant_file = CONFIG_PLANT_FILE
        self.config_position_file = CONFIG_POSITION_FILE

        # Initialize the predicted light level to 0
        self.predicted_light_level = 50  # Default valuex

        # Define routes
        self._setup_routes()

    def _read_json_file(self, file_path):
        """Read a JSON file and return its content."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _write_json_file(self, file_path, data):
        """Write data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
                
    def normalize_light_value(self, light_value):
        print(light_value, "called normalize_light_value")
        """Normalize the light sensor value to a scale of 0-100."""
        return (light_value / MAX_ABS_LIGHT_VALUE) * MAX_NORMALIZED_LIGHT_VALUE

    def _setup_routes(self):
        """Define the routes for the Flask app."""

        @self.app.route('/')
        def index():
            """Display the main page with forms for plants and positions."""
            plants = self._read_json_file(self.config_plant_file)
            positions = self._read_json_file(self.config_position_file)

            html_template = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Plant and Position Management</title>
            </head>
            <body>
                <h1>Manage Plants</h1>
                <h2>Add a New Plant</h2>
                <form method="POST" action="/add_plant">
                    Name: <input type="text" name="name"><br>
                    Code: <input type="number" name="code"><br>
                    Optimal Light Amount: <input type="number" name="optimal_light_amount"><br>
                    Position: <input type="text" name="position"><br>
                    Sensor: <input type="text" name="sensor"><br>
                    <button type="submit">Add Plant</button>
                </form>

# In the index method, within the HTML template
<h2>Existing Plants</h2>
{% for plant in plants %}
    <p>{{ plant['name'] }} (Code: {{ plant['code'] }}, Optimal Light: {{ plant['optimal_light_amount'] }}, Position: {{ plant['position'] }}, Sensor: {{ plant['sensor'] }})</p>
    <form method="POST" action="/modify_plant">
        <input type="hidden" name="code" value="{{ plant['code'] }}">
        Name: <input type="text" name="name" value="{{ plant['name'] }}"><br>
        Code: <input type="number" name="code" value="{{ plant['code'] }}" readonly><br>
        Optimal Light Amount: <input type="number" name="optimal_light_amount" value="{{ plant['optimal_light_amount'] }}"><br>
        Position: <input type="text" name="position" value="{{ plant['position'] }}"><br>
        Sensor: <input type="text" name="sensor" value="{{ plant['sensor'] }}"><br>
        <button type="submit">Modify</button>
    </form>
    <form method="POST" action="/delete_plant">
        <input type="hidden" name="code" value="{{ plant['code'] }}">
        <button type="submit">Delete</button>
    </form>
{% endfor %}

<h2>Existing Positions</h2>
{% for position in positions %}
    <p>{{ position['name'] }} (ID: {{ position['ID'] }}, Description: {{ position['description'] }}, Sensor: {{ position['sensor'] }})</p>
    <form method="POST" action="/modify_position">
        <input type="hidden" name="ID" value="{{ position['ID'] }}">
        Name: <input type="text" name="name" value="{{ position['name'] }}"><br>
        ID: <input type="number" name="ID" value="{{ position['ID'] }}" readonly><br>
        Description: <input type="text" name="description" value="{{ position['description'] }}"><br>
        Sensor: <input type="text" name="sensor" value="{{ position['sensor'] }}"><br>
        <button type="submit">Modify</button>
    </form>
    <form method="POST" action="/delete_position">
        <input type="hidden" name="ID" value="{{ position['ID'] }}">
        <button type="submit">Delete</button>
    </form>
{% endfor %}
            </body>
            </html>
            '''
            return render_template_string(html_template, plants=plants, positions=positions)
        
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
                            "sensors_mean_normalized": float(normalized_mean),
                            "predicted_light_level": float(self.predicted_light_level) # uses previous predicted value which will be compared with real one
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
        
        @self.app.route('/add_plant', methods=['POST'])
        def add_plant():
            """Add a new plant to the config_plant.json file."""
            try:
                plant = {
                    "name": request.form['name'],
                    "code": int(request.form['code']),
                    "optimal_light_amount": int(request.form['optimal_light_amount']),
                    "position": request.form['position'],
                    "sensor": request.form['sensor']
                }
                plants = self._read_json_file(self.config_plant_file)
                plants.append(plant)
                self._write_json_file(self.config_plant_file, plants)
                return '''
                <html>
                <body>
                    <h2>Plant added successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"

        @self.app.route('/delete_plant', methods=['POST'])
        def delete_plant():
            """Delete a plant from the config_plant.json file."""
            try:
                code = int(request.form['code'])
                plants = self._read_json_file(self.config_plant_file)
                plants = [plant for plant in plants if plant['code'] != code]
                self._write_json_file(self.config_plant_file, plants)
                return '''
                <html>
                <body>
                    <h2>Plant deleted successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"

        @self.app.route('/add_position', methods=['POST'])
        def add_position():
            """Add a new position to the config_position.json file."""
            try:
                position = {
                    "name": request.form['name'],
                    "ID": int(request.form['ID']),
                    "description": request.form['description'],
                    "sensor": request.form['sensor']
                }
                positions = self._read_json_file(self.config_position_file)
                positions.append(position)
                self._write_json_file(self.config_position_file, positions)
                return '''
                <html>
                <body>
                    <h2>Position added successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"

        @self.app.route('/delete_position', methods=['POST'])
        def delete_position():
            """Delete a position from the config_position.json file."""
            try:
                position_id = int(request.form['ID'])
                positions = self._read_json_file(self.config_position_file)
                positions = [position for position in positions if position['ID'] != position_id]
                self._write_json_file(self.config_position_file, positions)
                return '''
                <html>
                <body>
                    <h2>Position deleted successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"
        
        @self.app.route('/modify_plant', methods=['POST'])
        def modify_plant():
            """Modify an existing plant in the config_plant.json file."""
            try:
                plant_code = int(request.form['code'])
                updated_plant = {
                    "name": request.form['name'],
                    "code": plant_code,
                    "optimal_light_amount": int(request.form['optimal_light_amount']),
                    "position": request.form['position'],
                    "sensor": request.form['sensor']
                }
                plants = self._read_json_file(self.config_plant_file)
                # Find and update the plant
                for idx, plant in enumerate(plants):
                    if plant['code'] == plant_code:
                        plants[idx] = updated_plant
                        break
                self._write_json_file(self.config_plant_file, plants)
                return '''
                <html>
                <body>
                    <h2>Plant updated successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"

        @self.app.route('/modify_position', methods=['POST'])
        def modify_position():
            """Modify an existing position in the config_position.json file."""
            try:
                position_id = int(request.form['ID'])
                updated_position = {
                    "name": request.form['name'],
                    "ID": position_id,
                    "description": request.form['description'],
                    "sensor": request.form['sensor']
                }
                positions = self._read_json_file(self.config_position_file)
                # Find and update the position
                for idx, position in enumerate(positions):
                    if position['ID'] == position_id:
                        positions[idx] = updated_position
                        break
                self._write_json_file(self.config_position_file, positions)
                return '''
                <html>
                <body>
                    <h2>Position updated successfully!</h2>
                    <form action="/" method="GET">
                        <button type="submit">Back to Blueprint</button>
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error: {str(e)}"

    def run(self):
        """Run the Flask application."""
        self.app.run(host=self.http_host, port=self.http_port)


# Entry point when running this file directly
if __name__ == '__main__':
    http_proxy = DataProxyHTTP()
    http_proxy.run()