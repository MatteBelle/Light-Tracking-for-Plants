import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.preprocessing import LabelEncoder

# Load the dataset
file_path = "/content/light_data_november_with_sunrise_sunset_distribution.csv"
df = pd.read_csv(file_path)

# Parameters
BATCH_SIZE = 64
EPOCHS = 300
LEARNING_RATE = 0.01
CHECKPOINT_PATH = "/content/best_model.pth"  # File path to save the best model

# Preprocess data
def preprocess_data(df):
    """
    Prepares data where for each room at hour t, the model learns to predict the light level at hour t+1.
    """
    # Encode the room names using LabelEncoder
    le = LabelEncoder()
    df['room_encoded'] = le.fit_transform(df['room'])

    # Ensure light levels are numeric
    df['light_level'] = pd.to_numeric(df['light_level'], errors='coerce')

    # Fill missing values with 0 (or any other strategy)
    df.fillna(0, inplace=True)

    # Light levels (rooms) for each hour
    light_levels = df.pivot(index='timestamp', columns='room_encoded', values='light_level').values
    rooms = df['room_encoded'].unique()  # Get the number of unique rooms

    # Prepare sequences: the input is the current hour light levels + room encoding, and target is the next hour light levels
    sequences = []
    targets = []
    for i in range(len(light_levels) - 1):
        input_seq = light_levels[i]  # Current hour's light levels
        target_seq = light_levels[i + 1]  # Next hour's light levels
        sequences.append(input_seq)
        targets.append(target_seq)

    return np.array(sequences), np.array(targets), rooms

sequences, targets, rooms = preprocess_data(df)

# Custom Dataset
class LightDataset(Dataset):
    def __init__(self, sequences, targets):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]

# Dataset and DataLoader
dataset = LightDataset(sequences, targets)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# Define Neural Network
class LightPredictor(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LightPredictor, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Model, Loss, Optimizer
input_size = len(rooms)  # Number of rooms (after encoding)
hidden_size = 128
output_size = input_size  # Predict light for the next hour (same number of rooms)

model = LightPredictor(input_size, hidden_size, output_size)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# Training Loop with Checkpointing
def train_model(model, train_loader, val_loader, epochs, checkpoint_path):
    best_val_loss = float('inf')  # Initialize the best validation loss
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for inputs, targets in train_loader:
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        val_loss = 0
        model.eval()
        with torch.no_grad():
            for inputs, targets in val_loader:
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                val_loss += loss.item()

        # Check if validation loss is the best so far
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), checkpoint_path)  # Save the model
            print(f"Epoch {epoch+1}: Validation loss improved to {val_loss/len(val_loader):.4f}. Model weights saved.")

        print(f"Epoch {epoch+1}/{epochs}, Train Loss: {train_loss/len(train_loader):.4f}, Val Loss: {val_loss/len(val_loader):.4f}")

# Train the model
train_model(model, train_loader, val_loader, EPOCHS, CHECKPOINT_PATH)

# Predict Function
def predict_future_light(model, input_sequence):
    """
    Predict the light level for the next hour given the current hour's light levels and room encoding.
    """
    model.eval()
    with torch.no_grad():
        input_sequence = torch.tensor(input_sequence, dtype=torch.float32).view(1, -1)
        output = model(input_sequence)
        return output.numpy()

# Example Prediction
example_input = sequences[-1]  # Take the last sequence from the dataset (current hour)
model.load_state_dict(torch.load(CHECKPOINT_PATH))  # Load the best model weights
predicted_light = predict_future_light(model, example_input)

print("Predicted Light Levels for the Next Hour:")
print(predicted_light)