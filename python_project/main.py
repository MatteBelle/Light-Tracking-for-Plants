import subprocess
from data_proxy.configs import *


scripts = ['data_proxy_MQTT', 'data_proxy_HTTP']
scripts_extension = '.py'
scripts_folder = "python_project/data_proxy/"
processes = []
for script in scripts:
    process = subprocess.Popen(['python', scripts_folder+script+scripts_extension])
    processes.append(process)

for process in processes:
    process.wait()

# # WINDOWS

# if __name__ == "__main__":
#     scripts = ['data_proxy_MQTT', 'data_proxy_HTTP']
#     scripts_extension = '.py'
#     scripts_folder = "Data_proxy\\"
#     processes = []
#     # if log folder does not exist, create it
#     if not os.path.exists("logs"):
#         os.makedirs("logs")
#     for script in scripts:
#         try:
#             # creating log files to store outputs and errors of each script
#             with open(f"logs/{script}.log", "w") as log_file:
#                 process = subprocess.Popen(['python', script+scripts_extension], stdout=log_file, stderr=subprocess.STDOUT)
#                 processes.append(process)
#         except Exception as e:
#             print(f"Error launching {script}: {e}")

#     for process in processes:
#         process.wait()