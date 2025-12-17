
from rest_framework.pagination import PageNumberPagination

class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 10                          # 기본 페이지 크기
    page_size_query_param = 'page_size'     # ?page_size=20 처럼 쿼리파라미터로 받는 것을 허용
    max_page_size = 50


