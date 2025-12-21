from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

# 기본값을 설정한 페이지네이션 클래스
class DefaultPageNumberPagination(PageNumberPagination):
    page_size = 10                          # 기본 페이지 크기
    page_size_query_param = 'page_size'     # ?page_size=20 처럼 쿼리파라미터로 받는 것을 허용
    max_page_size = 50 # 클라이언트가 그 이상을 요청하더라도 서버 측에서 이 값 초과해서 반환하지 않도록 하는 리밋.


# 기본값 리밋오프셋페이지네이션 클래스
class DefaultLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'


# 쿼리셋 페이지네이션 적용
def apply_queryset_pagination(request, queryset, sort_field, sort_direction='desc', type='page'):
    """
    페이지네이션을 적용하여 페이지 단위로 슬라이싱된 쿼리셋(page)과 페이지네이터를 반환합니다.
        - 반환된 페이지네이터를 이용하여 paginator.get_paginated_response(serializer.data)로 response 객체를 만들 수 있습니다.

    :param request: 요청 객체 | request 객체
    :param queryset: 정렬할 쿼리셋 | queryset 객체
    :param sort_field: 정렬 기준 필드 | str 타입
    :param sort_direction: 정렬방향 desc(기본값) / asc | str 타입
    :param type: 사용할 페이지네이션 종류 page(기본값) / limit | str 타입
    :return: (page, paginator)
    """

    # 사용할 페이지네이션 종류 선택 (기본값: page)
    if type == 'page':
        paginator = DefaultPageNumberPagination()
    elif type == 'limit':
        paginator = DefaultLimitOffsetPagination()


    if sort_direction != 'asc': # 기본값: desc(내림차순)
        sort_field = f'-{sort_field}' # 정렬필드 앞에 -가 붙으면 내림차순으로 작동

    queryset = queryset.order_by(sort_field)
    page = paginator.paginate_queryset(queryset, request)
    return page, paginator

# 리스트 페이지네이션 적용
def apply_list_pagination(request, ls, type='page'):
    """
    페이지네이션을 적용하여 페이지 단위로 슬라이싱된 쿼리셋(page)과 페이지네이터를 반환합니다.
        - 정렬을 제공하지 않습니다. (쿼리셋이 아니기 때문)
        - 반환된 페이지네이터를 이용하여 paginator.get_paginated_response(serializer.data)로 response 객체를 만들 수 있습니다.

    :param request: 요청 객체 | request 객체
    :param ls: 페이지네이션 적용할 리스트 | queryset 객체
    :param type: 사용할 페이지네이션 종류 page(기본값) / limit | str 타입
    :return: (page, paginator)
    """

    # 사용할 페이지네이션 종류 선택 (기본값: page)
    if type == 'page':
        paginator = DefaultPageNumberPagination()
    elif type == 'limit':
        paginator = DefaultLimitOffsetPagination()

    page = paginator.paginate_queryset(ls, request)
    return page, paginator
