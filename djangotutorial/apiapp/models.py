from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
import sys
import uuid

# Add the utilities folder (2 levels up) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import elevenlabs_func as el
import s3_func as s3

class Sentence(models.Model):
    text = models.TextField()
    phonemes = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_url = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.text  # Display part of the sentence in the admin panel
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate audio on creation
            # Generate audio file from text
            audio_binary = el.generate_audio_file(self.text)

            # Upload to S3
            key = f"audio/fluent_audio/fluent_{uuid.uuid4().hex}.mp3"
            fluent_audio_url = s3.export_result_to_s3(key, audio_binary, 'audio/mpeg')
            self.audio_url = fluent_audio_url

        super().save(*args, **kwargs)

class Word(models.Model):
    word = models.CharField(max_length=100, unique=False)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_url = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = self.word.lower()
        # Prevent duplicate word entries
        if not self.pk:
            existing = Word.objects.filter(word__iexact=self.word).first()
            if existing:
                # Copy the existing audio_url from the found instance
                self.audio_url = existing.audio_url
            else:
                # Generate audio and upload
                audio_binary = el.generate_audio_file(f'''"Listen carefully to the word" <break time="1s" /> "{self.word}" <break time="1s" /> "now listen to the word again" <break time="1s" /> "{self.word}"''')
                key = f"audio/word_audio/word_{uuid.uuid4().hex}.mp3"
                word_audio_url = s3.export_result_to_s3(key, audio_binary, 'audio/mpeg')
                self.audio_url = word_audio_url

        super().save(*args, **kwargs)

class PronunciationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sentence = models.ForeignKey('Sentence', on_delete=models.CASCADE)
    score = models.IntegerField()
    expected_text = models.TextField()  # ✅ New field
    word_scores = models.JSONField()
    phoneme_scores = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)