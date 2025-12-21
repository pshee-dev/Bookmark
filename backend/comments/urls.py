from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comments/<int:target_id>/', views.delete, name='delete'),
]
