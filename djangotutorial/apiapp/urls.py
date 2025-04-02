from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_sentences, name='generate'),
    path('practice/', views.practice_view, name='practice'),
    path('reset_progress/', views.reset_progress, name='reset_progress'),
    path('completion/', views.completion_page, name='completion_page'),
    path('save-and-process-audio/', views.save_and_process_audio, name='save_and_process_audio'),
    path('generate-word-audio/', views.generate_word_audio, name='generate_word_audio'),
    path('debug/', views.debug_static, name='debug'),
]
