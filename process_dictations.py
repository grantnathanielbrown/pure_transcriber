import os
import subprocess
import requests
import datetime
import platform

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_and_print(statement,error=""):
    print(statement,error)
    with open('logs.txt', 'a', encoding='utf-8') as file:
        file.write(f"{statement}{error}\n")

def convert_audio_files(directory):
    for audio_file in os.listdir(directory):
        if audio_file == '.DS_Store':
            continue
        file_path = os.path.join(directory, audio_file)
        if '.mp3' not in file_path:
            output_file = os.path.splitext(file_path)[0] + '.mp3'
            ffmpeg_command = ['ffmpeg', '-i', file_path, '-vn', '-acodec', 'mp3', '-ab', '40k', output_file]

            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError:
                write_and_print(f"Error converting file {audio_file} with ffmpeg")
                continue
            # Delete the original file
            try:
                os.remove(file_path)
            except OSError as e:
                write_and_print(f"Error deleting original file {audio_file} after converting into .mp3:", e)
                continue

            write_and_print(f"Successfully converted {audio_file} into an .mp3 and deleted original")

def process(directory):
    for appointment in os.listdir(directory):
        if appointment == '.DS_Store':
            continue
        file_path = os.path.join(directory, appointment)
        # if this is running on a mac
        if platform.system() == "Darwin":
            subprocess.run(["python3", "transcribe_and_clean.py", file_path], check=True)
        else:
            subprocess.run(["python", "transcribe_and_clean.py", file_path], check=True)

def is_connected():
    try:
        response = requests.head("http://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError or requests.Timeout:
        write_and_print("Your internet connection is down or extremely slow. Please fix your connection then rerun this script.")
        return False

def git_push_logs():
    try:
        subprocess.run(["git", "add", "logs.txt"], check=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Update logs: {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "--force"], check=True)
        print("Successfully pushed logs to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pushing to GitHub: {e}")

write_and_print(f"\n\nProcessing script has been run at {now}")    
try:
    if is_connected():
        convert_audio_files("audio_files")
        process("audio_files")
        git_push_logs()
    else:
        input("Press enter to close this window when you are finished reading the error.")
except:
    input("Press enter to close this window when you are finished reading the error.")