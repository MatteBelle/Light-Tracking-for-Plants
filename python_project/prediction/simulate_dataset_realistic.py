#This code is used to simulate data for a month or so with some constraints. it is useful as it provides realistic data to work

import random
import pandas as pd
from datetime import datetime, timedelta
import math
import numpy as np

# Constants
start_date = datetime(2024, 11, 1)  # Start date
end_date = datetime(2025, 1, 15)  # End date
rooms = ["balcony", "bedroom"]
hours_in_day = 24
registered_days = (end_date - start_date).days + 1

# Time range for `_start` and `_stop`
_start = datetime.utcnow() - timedelta(hours=6)  # Example start
_stop = datetime.utcnow()  # Example stop

# Initial sunrise and sunset times on December 1st (these will shift each day)
initial_sunrise = datetime.strptime("07:50", "%H:%M")
initial_sunset = datetime.strptime("17:00", "%H:%M")

# Light bounds for each room (lower and upper bounds)
room_light_bounds = {
    "balcony": (94, 100),
    "bedroom": (85, 100),
}

# Light time bounds for each room (lower and upper bounds)
room_light_time_bounds = {
    "balcony": (7, 17),
    "bedroom": (9, 23),
}

# Function to generate light level based on normal distribution
def generate_light_level(bounds, variance_factor=0.12):
    """
    Generate a light level using a normal distribution.
    :param bounds: Tuple of (min_light, max_light).
    :param variance_factor: Fraction of the range to use as standard deviation.
    :return: Light level, clipped within bounds.
    """
    min_light, max_light = bounds
    mean = (min_light + max_light) / 2  # Mean is the midpoint of the bounds
    std_dev = (max_light - min_light) * variance_factor  # Standard deviation
    light_level = np.random.normal(mean, std_dev)  # Generate random value
    return int(np.clip(light_level, min_light, max_light))  # Clip within bounds

# Function to simulate light level considering sunrise and sunset with gradual transition
def simulate_light_level(room, hour_of_day, day_of_month):
    # Calculate sunrise and sunset for the given day
    sunrise_time = initial_sunrise + timedelta(minutes=day_of_month - 1)
    sunset_time = initial_sunset + timedelta(minutes=day_of_month - 1)
    
    # Calculate the times for smooth transition (1 hour before sunrise and sunset)
    sunrise_transition_start = sunrise_time - timedelta(hours=1)
    sunset_transition_start = sunset_time - timedelta(hours=1)

    # Get light bounds for the room
    bounds = room_light_bounds[room]
    
    # Determine if it's daytime (between sunrise and sunset)
    is_daytime = sunrise_time.hour <= hour_of_day < sunset_time.hour

    # Light levels based on transitions around sunrise and sunset
    if hour_of_day < room_light_time_bounds[room][0] or hour_of_day > room_light_time_bounds[room][1]:
        return 0
    elif hour_of_day == sunrise_transition_start.hour:
        # Gradual increase in light during the 1 hour before sunrise
        return generate_light_level((0, bounds[0]), variance_factor=0.05)
    elif sunrise_time.hour <= hour_of_day < sunrise_transition_start.hour:
        # Gradual increase during sunrise
        transition_factor = (hour_of_day - sunrise_time.hour) / 1  # 1 hour of transition
        return int(bounds[0] * transition_factor)
    elif hour_of_day == sunset_transition_start.hour:
        # Gradual decrease in light during the 1 hour before sunset
        return generate_light_level((bounds[0], bounds[1]), variance_factor=0.05)
    elif sunset_time.hour <= hour_of_day < sunset_transition_start.hour:
        # Gradual decrease during sunset
        transition_factor = (hour_of_day - sunset_time.hour) / 1  # 1 hour of transition
        return int(bounds[1] * (1 - transition_factor))
    elif is_daytime:
        return generate_light_level(bounds)  # Use random distribution for daytime
    else:
        return generate_light_level((0, 15), variance_factor=0.1)  # Low light or dark during night

# # Function to simulate light levels
# def simulate_light_level():
#     return random.uniform(60, 100)  # Simulated sensor value

# Generate dataset
data = []
for day in range(1, registered_days + 1):
    date = start_date + timedelta(days=day - 1)
    for hour in range(hours_in_day):
        for room in rooms:
            sensors_mean = math.trunc(simulate_light_level(room, hour, day))
            data.append({
                "_result": "",  # Leave `_result` empty
                "table": 1,  # Example table number
                "_start": _start.isoformat() + "Z",  # Convert to RFC3339
                "_stop": _stop.isoformat() + "Z",
                "_time": (datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)).isoformat() + "Z",
                "_value": sensors_mean,
                "_field": "sensors_mean",
                "_measurement": "light_tracking",
                "device_id": "ESP32_1",
                "position": room,
                "sampling_rate": "5000",
            })

# Convert to DataFrame
df = pd.DataFrame(data)

# Add annotated CSV metadata
annotated_csv = [
    "#group,false,false,true,true,false,false,true,true,true,true,true",
    "#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string,string,string,string,string",
    "#default,mean,,,,,,,,,,",
    ",result,table,_start,_stop,_time,_value,_field,_measurement,device_id,position,sampling_rate",
]

# Add data rows
for _, row in df.iterrows():
    annotated_csv.append(
        f",{row['_result']},{row['table']},{row['_start']},{row['_stop']},{row['_time']},"
        f"{row['_value']},{row['_field']},{row['_measurement']},{row['device_id']},"
        f"{row['position']},{row['sampling_rate']}"
    )

# Save to CSV file
output_file = "annotated_light_tracking.csv"
with open(output_file, "w") as f:
    f.write("\n".join(annotated_csv))

print(f"Annotated CSV has been saved to '{output_file}'.")
