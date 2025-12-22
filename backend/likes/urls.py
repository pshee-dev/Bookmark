from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    path('', views.like_toggle, name='like_toggle'),
]
