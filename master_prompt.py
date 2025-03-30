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