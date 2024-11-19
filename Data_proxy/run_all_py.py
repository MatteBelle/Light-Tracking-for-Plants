# FILE USED BY SEPPIA
import subprocess

scripts = ['data_acquisition_proxy/main.py', 'data_analytics/main.py', 'data_analytics/run_predictions.py', 'telegram_bot.py']
processes = []
for script in scripts:
    process = subprocess.Popen(['python', script])
    processes.append(process)

for process in processes:
    process.wait()