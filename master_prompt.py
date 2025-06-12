MASTER_PROMPT = '''Context:
This prompt is for generating sentences designed to improve the pronunciation and fluency of call centre staff. The generated sentences will be recorded by staff, and these recordings will be processed by an AI system to assess pronunciation and fluency.

Instructions:
Term Usage:

Each sentence must include one term from the list provided directly in the sub-prompt (terms will be separated by commas).
Each term must be used once in its own sentence.
The term should appear in capitals where it occurs naturally within the sentence, rather than at the beginning.
Sentences must start with the term provided first in the sub-prompt list and proceed in the same order as the list.
Sentence Quantity:

The number of sentences will be specified in the sub-prompt as [sentence number].
If the specified number of sentences is fewer than the number of terms in the vocabulary list, the number of sentences must equal the number of terms to ensure each one is used at least once.
If the requested number of sentences exceeds the number of terms in the vocabulary list, the number of sentences should be limited to the vocabulary list's count.
Sentence Order:

Sentences must be generated in the same order as the terms appear in the sub-prompt.
Language Level:

Sentences should align with CEFR B2 language standards.
The CEFR level does not apply to the terms themselves; the vocabulary list may include words from different levels.
Relevance, Authenticity, and Context:

Sentences should be relevant to call centre staff and align with realistic workplace scenarios.
Each sentence must contain a different context and language from any other sentence.
Sentences should reflect authentic things a call centre agent would say to a customer, using realistic language and instructions that align with typical customer interactions.
No subject is required in the sub-prompt. The generated sentences should be created based solely on the provided list of terms.
Formatting:

Each term should appear in capitals and only where it occurs naturally in the sentence.'''

PROMPT_2 = '''Context:
This prompt is for generating sentences designed to improve the pronunciation and fluency of call centre staff. The generated sentences will be recorded by staff, and these recordings will be processed by an AI system to assess pronunciation and fluency.
⸻
Instructions:
1. Term Usage:
• Each sentence must include one term from the list provided directly in the sub-prompt.
• Throughout the entire series of sentences, each term must be used once in its own sentence.
• The term should appear where it occurs naturally within the sentence.
• The term should appear in CAPITALS.
2. Phoneme Coverage:
• The generated 25 sentences should be designed to include all phonemes in the IPA system (vowels, pulmonic consonants, and non-pulmonic consonants) in natural language contexts.
• Phonemes should appear in their most usual positions within realistic and relevant sentences.
• Sentences should reflect natural rhythm, intonation, and connected speech patterns to model authentic English speech.
• Each phoneme must appear 10 times across the full series of sentences to ensure adequate repetition for learning.
3. Sentence Quantity:
• The minimum number of sentences generated must always be 25. I repeat, ALWAYS PRODUCE 25 SENTENCES IN ONE RESPONSE
• If the number of items in the vocabulary list is fewer than 25, the remaining sentences should be generated using words that are semantically similar to those in the vocabulary list.
4. Sentence Order:
• Sentences must be generated in the same order within the overall series as the terms appear in the list uploaded in a sub-prompt.
5. Language Level:
• Sentences should align with CEFR B2 language standards.
• The CEFR level does not apply to the terms themselves; the vocabulary list may include words from different levels.
6. Relevance, Authenticity, and Context:
• Sentences should be relevant to call centre staff and align with realistic workplace scenarios.
• Each sentence must contain a different context and language from any other sentence.
• Sentences should reflect authentic things a call centre agent would say to a customer, using realistic language and instructions that align with typical customer interactions.
• Each term should appear naturally in the sentence and in CAPITALS.
7. Phoneme Metadata:
For each generated sentence, provide an accompanying phonetic version with each word shown as its constituent phonemes according to the IPA standard.
• Each phoneme ‘spelt’ word must have a space between each character.
• The standard word should appear normally without added spaces.
• Example:
• Insurance → [ɪ n ʃ ʊ r ə n s]
8. Formatting:
I want the sentences formatted as one long continuous text as I will split it myself programmatically so the format you provide the sentences in is crucial. Follow the format seen below:
sentence - phonemes of sentence ## sentence - phonemes of sentence'''