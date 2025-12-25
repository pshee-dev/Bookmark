from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('<int:review_id>/', views.recommend_book, name='recommend_book'),
]
