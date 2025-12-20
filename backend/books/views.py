from django.shortcuts import get_object_or_404
from .models import Book
from .serializers import BookSerializer, BookListSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .services.book_search_service import search_books
from .errors import *

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

@api_view(['GET'])
def detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def resolve_by_isbn(request):
    """
    검색된 책 리스트 중 하나를 선택 시, 해당 요소 isbn 정보로 db 내 존재여부를 확인한 후 \n
    - a. db에 해당 도서 존재 시 -> 해당도서 상세정보 반환 \n
    - b. db에 해당 도서 부재 시 -> 생성 후 해당도서 상세정보 반환 \n
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
    if book: 
        serializer = BookSerializer(book.get())
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    '''# 책 정보가 db에 저장되어있지 않을 경우 새로 생성
    try:
        book_info = fetch_aladin_info_by_isbn(isbn) 
    except BookExceptionHandler as e :
        return Response({
            "error": {
                "code": e.code,
                "message": e.user_message,
            }
        }, status=STATUS_MAP[e.http_status])
        
    serializer = BookSerializer(data=book_info)
    
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)'''

STATUS_MAP = {
    400: status.HTTP_400_BAD_REQUEST, 
    404: status.HTTP_404_NOT_FOUND,
    500: status.HTTP_500_INTERNAL_SERVER_ERROR,
    502: status.HTTP_502_BAD_GATEWAY,
    504: status.HTTP_504_GATEWAY_TIMEOUT,
}
