import os
import subprocess
import requests
import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_and_print(statement,error=""):
    print(statement,error)
    with open('logs.txt', 'a', encoding='utf-8') as file:
        file.write(f"{statement}{error}\n")

def process(directory):
    for appointment in os.listdir(directory):
        file_path = os.path.join(directory, appointment)
        subprocess.run(["python", "transcribe_and_clean.py", file_path], check=True)

def is_connected():
    try:
        response = requests.head("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError or requests.Timeout:
        write_and_print("Your internet connection is down or extremely slow. Please fix your connection then rerun this script.")
        return False
    

write_and_print(f"\n\nProcessing script has been run at {now}")    
try:
    if is_connected():
        process("audio_files")
    else:
        input("Press enter to close this window when you are finished reading the error.")
except:
    input("Press enter to close this window when you are finished reading the error.")