import pandas as pd

# Load the original data
df = pd.read_csv("light_data_november_with_sunrise_sunset_distribution.csv")

# Convert timestamp to datetime and extract the hour
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.hour

# Save the updated dataset
df.to_csv("light_data_with_hour_only.csv", index=False)