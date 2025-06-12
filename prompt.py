def generate_prompt(payload):

    vocab_list = ','.join(payload)

    return f"""Vocabulary list: {vocab_list}
There are {len(vocab_list)} terms in the list.
Use the terms in the list to generate the sentences described in the previous prompt.
I want the sentences formatted as one long continuous text as I will split it myself programmatically so the format you provide the sentences in is crucial. Follow the format seen below:
sentence - phonemes of sentence ## sentence - phonemes of key word
"""