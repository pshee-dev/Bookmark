from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Book
from .serializers import BookSerializer, BookListSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .services.book_search_service import search_books, get_book_info_by_isbn
from .errors import *

STATUS_MAP = {
    400: status.HTTP_400_BAD_REQUEST,
    404: status.HTTP_404_NOT_FOUND,
    500: status.HTTP_500_INTERNAL_SERVER_ERROR,
    502: status.HTTP_502_BAD_GATEWAY,
    504: status.HTTP_504_GATEWAY_TIMEOUT,
}

@extend_schema(
    tags=["Books"],
    summary="도서 검색",
    description="""
    키워드 기반으로 도서를 검색합니다.

    - 제목(title) 또는 저자(author) 기준 검색 가능
    - 외부 도서 API를 통해 검색된 결과를 페이지네이션 형태로 반환합니다.

    ### 동작 방식
    1. keyword, field, page_size, page 값을 쿼리 파라미터로 받습니다.
    2. 내부에서 외부 도서 API를 호출합니다.
    3. 검색 결과를 리스트 형태로 반환합니다.

    ### 예외 처리
    - 외부 API 오류
    - 잘못된 검색 조건
    """,
)
@api_view(['GET'])
def search(request):
    keyword = (request.query_params.get("keyword") or "").strip()
    field = (request.query_params.get("field") or "title").strip().lower() # title or author
    page_size = request.query_params.get("page_size", '10') # 기본값 10, 최대값 40. 1미만/40초과 시 1/최대값으로 대체.
    page = request.query_params.get("page", '1') # 기본값 1. 입력값이 1 미만일 시, 기본값으로 대체.
    try:
        search_results = search_books(keyword, field, page_size, page)
        return Response(BookListSerializer(search_results).data, status=status.HTTP_200_OK)
    except BookExceptionHandler as e:
        return Response({
            "error": {
                "code": e.code,
                "message": e.user_message,
            }
        }, status=STATUS_MAP[e.http_status])

@extend_schema(
    tags=["Books"],
    summary="도서 상세 조회",
    description="""
    특정 도서의 상세 정보를 조회합니다.

    - 내부 DB에 저장된 도서만 조회 가능
    - 존재하지 않는 경우 404 반환
    """,
)
@api_view(['GET'])
def detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Books"],
    summary="ISBN 기반 도서 조회 또는 생성",
    description="""
    ISBN을 기준으로 도서의 DB 존재 여부를 확인합니다.

    ### 동작 시나리오
    1. 요청으로 전달된 ISBN을 기준으로 DB 조회
    2. 이미 존재하는 경우
       → 해당 도서의 ID를 반환 (200 OK)
    3. 존재하지 않는 경우
       → 외부 API를 통해 도서 정보 조회
       → DB에 신규 생성 후 ID 반환 (201 Created)

    ### 사용 목적
    - 검색 결과에서 특정 도서를 선택했을 때
    - 프론트엔드에서 도서 상세 페이지로 이동하기 위한 ID 확보
    """,
)
@api_view(['GET','POST'])
def resolve_by_isbn(request):
    """
    검색된 책 리스트 중 하나를 선택 시, 해당 요소 isbn 정보로 db 내 존재여부를 확인한 후 \n
    - a. db에 해당 도서 존재 시 -> 해당도서 id와 함께 200 반환 \n
    - b. db에 해당 도서 부재 시 -> 생성 후 해당도서 id와 함께 201 반환
    (프론트에서 해당 id를 참고하여 해당 도서 상세정보 url로 이동시키기 위한 정보 제공)
    """
    raw_isbn = request.data.get("isbn")
    isbn = raw_isbn.strip()
    if not isbn:
        return Response({
            "error": {
                "code": "invalid_isbn",
                "message": "현재 서비스 이용이 불가하오니, 나중에 다시 시도해 주세요."
            }
        }, status=STATUS_MAP[400])
    book = Book.objects.filter(isbn=isbn)
    #TODO 동일 도서이지만 제목이 조금씩 달라, isbn이 다른 똑같은 책이 여러 권 생성되는 문제에 대해 고민해보기
    if book: 
        return Response({'book_id': book.get().id}, status=status.HTTP_200_OK)
    
    # 책 정보가 db에 저장되어있지 않을 경우 새로 생성
    try:
        book_info = get_book_info_by_isbn(isbn, status=status.HTTP_200_OK)
    except BookExceptionHandler as e :
        return Response({
            "error": {
                "code": e.code,
                "message": e.user_message,
            }
        }, status=STATUS_MAP[e.http_status])
    serializer = BookSerializer(data=book_info)
    if serializer.is_valid(raise_exception=True):
        book = serializer.save(category=book_info['category'])
    return Response(book.pk, status=status.HTTP_201_CREATED)

