#!/bin/bash

# Prompt user for broker details if not set as environment variables
#BROKER=${BROKER:-"127.0.0.1"}  # Default: localhost
BROKER=${BROKER:-"172.20.10.2"}  # Default: localhost
PORT=${PORT:-1883}             # Default MQTT port

# Prompt user for topic and message
read -p "Enter the topic to publish to: " TOPIC
read -p "Enter the message to publish: " MESSAGE

# Check if the topic or message is empty
if [[ -z "$TOPIC" || -z "$MESSAGE" ]]; then
    echo "Error: Both topic and message must be provided."
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