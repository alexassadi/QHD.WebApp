from django.contrib import admin
from .models import Sentence, PronunciationResult

# Register your models here.
admin.site.register(Sentence)
admin.site.register(PronunciationResult)