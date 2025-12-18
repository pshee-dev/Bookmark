from rest_framework import pagination
from rest_framework.pagination import PageNumberPagination

# 기본값을 설정한 페이지네이션 클래스
class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 10                          # 기본 페이지 크기
    page_size_query_param = 'page_size'     # ?page_size=20 처럼 쿼리파라미터로 받는 것을 허용
    max_page_size = 50 # 클라이언트가 그 이상을 요청하더라도 서버 측에서 이 값 초과해서 반환하지 않도록 하는 리밋.

# 페이지네이션 적용
def apply_pagination(request, queryset, sort_field, sort_direction='desc'):
    """
    페이지네이션을 적용하여 페이지 단위로 슬라이싱된 쿼리셋(page)과 페이지네이터를 반환합니다.
        - 반환된 페이지네이터를 이용하여 paginator.get_paginated_response(serializer.data)로 response 객체를 만들 수 있습니다.

    :param request: 요청 객체 | request 객체
    :param queryset: 정렬할 쿼리셋 | queryset 객체
    :param sort_field: 정렬 기준 필드 | str 타입
    :param sort_direction: 정렬방향 desc(기본값) / asc | str 타입
    :return: (page, paginator)
    """

    if sort_direction != 'asc': # 기본값: desc(내림차순)
        sort_field = f'-{sort_field}' # 정렬필드 앞에 -가 붙으면 내림차순으로 작동

    queryset = queryset.order_by(sort_field)
    paginator = DefaultPageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    return page, paginator


