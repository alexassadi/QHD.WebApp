from django.contrib import admin
from .models import Sentence, PronunciationResult, Client, Profile

# Register your models here.
admin.site.register(Sentence)
admin.site.register(PronunciationResult)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'client')
    list_filter = ('client', 'is_admin')