import prompt
import openai
import re
from decouple import config
from master_prompt import MASTER_PROMPT, PROMPT_2

API_KEY = config('OPENAI_API_KEY')

# Read file and save as string

def initial_prompt(vocab_list):
    # Set your API key
    client = openai.OpenAI(api_key=API_KEY)

    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": PROMPT_2},
        {"role": "user", "content": prompt.generate_prompt(vocab_list)},
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

    sentences = [s.strip() for s in reply.split('##') if '-' in s and len(s) > 40]

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