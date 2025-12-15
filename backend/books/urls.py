from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('<int:book_id>/reviews/', views.review_list_and_create, name='reviews'),
    path('<int:book_id>/galfies/', views.galfy_list_and_create, name='galfies'),
    path('<int:book_id>/', views.detail, name='detail'),
    path('', views.create, name='create'),
]
