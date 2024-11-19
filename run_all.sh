#!/bin/bash

# Run the MicroPython script on the ESP32 via Thonny
echo "Starting MicroPython script on ESP32..."
thonny --run /Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Data_proxy/esp32_micropython.mpy.py &
thonny_pid=$!

# Run the data_proxy_HTTP.ipynb notebook
echo "Starting data_proxy_HTTP.ipynb..."
jupyter nbconvert --to notebook --execute /Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Data_proxy/data_proxy_HTTP.ipynb --inplace &
http_pid=$!

# Run the data_proxy_MQTT.ipynb notebook
echo "Starting data_proxy_MQTT.ipynb..."
jupyter nbconvert --to notebook --execute /Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Data_proxy/data_proxy_MQTT.ipynb --inplace &
mqtt_pid=$!

# Wait for all background processes to finish
wait $thonny_pid $http_pid $mqtt_pid
echo "All processes finished."