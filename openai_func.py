import prompt
import openai
import re
from decouple import config
from master_prompt import MASTER_PROMPT

API_KEY = config('OPENAI_API_KEY')

# Read file and save as string

def initial_prompt(vocab_list, quantity):
    # Set your API key
    client = openai.OpenAI(api_key=API_KEY)

    # Initialize conversation history
    conversation_history = [
        {"role": "system", "content": MASTER_PROMPT},
        {"role": "user", "content": prompt.generate_prompt(vocab_list,quantity)},
    ]

    # Send first prompt
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_history
    )

    # Print response
    reply = response.choices[0].message.content

    # Use regex to split at the numbers followed by a period and a space
    sentences = [x[:-1].replace('\n','') for x in re.split(r'\d+\.\s', reply)[1:]]  # [1:] removes the first empty element

    # Print the resulting list
    return sentences