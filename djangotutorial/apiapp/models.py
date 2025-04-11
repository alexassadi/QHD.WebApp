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