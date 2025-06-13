from django_q.tasks import async_task
from apiapp.models import Sentence, Term
from django.contrib.auth import get_user_model
import openai_func as oa

User = get_user_model()

def generate_sentences_task(vocab_list, user_id, client, hook=None):
    user = User.objects.get(id=user_id)

    terms = Term.objects.filter(client=client).order_by('position')
    vocab_list = [t.term for t in terms]

    sentences = oa.generate_sentences(vocab_list)

    for sentence in sentences:
        print("SAVING:", sentence)  # Debug print

        if isinstance(sentence, list) and len(sentence) == 2:
            Sentence.objects.create(
                text=sentence[0],
                client=client,
                phonemes=sentence[1],
                user=user
            )
        else:
            print("⚠️ Malformed sentence:", sentence)

    return "done"
