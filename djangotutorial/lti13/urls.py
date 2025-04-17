from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.lti13_login, name='lti13_login'),
    path('launch/', views.lti13_launch, name='lti13_launch'),
    path('.well-known/jwks.json', views.jwks_view, name='jwks'),
]
