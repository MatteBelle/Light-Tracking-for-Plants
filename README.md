# Light-Tracking-for-Plants
This project involves creating an IoT system to monitor daily light exposure for plants using ESP32 and LDR sensors. The system collects data to optimize plant placement based on light needs. HTTP and MQTTP protocols are used.

# If run locally follow the following steps:
1) install mosquitto.
2) run mosquitto from bash using the bash command "brew services start mosquitto" (on Linux or MacOs).
3) run the HTTP python file.
4) run the MQTT python file.
5) connect the proxy to the same wifi network as the ESP32. To connect the ESP32 to the network, modify its code changing the variables related to the wifi credentials.
6) finally, run the esp32 script.

# To access Influxdb UI and the saved data 
1) install influxdb (i.e. using brew install)
2) run the command "sudo influxd" to run the local server (you can also run with only "influxd" but I configured my credentials with sudo)
3) access it via browser using "localhost" and the chosen port (i.e., http://localhost:8086/)

n.b. it might be necessary to modify the configuration file