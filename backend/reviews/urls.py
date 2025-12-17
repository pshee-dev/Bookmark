from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:review_id>/', views.detail_and_update_and_delete, name='detail_and_update_and_delete'),
]
