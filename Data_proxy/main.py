import os
# import sys
# import time
# import requests
# import json

import subprocess
from configs import *
import data_proxy_HTTP
import data_proxy_MQTT

# if __name__ == "__main__":
#     # HTTP
#     # Run the HTTP server to receive sensor data and send it to InfluxDB
#     http_proxy = data_proxy_HTTP.DataProxyHTTP()
#     http_proxy.run()

#     print("HTTP server running...")
    
#     # MQTT
#     mqtt_proxy = data_proxy_MQTT.DataProxyMQTT()
#     mqtt_proxy.connect()
#     # Example actions
#     mqtt_proxy.subscribe_topic("custom/topic")
#     mqtt_proxy.publish_message(MQTT_TOPIC_SAMPLING, 3)
#     mqtt_proxy.publish_message(MQTT_TOPIC_POSITION, "Bedroom Desk")
#     mqtt_proxy.change_position("Office")
    
#     print("MQTT client running...")

#     # try:
#     #     while True:
#     #         pass
#     # except KeyboardInterrupt:
#     #     mqtt_proxy.disconnect()

if __name__ == "__main__":
    #scripts = ['data_proxy_MQTT.py', 'data_analytics/main.py', 'data_analytics/run_predictions.py', 'telegram_bot.py']
    scripts = ['data_proxy_MQTT', 'data_proxy_HTTP']
    scripts_extension = '.py'
    scripts_folder = "Data_proxy/"
    processes = []
    # if log folder does not exist, create it
    if not os.path.exists("logs"):
        os.makedirs("logs")
    for script in scripts:
        try:
            # creating log files to store outputs and errors of each script
            with open(f"logs/{script}.log", "w") as log_file:
                process = subprocess.Popen(['python', scripts_folder+script+scripts_extension], stdout=log_file, stderr=subprocess.STDOUT)
                processes.append(process)
        except Exception as e:
            print(f"Error launching {script}: {e}")

    for process in processes:
        process.wait()