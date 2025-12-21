from django.urls import path
from . import views
from comments import views as comments_views

app_name = 'reviews'

urlpatterns = [
    path('<int:review_id>/comments/', comments_views.list_and_create, {'target_type': 'REVIEW'}, name='comments_list_and_create'),
    path('<int:review_id>/', views.detail_and_update_and_delete, name='detail_and_update_and_delete'),
]
