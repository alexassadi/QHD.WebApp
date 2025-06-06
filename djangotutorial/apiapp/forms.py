from django import forms
from .models import Sentence

class SentenceGenerationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 51):
            self.fields[f'word_{i}'] = forms.CharField(
                required=False,
                label=f"{i}",
                widget=forms.TextInput(attrs={'style': 'width: 95%;'})
            )

    def clean(self):
        cleaned_data = super().clean()
        terms = [cleaned_data.get(f'word_{i}', '').strip() for i in range(1, 51) if cleaned_data.get(f'word_{i}', '').strip()]

        # Check all terms are unique
        if len(set(terms)) != len(terms):
            raise forms.ValidationError("Each word or term must be unique.")

        # Optionally: Spell check each word in each term
        from spellchecker import SpellChecker
        spell = SpellChecker()
        for term in terms:
            misspelled = [word for word in term.split() if word.lower() not in spell]
            if misspelled:
                raise forms.ValidationError(f"Term '{term}' contains spelling errors: {', '.join(misspelled)}")

        return cleaned_data

    def get_terms(self):
        return [self.cleaned_data[f'word_{i}'].strip() for i in range(1, 51) if self.cleaned_data.get(f'word_{i}', '').strip()]

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