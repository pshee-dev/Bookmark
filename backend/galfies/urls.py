from django.urls import path
from . import views
from comments import views as comments_views

app_name = 'galfies'

urlpatterns = [
    path('<int:galfy_id>/comments/', comments_views.list_and_create, {'target_type': 'GALFY'}, name='comments_list_and_create'),
    path('<int:galfy_id>/', views.detail_and_update_and_delete, name='detail_and_update_and_delete'),
]
