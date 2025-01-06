import sys
import subprocess
from data_proxy.configs import *
sys.path.append('/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Light-Tracking-for-Plants/python_project/')
scripts = ['data_proxy_HTTP', 'data_proxy_MQTT']
scripts_extension = '.py'

scripts_folder = "python_project/data_proxy/"
#scripts_folder = "python_project\\data_proxy\\" for Windows
processes = []
for script in scripts:
    process = subprocess.Popen(['python', scripts_folder+script+scripts_extension])
    processes.append(process)

for process in processes:
    process.wait()