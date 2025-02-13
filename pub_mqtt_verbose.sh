#!/bin/bash

# Set MQTT Broker and Port
BROKER=${BROKER:-"localhost"}  # Default broker
PORT=${PORT:-1883}             # Default MQTT port

echo "Fetching available MQTT topics..."
# Capture topics for a few seconds (change timeout as needed)
mosquitto_sub -h "$BROKER" -p "$PORT" -t '#' -C 1 --quiet | awk -F ' ' '{print $1}' | sort -u

# Ask user for the topic
read -p "Enter the topic to publish to: " TOPIC

# Check if topic is empty
if [[ -z "$TOPIC" ]]; then
    echo "Error: Topic must be provided."
    exit 1
fi

echo "Fetching last known message for topic '$TOPIC'..."
LAST_MESSAGE=$(mosquitto_sub -h "$BROKER" -p "$PORT" -t "$TOPIC" -C 1 --quiet)

if [[ -z "$LAST_MESSAGE" ]]; then
    echo "No recent messages found for topic '$TOPIC'."
else
    echo "Current value of '$TOPIC': $LAST_MESSAGE"
fi

# Ask user for new message
read -p "Enter the message to publish: " MESSAGE

# Check if message is empty
if [[ -z "$MESSAGE" ]]; then
    echo "Error: Message cannot be empty."
    exit 1
fi

# Publish the message
mosquitto_pub -h "$BROKER" -p "$PORT" -t "$TOPIC" -m "$MESSAGE"

# Confirm the message was sent
if [[ $? -eq 0 ]]; then
    echo "Message '$MESSAGE' successfully published to topic '$TOPIC' on broker '$BROKER'."
else
    echo "Failed to publish message. Please check your broker settings and topic."
fi
