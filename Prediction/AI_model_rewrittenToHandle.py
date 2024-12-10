import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split

# Load the dataset
file_path = "/content/light_data_november_with_sunrise_sunset_distribution.csv"
df = pd.read_csv(file_path)

# Parameters
N = 6  # Predict the next 6 hours
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.001
CHECKPOINT_PATH = "/content/best_model.pth"  # File path to save the best model

# Prepare data
def preprocess_data(df, N):
    """
    Prepares sequences for training a time series model.
    Input: sequences of N hours, Target: next N hours
    """
    light_levels = df.iloc[:, 1:].values  # Exclude timestamp, take light levels
    sequences = []
    targets = []

    for i in range(len(light_levels) - 2 * N):
        input_seq = light_levels[i:i+N]
        target_seq = light_levels[i+N:i+2*N]
        sequences.append(input_seq)
        targets.append(target_seq)

    return np.array(sequences), np.array(targets)

sequences, targets = preprocess_data(df, N)

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
input_size = df.shape[1] - 1  # Number of rooms (features)
hidden_size = 128
output_size = input_size * N  # Predict N hours for all rooms

model = LightPredictor(input_size * N, hidden_size, output_size)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# Training Loop with Checkpointing
def train_model(model, train_loader, val_loader, epochs, checkpoint_path):
    best_val_loss = float('inf')  # Initialize the best validation loss
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for inputs, targets in train_loader:
            inputs = inputs.view(inputs.size(0), -1)  # Flatten sequences
            targets = targets.view(targets.size(0), -1)

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
                inputs = inputs.view(inputs.size(0), -1)
                targets = targets.view(targets.size(0), -1)
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
def predict_future_light(model, input_sequence, N):
    """
    Predict the light levels for the next N hours.
    """
    model.eval()
    with torch.no_grad():
        input_sequence = torch.tensor(input_sequence, dtype=torch.float32).view(1, -1)
        output = model(input_sequence)
        return output.view(N, -1).numpy()

# Example Prediction
example_input = sequences[-1]  # Take the last sequence from the dataset
model.load_state_dict(torch.load(CHECKPOINT_PATH))  # Load the best model weights
predicted_light = predict_future_light(model, example_input, N)

print("Predicted Light Levels for the Next N Hours:")
print(predicted_light)