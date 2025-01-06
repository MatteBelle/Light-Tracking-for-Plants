import random
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Constants
start_date = datetime(2024, 11, 1)  # Start date: 1st November
end_date = datetime(2024, 12, 14)  # End date: 30th November
rooms = ["balcony", "bedroom", "living_room"]
hours_in_day = 24
days_in_november = 30

# Initial sunrise and sunset times on December 1st (these will shift each day)
initial_sunrise = datetime.strptime("07:50", "%H:%M")
initial_sunset = datetime.strptime("17:00", "%H:%M")

# Light bounds for each room (upper and lower bounds)
room_light_bounds = {
    "balcony": (60, 100),
    "bedroom": (40, 80),
    "living_room": (20, 60),
}

# Function to generate light level based on normal distribution
def generate_light_level(bounds, variance_factor=0.2):
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
    if hour_of_day == sunrise_transition_start.hour:
        # Gradual increase in light during the 1 hour before sunrise
        return generate_light_level((0, bounds[0]), variance_factor=0.1)
    elif sunrise_time.hour <= hour_of_day < sunrise_transition_start.hour:
        # Gradual increase during sunrise
        transition_factor = (hour_of_day - sunrise_time.hour) / 1  # 1 hour of transition
        return int(bounds[0] * transition_factor)
    elif hour_of_day == sunset_transition_start.hour:
        # Gradual decrease in light during the 1 hour before sunset
        return generate_light_level((bounds[0], bounds[1]), variance_factor=0.1)
    elif sunset_time.hour <= hour_of_day < sunset_transition_start.hour:
        # Gradual decrease during sunset
        transition_factor = (hour_of_day - sunset_time.hour) / 1  # 1 hour of transition
        return int(bounds[1] * (1 - transition_factor))
    elif is_daytime:
        return generate_light_level(bounds)  # Use random distribution for daytime
    else:
        return generate_light_level((0, 15), variance_factor=0.1)  # Low light or dark during night

# Generate dataset
data = []

for day in range(1, days_in_november + 1):
    date = start_date + timedelta(days=day - 1)  # Adjusting index to start from 1
    for hour in range(hours_in_day):
        for room in rooms:
            light_level = simulate_light_level(room, hour, day)
            data.append({
                "timestamp": datetime.combine(date, datetime.min.time()) + timedelta(hours=hour),
                "room": room,
                "light_level": light_level
            })

# Convert to DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the dataset
print(df.head())

# Save to CSV file
df.to_csv("light_data_november_with_sunrise_sunset_distribution.csv", index=False)

print("Dataset has been saved to 'light_data_november_with_sunrise_sunset_distribution.csv'.")