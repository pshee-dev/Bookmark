from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('recommend/<int:review_id>/', views.recommend_book, name='recommend_book'),
]
