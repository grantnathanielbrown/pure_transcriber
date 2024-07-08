import openai
from openai import OpenAI
import sys
import os
import datetime
import shutil
import time

OAI_client = OpenAI()

start_time = time.perf_counter()
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_and_print(statement,error=""):
    print(statement,error)
    with open('logs.txt', 'a', encoding='utf-8') as file:
        file.write(f"{statement}\n{error}\n")

def read_error_handler(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        log_and_print(f"File not found: {filepath}. Please check the file path and try again.")
        raise
    except OSError as e:
        log_and_print(f"Error opening file {filepath}: ", e)
        raise

def write_error_handler(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        log_and_print(f"Error writing to file {filepath}: ", e)
        return False
    return True

def OAI_call(instructions,text_input,error_text,n_outputs=1,temperature=0): 
    try:
        completion = OAI_client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text_input},
            ],
            n=n_outputs,
            temperature=temperature
        )
        log_and_print(f"{error_text} API call was successful. prompt tokens: {completion.usage.prompt_tokens} \n completion tokens: {completion.usage.completion_tokens} \n total: {completion.usage.total_tokens}") 
        return completion
    except openai.BadRequestError as e:
        log_and_print(f"{error_text}: GPT-4: Invalid request, perhaps a problem with the file or parameters:", e)
    except openai.AuthenticationError as e:
        log_and_print(f"{error_text}: GPT-4: Authentication error", e)
    except openai.RateLimitError as e:
        log_and_print(f"{error_text}: GPT-4: Rate limit exceeded", e)
    except openai.APIStatusError as e:
        log_and_print(f"{error_text}: GPT-4: OpenAI's API status error: ", e)
    except Exception as e:  
        log_and_print(f"{error_text}: GPT-4: An unexpected error occurred:", e)

# might need to modify a bit if pathing is included in sys.argv[1]
filename = os.path.basename(sys.argv[1]).replace(".m4a","")
log_and_print(f"{filename} is being processed at {now}")
split_filename = filename.split(" ")
patient_name = f"{split_filename[0]} {split_filename[1]}"

date_string = split_filename[-1]
date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%d")
formatted_date_str = date_obj.strftime("%B %d, %Y")

log_and_print("Submitting audio file to Whisper for transcription")
try:
  audio_file = open(sys.argv[1], "rb")
  transcript = OAI_client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    response_format="text"
  )

except openai.BadRequestError as e:
    log_and_print("WHISPER: Invalid request, perhaps a problem with the file or parameters:", e)
    raise
except openai.AuthenticationError as e:
    log_and_print("WHISPER: Authentication error", e)
    raise
except openai.RateLimitError as e:
    log_and_print("WHISPER: Rate limit exceeded", e)
    raise
except openai.APIStatusError as e:
    log_and_print("GPT-4: OpenAI's API status error: ", e)
    raise
except Exception as e:  
    log_and_print("WHISPER: An unexpected error occurred:", e)
    raise

audio_file.close()
log_and_print("Audio file transcribed")

base_instructions = read_error_handler("base_instructions.txt")

MSE = read_error_handler("MSE.txt")

log_and_print("Submitting to GPT for polishing")

body_text = OAI_call(base_instructions,transcript,"body text").choices[0].message.content

log_and_print("No errors in the GPT4 calls")

summary_template = read_error_handler('summary_template.txt')

document_content = (
    summary_template
        .replace('{patient_name}', patient_name)
        .replace('{formatted_date_str}', formatted_date_str)
        .replace('{body_text}', body_text)
        .replace('{MSE}', MSE)
)

write_error_handler(f"test_transcripts/{filename}.txt", transcript)
write_error_handler(f"dictations/{filename}.txt", document_content)

try:
  shutil.copy2(sys.argv[1], f"transcribed_audio_files/{os.path.basename(sys.argv[1])}")
  os.remove(sys.argv[1])

except FileNotFoundError:
    log_and_print("The source file was not found")
    raise
except PermissionError:
    log_and_print("Permission denied while accessing the file or directory.")
    raise

end_time = time.perf_counter()
elapsed_time = end_time - start_time
elapsed_minutes,elapsed_seconds = divmod(elapsed_time,60)
log_and_print(f"Done processing {filename}!")
log_and_print(f"Elapsed time: {elapsed_minutes} minutes and {elapsed_seconds} seconds")