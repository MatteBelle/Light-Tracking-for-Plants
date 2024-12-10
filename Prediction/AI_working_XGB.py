import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder

# Prepare the data as before
df = pd.read_csv("light_data_with_hour_only.csv")

# Shift the light level to get the next light level
df['next_light_level'] = df.groupby('room')['light_level'].shift(-1)
df = df.dropna(subset=['next_light_level'])

# One-hot encode 'room' column
encoder = OneHotEncoder(sparse_output=False)
encoded_rooms = encoder.fit_transform(df[['room']])
encoded_rooms_df = pd.DataFrame(encoded_rooms, columns=encoder.categories_[0])

# Merge everything into a final DataFrame
df = pd.concat([df, encoded_rooms_df], axis=1)
X = df[['timestamp'] + list(encoded_rooms_df.columns) + ['light_level']]
y = df['next_light_level']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {'objective': 'reg:squarederror', 'eval_metric': 'rmse'}
model = xgb.train(params, dtrain, num_boost_round=100)

# Predict on test data
y_pred = model.predict(dtest)

# Evaluate model
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

def predict_and_print(model, X_data, y_data):
    """
    This function takes a trained model, input features (X_data), and real target values (y_data),
    and prints the room, current light level, real light level, and predicted light level.

    Parameters:
    - model: Trained XGBoost model
    - X_data: Input features (e.g., test data or any new data)
    - y_data: Actual light levels (real values) to compare predictions against
    """
    # Make predictions on the input data
    y_pred = model.predict(xgb.DMatrix(X_data))
    
    # Iterate over the data and print the room, current light level, real, and predicted light levels
    print(f'Room       | Current Light Level | Real Next Light | Predicted Next Light')
    
    for i, (real, pred) in enumerate(zip(y_data, y_pred)):
        # Extract the current light level from the 'light_level' column of X_data
        current_light = X_data.iloc[i]['light_level']
        
        # Determine the room by checking which column has a value of 1.0
        room = X_data.iloc[i][['balcony', 'bedroom', 'living_room']].idxmax()
        
        print(f'{room:<10} | {current_light:.2f}              | {real:.2f}            | {pred:.2f}')

# Example usage:
# Predict and print the results for the test data
predict_and_print(model, X_test, y_test)