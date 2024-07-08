import openai
from openai import OpenAI
import sys
import os
from datetime import datetime
from collections import Counter

OAI_client = OpenAI()

def read_error_handler(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}. Please check the file path and try again.")
        raise
    except OSError as e:
        print(f"Error opening file {filepath}: ", e)
        raise

def write_error_handler(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        print(f"Error writing to file {filepath}: ", e)
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
        print(f"API call was successful. prompt tokens: {completion.usage.prompt_tokens} \n completion tokens: {completion.usage.completion_tokens} \n total: {completion.usage.total_tokens}") 
        return completion
    except openai.BadRequestError as e:
        print(f"{error_text}: GPT-4: Invalid request, perhaps a problem with the file or parameters:", e)
    except openai.AuthenticationError as e:
        print(f"{error_text}: GPT-4: Authentication error", e)
    except openai.RateLimitError as e:
        print(f"{error_text}: GPT-4: Rate limit exceeded", e)
    except openai.APIStatusError as e:
        print(f"{error_text}: GPT-4: OpenAI's API status error: ", e)
    except Exception as e:  
        print(f"{error_text}: GPT-4: An unexpected error occurred:", e)
    
# might need to modify a bit if pathing is included in sys.argv[1]
filename = os.path.basename(sys.argv[1]).replace(".txt","")
print(f"Processing {filename}...")
split_filename = filename.split(" ")
patient_name = f"{split_filename[0]} {split_filename[1]}"

date_string = split_filename[-1]
date_obj = datetime.strptime(date_string, "%Y-%m-%d")
formatted_date_str = date_obj.strftime("%B %d, %Y")

base_instructions = read_error_handler("base_instructions.txt")

# MSE = read_error_handler("MSE.txt")
transcript = read_error_handler(sys.argv[1])
choices = OAI_call(base_instructions,transcript,"body text",10).choices
print(choices)
# summary_template = read_error_handler('summary_template.txt')

# document_content = (
#     summary_template
#     .replace('{patient_name}', patient_name)
#     .replace('{formatted_date_str}', formatted_date_str)
#     .replace('{body_text}', body_text)
#     .replace('{MSE}', MSE)
# )
for index, choice in enumerate(choices):

    write_error_handler(f"test_outputs/test{index}.txt", choice.message.content)