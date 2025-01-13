import json
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from configs import *
class PlantLightManager:
    # def __init__(self,
    #              influxdb_url = INFLUXDB_URL,
    #              influxdb_token = INFLUXDB_TOKEN,
    #              influxdb_org = INFLUXDB_ORG,
    #              bucket = INFLUXDB_BUCKET,
    #              measurement = INFLUXDB_MEASUREMENT_NAME,
    #              config_file = CONFIG_PLANT_FILE):
    #     self.client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    #     self.bucket = bucket
    #     self.measurement = measurement
    #     self.config_file = config_file
    def __init__(self):
        self.bucket = INFLUXDB_BUCKET
        self.measurement = INFLUXDB_MEASUREMENT_NAME
        self.config_file = CONFIG_PLANT_FILE
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

    def _get_all_avg_light(self):
        query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -30d)
            |> filter(fn: (r) => r["_measurement"] == "{INFLUXDB_MEASUREMENT_NAME}")
            |> filter(fn: (r) => r["_field"] == "sensors_mean")
            |> filter(fn: (r) => r["_value"] > 50)  // Keep only values greater than 50
            |> aggregateWindow(every: 1h, fn: count, createEmpty: false)  // Group by 1-hour windows
            |> group(columns: ["position"])  // Group by position
            |> sum(column: "_value")  // Sum the hourly counts for each position
            |> yield(name: "monthly_light")
        '''
        try:
            result = self.client.query_api().query(org=INFLUXDB_ORG, query=query)
            averages = {}
            for table in result:
                for record in table.records:
                    position = record.values["position"]
                    averages[position] = record.get_value()/30
            
            return averages  # Dictionary containing average light hours for all positions
        except Exception as e:
            print(f"Error while querying InfluxDB: {e}")
            return None

    def _load_config(self):
        with open(self.config_file, "r") as file:
            config_data = json.load(file)
        return config_data
    
    def suggest_position(self):
        """
        Checks if plants are receiving enough light and suggests a new position if they are not.
        """
        # Get all average light values for the last week
        position_light_dict = self._get_all_avg_light()
        # Print the average light values for all positions
        print("Average light values over the last 7 days by position:")
        for position, avg_light in position_light_dict.items():
            print(f"{position}: {avg_light}")
        
        # Load plant configurations
        plants = self._load_config()
        suggestions = []  # Collect suggestions for all plants
        # Find a new position with sufficient light
        for plant in plants:
            name = plant["name"]  # Fix: Correct key for plant name
            optimal_light = plant["optimal_light_amount"]
            current_position = plant["position"]
            current_light = position_light_dict.get(current_position, 0)

            if current_light < optimal_light:
                # Try to find a better position
                best_position = None
                best_light = current_light  # Start with current light level
                
                for pos, avg_light in position_light_dict.items():
                    if avg_light >= optimal_light and pos != current_position:
                        # Found a suitable position
                        suggestions.append(
                            f"Not enough daylight! Move plant '{name}' to optimal position '{pos}'."
                        )
                        break  # No need to look further if optimal is found
                    
                    # If no optimal position, find the best improvement
                    if avg_light > best_light and pos != current_position:
                        best_position = pos
                        best_light = avg_light

                # If no optimal position found, suggest the best available improvement
                if not suggestions and best_position:
                    suggestions.append(
                        f"Move plant '{name}' (requires {optimal_light}) to position '{best_position}' (provides {best_light}). "
                        f"It's not optimal, but it's better than '{current_position}' (provides {current_light})."
                    )
                # If no improvement is possible
                if not suggestions:
                    suggestions.append(f"No enough light for plant '{name}', but current room is the best available.")

        # Return all suggestions
        return suggestions if suggestions else ["All plants are receiving sufficient light."]

    def display_suggestions(self):
        """
        Displays the suggestions for plant positions in a user-friendly way.
        """
        suggestions = self.suggest_position()
        print("\nSuggestions for Plant Positions:")
        for suggestion in suggestions:
            print(suggestion)


# Example usage
if __name__ == "__main__":
    # Initialize the manager with appropriate settings
    manager = PlantLightManager()
    # Display the suggestions
    manager.display_suggestions()