from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_book_list),
    path('<int:library_id>/', views.library_book),
]
