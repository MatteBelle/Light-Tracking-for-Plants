# Light-Tracking-for-Plants
This project involves creating an IoT system to monitor daily light exposure for plants using ESP32 and LDR sensors. The system collects data to optimize plant placement based on light needs. HTTP and MQTTP protocols are used, local InfluxDB is used to stock data and query it and Grafana is used to show graphs.
A Telegram bot is deployed to access information about plants and rooms and change it.

# If run locally follow the following steps:
1) Clone this repository.
2) Access the folder where the file "requirements.txt" is located.
3) Activate a new conda environment (not to alter your personal python library versions).
4) Run the command "pip install -r requirements.txt" in the bash to install all required libraries and versions
5) Copy the folder "esp32_files" on your ESP_32 device supporting micropython (look for tutorials to flash it)
6) Modify the variables in this file for HTTP, MQTT and WI-FI connections to connect it to the same network as the pc.
7) Modify the variables in the "configs.py" file (python_project/data_proxy/configs.py) for influxdb, HTTP and MQTT.
8) Create a ".env" file in "data_proxy/" containing the three sensitive variables in this format (they will be loaded in configs at runtime):
"
INFLUXDB_PASSWORD=yourinfluxdbpassword
INFLUXDB_TOKEN=yourinfluxdbtoken
TELEGRAM_BOT=yourtelegrambotkey
"
9) Run the "run_all.py" file in "python_project/".
9.1) it runs the HTTP python file. (python_project/data_proxy/data_proxy_HTTP.py)
9.2) it runs the MQTT python file. (python_project/data_proxy/data_proxy_MQTT.py)
9.3) it runs un the Telegram file (python_project/telegram/telegram_bot.py)
    9.3.1) n.b. To work with your telegram Bot you need to get a personal token
10) Finally, run the esp32 having two ldr sensors connected (eventually, modify the pins in the esp_32 main file).
11) Via Telegram bot you can:
    - add, delete or modify plants
    - add, delete or modify positions
    - ask for suggestion about the plant position, based on required light (as in daily light hours) and current and available positions light.
12) Via Web interface you can
    - swiftly visualize the house configuration
    - add, delete or modify plants
    - add, delete or modify positions
13) Via MQTT you can
    - publish to broker to change sampling rate of the ESP32
    - publish to broker to change position of the ESP32

# To access Influxdb UI and the saved data 
1) install influxdb (i.e. using brew install)
2) run the command "sudo influxd" to run the local server (you can also run with only "influxd" but I configured my credentials with sudo)
3) access it via browser using "localhost" and the chosen port (i.e., http://localhost:8086/)
4) TODO: create a file named ".env" where you will save local variables for accessing InfluxDB. This file MUST REMAIN PRIVATE and NOT pushed to a git repository, since it will contain sensible data. In this file you have to save local environental variables which will be add to the project by "configs.py".
The content of the .env file should be (replace yourpassword and yourtoken with the data your personal information):
"INFLUXDB_PASSWORD=yourpassword
INFLUXDB_TOKEN=yourtoken
TELEGRAM_BOT=yourtelegrambotkey"

n.b. it might be necessary to modify the configuration file