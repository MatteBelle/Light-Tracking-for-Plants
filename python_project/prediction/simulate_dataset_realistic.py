#This code is used to simulate data for a month or so with some constraints. it is useful as it provides realistic data to work

import random
import pandas as pd
from datetime import datetime, timedelta

# Constants
start_date = datetime(2024, 11, 1)  # Start date
end_date = datetime(2024, 12, 14)  # End date
rooms = ["balcony", "bedroom", "living_room"]
hours_in_day = 24
days_in_november = (end_date - start_date).days + 1

# Time range for `_start` and `_stop`
_start = datetime.utcnow() - timedelta(hours=6)  # Example start
_stop = datetime.utcnow()  # Example stop

# Function to simulate light levels
def simulate_light_level():
    return random.uniform(60, 100)  # Simulated sensor value

# Generate dataset
data = []
for day in range(1, days_in_november + 1):
    date = start_date + timedelta(days=day - 1)
    for hour in range(hours_in_day):
        for room in rooms:
            sensors_mean = simulate_light_level()
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

# #This code is used to simulate data for a month or so with some constraints. it is useful as it provides realistic data to work

# import random
# import pandas as pd
# from datetime import datetime, timedelta

# # Constants
# start_date = datetime(2024, 11, 1)  # Start date
# end_date = datetime(2024, 12, 14)  # End date
# rooms = ["balcony", "bedroom", "living_room"]
# hours_in_day = 24
# days_in_november = (end_date - start_date).days + 1

# # Time range for `_start` and `_stop`
# _start = datetime.utcnow() - timedelta(hours=6)  # Example start
# _stop = datetime.utcnow()  # Example stop

# # Function to simulate light levels
# def simulate_light_level():
#     return random.uniform(60, 100)  # Simulated sensor value

# # Generate dataset
# data = []
# for day in range(1, days_in_november + 1):
#     date = start_date + timedelta(days=day - 1)
#     for hour in range(hours_in_day):
#         for room in rooms:
#             sensors_mean = simulate_light_level()
#             data.append({
#                 "_result": "",  # Leave `_result` empty
#                 "table": 1,  # Example table number
#                 "_start": _start.isoformat() + "Z",  # Convert to RFC3339
#                 "_stop": _stop.isoformat() + "Z",
#                 "_time": (datetime.combine(date, datetime.min.time()) + timedelta(hours=hour)).isoformat() + "Z",
#                 "_value": sensors_mean,
#                 "_field": "sensors_mean",
#                 "_measurement": "light_tracking",
#                 "device_id": "ESP32_1",
#                 "position": room,
#                 "sampling_rate": "5000",
#             })

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Add annotated CSV metadata
# annotated_csv = [
#     "#group,false,false,true,true,false,false,true,true,true,true,true",
#     "#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string,string,string,string,string",
#     "#default,mean,,,,,,,,,,",
#     ",result,table,_start,_stop,_time,_value,_field,_measurement,device_id,position,sampling_rate",
# ]

# # Add data rows
# for _, row in df.iterrows():
#     annotated_csv.append(
#         f",{row['_result']},{row['table']},{row['_start']},{row['_stop']},{row['_time']},"
#         f"{row['_value']},{row['_field']},{row['_measurement']},{row['device_id']},"
#         f"{row['position']},{row['sampling_rate']}"
#     )

# # Save to CSV file
# output_file = "annotated_light_tracking.csv"
# with open(output_file, "w") as f:
#     f.write("\n".join(annotated_csv))

# print(f"Annotated CSV has been saved to '{output_file}'.")