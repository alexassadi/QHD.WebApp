import prompt
import openai
import re
from decouple import config
from master_prompt import MASTER_PROMPT, PROMPT_2

API_KEY = config('OPENAI_API_KEY')

# Read file and save as string

def get_sentences_prompt(first_half,second_half=None):
    # Set your API key
    response1 = send_and_get_prompt(first_half)

    if second_half != None:
        response2 = send_and_get_prompt(second_half)
        combined_response = response1 + "\n" + response2
        sentences = [s.strip() for s in combined_response.split('##') if '-' in s and len(s) > 40]
    else:
        sentences = [s.strip() for s in response1.split('##') if '-' in s and len(s) > 40]

    nested_sentences = []

    for item in sentences:
        # Use regex to split on the first " - [" pattern and preserve content
        match = re.match(r"^(.*?)\s*-\s*\[(.*)\]$", item.strip())
        if match:
            sentence = match.group(1).strip()
            phonemes = match.group(2).strip()  # Re-adding the brackets
            if len(sentence) > 30:
                nested_sentences.append([sentence, phonemes])
        else:
            print("Could not parse item:", item)  # Optional error logging

    # Print the resulting list
    return nested_sentences

def generate_sentences(vocab_list):
    first_half = vocab_list[:25]
    second_half = vocab_list[25:]

    nested_sentences = get_sentences_prompt(first_half, second_half)

    while nested_sentences < 50:
        temp_list = vocab_list

        for sentence in nested_sentences:
            for word in temp_list:
                if word.upper() in sentence[0]:
                    temp_list.remove(word)

        fix_reply = get_sentences_prompt(temp_list)

        for i in fix_reply:
            nested_sentences.append(i)

def send_and_get_prompt(payload):
    client = openai.OpenAI(api_key=API_KEY)

    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": PROMPT_2},
        {"role": "user", "content": prompt.generate_prompt(payload)},
    ]

    # Send first prompt
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_history,
        temperature=0.7,
        max_tokens=4096
    )

    # Print response
    reply = response.choices[0].message.content
    print(f"Raw response:\n {reply}")

    return reply