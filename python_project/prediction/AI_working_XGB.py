import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder
import numpy as np

# Load dataset, skipping lines starting with '#'
df = pd.read_csv("annotated_light_tracking.csv", comment="#")
# The first three lines are for header
df = df.iloc[2:]
# Strip any extra whitespace from column names
df.columns = df.columns.str.strip()
# Verify column names to make sure '_time' exists
#print(df.columns)

# Convert the '_time' column to datetime if it's not already
df['_time'] = pd.to_datetime(df['_time'])

# Check the first few rows to ensure data is loaded correctly
print(df.head())

# If '_time' is parsed correctly, continue with feature engineering
df['hour'] = df['_time'].dt.hour

# Check if the transformation works
print(df[['hour', '_time']].head())

# Rename and select required columns
df = df.rename(columns={"position": "room", "_value": "light_level"})
df = df[['hour', 'room', 'light_level']]

# Shift light level to create the target for the next time step
df['next_light_level'] = df.groupby('room')['light_level'].shift(-1)
df = df.dropna(subset=['next_light_level'])
df['next_light_level'] = df['next_light_level'].apply(lambda x: int(x))
print()
print("Let's print the shifted dataset")
print(df[1:20])

# One-hot encode the 'room' column
encoder = OneHotEncoder(sparse_output=False)
encoded_rooms = encoder.fit_transform(df[['room']])
room_columns = encoder.categories_[0]  # Room categories (e.g., balcony, bedroom, living_room)
encoded_rooms_df = pd.DataFrame(encoded_rooms, columns=room_columns)

# Merge encoded rooms with the original DataFrame
df = pd.concat([df.reset_index(drop=True), encoded_rooms_df.reset_index(drop=True)], axis=1)

# Prepare features and target
X = df[['hour'] + list(room_columns) + ['light_level']]
print("I now print the training values")
print(X.head())
y = df['next_light_level']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {'objective': 'reg:squarederror', 'eval_metric': 'rmse'}
model = xgb.train(params, dtrain, num_boost_round=20)

# Save the trained model and encoder
model.save_model("xgb_model.json")
encoder_path = "room_encoder.npy"
np.save(encoder_path, encoder)  # Save encoder for future predictions

# Predict on test data
y_pred = model.predict(dtest).astype(int)

# Print some prediction examples
print(f'Room       | Current Light Level | Real Next Light | Predicted Next Light')
for i, (real, pred) in enumerate(zip(y_test, y_pred)):
    current_light = X_test.iloc[i]['light_level']
    room = X_test.iloc[i][['balcony', 'bedroom']].idxmax()
    print(f'{room:<10} | {current_light}              | {real}            | {pred}')
    if i >= 20:
        break

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")