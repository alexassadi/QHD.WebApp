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
    path('accounts/signup/', views.signup_view, name='signup'),
    path("initial_assessment/", views.initial_assessment, name="initial_assessment"),
    path("assessment_complete/", views.assessment_complete, name="assessment_complete"),
    path('register/', views.register, name='register'),
    path('edit-terms/', views.edit_terms, name='edit_terms'),
]
