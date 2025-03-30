from django import forms
from .models import Sentence

class SentenceGenerationForm(forms.Form):
    sentence_number = forms.CharField(label='Number of senteces', widget=forms.Textarea, required=True)
    vocab_list = forms.CharField(label='Vocabulary list', widget=forms.Textarea, required=True)
    

class PronunciationForm(forms.Form):

    sentence = forms.ModelChoiceField(
        queryset=Sentence.objects.all(),
        empty_label="Select a sentence",
        label="Choose a Sentence"
    )

    speaker_gender = forms.ChoiceField(
        choices=[
            ('male', 'Male'),
            ('female', 'Female')
        ],
        required=False,  # ✅ No longer required during sentence selection
        label="Speaker Gender"
    )
    
    audio_file = forms.CharField(
        widget=forms.HiddenInput(),
        required=False  # ✅ No longer required during sentence selection
    )

class PracticeForm(forms.Form):

    audio_file = forms.CharField(
        widget=forms.HiddenInput(),
        required=False  # ✅ No longer required during sentence selection
    )