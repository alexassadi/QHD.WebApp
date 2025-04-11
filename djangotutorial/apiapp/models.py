from django.db import models
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
    created_at = models.DateTimeField(auto_now_add=True)
    '''audio_url = models.CharField(max_length=255, blank=True, null=True)

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
'''