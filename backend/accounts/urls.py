from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.get_global_feed),
    path('profile/', views.profile_by_username),
    path('<int:user_id>/follow/', views.follow),
    path('<int:user_id>/followings/', views.get_following_list),
    path('<int:user_id>/followers/', views.get_follower_list),
    path('<int:user_id>/reviews/', views.get_review_list),
    path('<int:user_id>/galfies/', views.get_galfy_list),
    path('<int:user_id>/feed/', views.get_feed),
    path('<int:user_id>/', views.profile),
]
