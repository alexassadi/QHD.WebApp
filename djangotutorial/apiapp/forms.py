from django import forms
from .models import Sentence, Client, Profile
from django.contrib.auth.models import User

class SentenceGenerationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 51):
            self.fields[f'word_{i}'] = forms.CharField(
                required=False,
                label=f"{i}",
                widget=forms.TextInput(attrs={'class': 'term-input'})
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

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    client_id = forms.CharField(label="Client ID", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_client_id(self):
        client_id = self.cleaned_data['client_id'] 
        try:
            client = Client.objects.get(name=client_id)  # match must be exact
        except Client.DoesNotExist:
            raise forms.ValidationError("❌ The client ID you entered does not exist.")
        return client

    def save(self, commit=True):
        client = self.clean_client_id()
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            Profile.objects.create(user=user, client=client, is_admin=False)

        return user
    
class EditTermsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(1, 51):
            self.fields[f'word_{i}'] = forms.CharField(
                required=True,
                max_length=50,
                widget=forms.TextInput(attrs={
                    'class': 'term-input',
                })
            )
