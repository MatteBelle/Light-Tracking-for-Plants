#!/bin/bash

# Start Grafana
brew services start grafana

# Start Mosquitto
brew services start mosquitto

# Start InfluxDB
echo "Starting InfluxDB with sudo privileges..."
sudo influxd
