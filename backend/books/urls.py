from django.urls import path
from . import views
from reviews.views import list_and_create as review_list_and_create
from galfies.views import list_and_create as galfy_list_and_create


app_name = 'books'

urlpatterns = [
    # isbn으로 db 내 도서 존재여부 확인하여 없으면 생성 후 상세정보 반환
    path('resolve/', views.resolve_by_isbn, name='resolve'),
    path('search/', views.search, name='search'),
    path('<int:book_id>/reviews/', review_list_and_create, name='review_list_and_create'),
    path('<int:book_id>/galfies/', galfy_list_and_create, name='galfy_list_and_create'),
    path('<int:book_id>/', views.detail, name='detail'),
]
