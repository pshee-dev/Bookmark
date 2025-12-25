from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample

from .models import Book
from .serializers import BookSerializer, BookListSerializer, ISBNResolveSerializer
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
    키워드를 기반으로 외부 도서 API를 호출하여 검색 결과를 반환합니다.

    - 제목(title) 또는 저자(author) 기준 검색 가능
    - 페이지네이션을 지원하며, page / page_size를 통해 제어합니다.
    - 실제 DB 검색이 아닌 외부 API 기반 검색입니다.
    """,
    parameters=[
        OpenApiParameter(
            name="keyword",
            description="검색 키워드 (공백 가능, 없을 경우 빈 문자열로 처리)",
            required=False,
            type=str
        ),
        OpenApiParameter(
            name="field",
            description="검색 기준 필드 (title | author)",
            required=False,
            type=str
        ),
        OpenApiParameter(
            name="page",
            description="조회할 페이지 번호 (기본값: 1)",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="page_size",
            description="페이지당 결과 개수 (기본값: 10, 최대 40)",
            required=False,
            type=int
        ),
    ],
    responses={200: BookListSerializer}
)
@api_view(['GET'])
def search(request):
    """
    [Books] 도서 검색 API

    외부 도서 API를 통해 검색 결과를 조회합니다.
    DB에 저장되지 않은 도서도 검색 결과로 반환될 수 있습니다.
    """

    # 검색 키워드 (None 방지 → 항상 문자열)
    keyword = (request.query_params.get("keyword") or "").strip()

    # 검색 기준 필드 (기본값: title)
    field = (request.query_params.get("field") or "title").strip().lower()

    # 페이지 사이즈 (문자열로 들어오므로 내부에서 변환 처리)
    page_size = request.query_params.get("page_size", '10')

    # 페이지 번호
    page = request.query_params.get("page", '1')

    try:
        # 외부 API 검색 로직 호출
        search_results = search_books(keyword, field, page_size, page)

        # 리스트 전용 Serializer 사용
        return Response(
            BookListSerializer(search_results).data,
            status=status.HTTP_200_OK
        )

    except BookExceptionHandler as e:
        # 외부 API 오류 / 데이터 오류 등을 공통 포맷으로 변환
        return Response(
            {
                "error": {
                    "code": e.code,
                    "message": e.user_message,
                }
            },
            status=STATUS_MAP[e.http_status]
        )


@extend_schema(
    tags=["Books"],
    summary="Book detail",
    description="Retrieve book detail by id.",
    parameters=[
        OpenApiParameter(
            name="book_id",
            description="Book id",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        ),
    ],
    responses={200: BookSerializer},
)
@api_view(['GET'])
def detail(request, book_id):
    """
    [Books] 도서 상세 조회 API

    - book_id를 기준으로 DB에 저장된 도서 정보를 반환합니다.
    - 존재하지 않을 경우 404 반환
    """

    # DB에 존재하는 도서만 조회 가능
    book = get_object_or_404(Book, id=book_id)

    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Books"],
    summary="ISBN 기반 도서 확인 또는 생성",
    description="""
    ISBN을 기준으로 도서의 DB 존재 여부를 확인합니다.

    - 이미 존재하면 해당 도서 ID 반환 (200)
    - 존재하지 않으면 외부 API를 통해 도서 생성 후 ID 반환 (201)
    """,

    request=ISBNResolveSerializer,
    examples=[
        OpenApiExample(
            "ISBN Example",
            value={"isbn": "9791192742175"},
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=None,
            description="이미 존재하는 도서 → book_id 반환"
        ),
        201: OpenApiResponse(
            response=None,
            description="신규 도서 생성 → book_id 반환"
        )
    }
)
@api_view(['POST'])
def resolve_by_isbn(request):
    """
    [Books] ISBN 기반 도서 Resolve API

    검색 결과 중 하나를 선택했을 때,
    해당 도서가 DB에 존재하는지 확인하고 없으면 생성합니다.
    """

    raw_isbn = request.data.get("isbn")

    isbn = raw_isbn.strip() if raw_isbn else ""

    # ISBN 유효성 검사
    if not isbn:
        return Response(
            {
                "error": {
                    "code": "invalid_isbn",
                    "message": "현재 서비스 이용이 불가하오니, 나중에 다시 시도해 주세요."
                }
            },
            status=STATUS_MAP[400]
        )

    # ISBN으로 기존 도서 존재 여부 확인

    book = Book.objects.filter(isbn=isbn)

    # 이미 존재하는 경우 → 생성하지 않고 ID 반환
    if book.exists():
        return Response(
            {"book_id": book.get().id},
            status=status.HTTP_200_OK
        )

    # 존재하지 않는 경우 → 외부 API 호출 후 생성
    try:
        book_info = get_book_info_by_isbn(isbn)

    except BookExceptionHandler as e:
        return Response(
            {
                "error": {
                    "code": e.code,
                    "message": e.user_message,
                }
            },
            status=STATUS_MAP[e.http_status]
        )

    # Serializer를 통해 새 도서 생성
    serializer = BookSerializer(data=book_info)
    serializer.is_valid(raise_exception=True)

    book = serializer.save(category=book_info['category'])
    try:
        from recommendations.services.make_book_vector_pipeline_after_add_book import (
            enqueue_book_vector_build,
        )
        enqueue_book_vector_build(book.isbn)
    except Exception:
        pass

    return Response(
        {"book_id": book.pk},
        status=status.HTTP_201_CREATED
    )


