import xgboost as xgb
import pandas as pd
import numpy as np

class LightPredictor:
    def __init__(self, model_path, encoder_path):
        # Load trained model
        self.model = xgb.Booster()
        self.model.load_model(model_path)

        # Load the one-hot encoder
        self.encoder = np.load(encoder_path, allow_pickle=True).item()
        self.room_columns = self.encoder.categories_[0]  # Known room categories

    def predict(self, timestamp, room, light_level):
        """
        Predict the next light level based on input features.

        Args:
            timestamp (int): The current timestamp.
            room (str): Room name (can be known or unknown).
            light_level (float): Current light level.

        Returns:
            float: Predicted next light level.
        """
        # Prepare input data as a dictionary
        input_data = {'hour': [timestamp], 'light_level': [light_level]}
        
        # Initialize one-hot encoding for rooms
        for col in self.room_columns:
            input_data[col] = [0]  # Default to 0 for all room columns
        
        # Handle known and unknown rooms
        if room in self.room_columns:
            # Known room: Set the corresponding one-hot column to 1
            input_data[room][0] = 1
        else:
            # Unknown room: Set all room columns to the average value
            avg_value = 1 / len(self.room_columns)
            for col in self.room_columns:
                input_data[col][0] = avg_value

        # Convert to DataFrame in the correct feature order
        feature_order = ['hour'] + list(self.room_columns) + ['light_level']
        input_df = pd.DataFrame(input_data)[feature_order]

        # Predict using the model
        dmatrix = xgb.DMatrix(input_df)
        prediction = self.model.predict(dmatrix)
        # crop prediction in the range [0, 100]
        prediction = np.clip(prediction, 0, 100)
        return prediction[0]  # Return the single prediction value

    def predict_n(self, timestamp, room, light_level, n=1):
        """
        Predict the next 'n' light levels, reusing the predicted value for each step.

        Args:
            timestamp (int): The current timestamp.
            room (str): Room name (can be known or unknown).
            light_level (float): Current light level.
            n (int): Number of predictions to make.

        Returns:
            list: List of 'n' predicted light levels.
        """
        predictions = []
        for i in range(n):
            # Predict the next light level
            next_light_level = self.predict(timestamp, room, light_level)
            
            # Add the prediction to the list
            predictions.append(float(next_light_level))
            
            # Update the light_level for the next prediction
            light_level = next_light_level
            timestamp += 1  # Update timestamp (assuming hourly increments)

        return predictions

# Example usage
if __name__ == "__main__":
    model_path = "/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Light-Tracking-for-Plants/python_project/prediction/models_weights/xgb_model.json"
    encoder_path = "/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Light-Tracking-for-Plants/python_project/prediction/models_weights/room_encoder.npy"
    
    predictor = LightPredictor(model_path, encoder_path)
    
    # Known room prediction
    pred1 = predictor.predict(timestamp=6, room="balcony", light_level=7)
    print(f"Prediction for known room (balcony): {pred1}")
    
    # Unknown room prediction
    pred2 = predictor.predict(timestamp=6, room="kitchen", light_level=7)
    print(f"Prediction for unknown room (kitchen): {pred2}")

        # Known room prediction (predict the next 3 hours for the 'balcony' room)
    pred1 = predictor.predict_n(timestamp=6, room="balcony", light_level=7, n=3)
    print(f"Prediction for known room (balcony) for next 3 hours: {pred1}")
    
    # Unknown room prediction (predict the next 3 hours for the 'kitchen' room)
    pred2 = predictor.predict_n(timestamp=6, room="kitchen", light_level=7, n=3)
    print(f"Prediction for unknown room (kitchen) for next 3 hours: {pred2}")