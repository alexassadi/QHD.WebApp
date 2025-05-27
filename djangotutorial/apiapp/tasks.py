from django_q.tasks import async_task
from apiapp.models import Sentence
from django.contrib.auth import get_user_model
import openai_func as oa

User = get_user_model()

def generate_sentences_task(vocab_list, user_id):
    user = User.objects.get(id=user_id)
    sentences = oa.initial_prompt(vocab_list)

    for sentence in sentences:
        print("SAVING:", sentence)  # Debug print

        if isinstance(sentence, list) and len(sentence) == 2:
            Sentence.objects.create(
                text=sentence[0],
                phonemes=sentence[1],
                user=user
            )
        else:
            print("⚠️ Malformed sentence:", sentence)

    return "done"
