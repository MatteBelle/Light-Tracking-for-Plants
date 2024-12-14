import subprocess
from data_proxy.configs import *

scripts = ['data_proxy_MQTT', 'data_proxy_HTTP']
scripts_extension = '.py'

scripts_folder = "python_project/data_proxy/"
#scripts_folder = "python_project\\data_proxy\\" for Windows
processes = []
for script in scripts:
    process = subprocess.Popen(['python', scripts_folder+script+scripts_extension])
    processes.append(process)

for process in processes:
    process.wait()