from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Book
import requests
from .serializers import BookSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services.book_search_service import search_books
from .errors import *

@api_view(['GET'])
def search(request):
    keyword = (request.query_params.get("keyword") or "").strip()
    field = (request.query_params.get("field") or "title").strip().lower()
    page_size = request.query_params.get("page_size", '10')
    page = request.query_params.get("page_size", '1')
    try:
        search_results = search_books(keyword, field, page_size, page)
        return Response(search_results, status=status.HTTP_200_OK)
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

def create(request):
    pass

def review_list_and_create(request, book_id):
    pass

def galfy_list_and_create(request, book_id):
    pass
STATUS_MAP = {
    400: status.HTTP_400_BAD_REQUEST, 
    404: status.HTTP_404_NOT_FOUND,
    500: status.HTTP_500_INTERNAL_SERVER_ERROR,
    502: status.HTTP_502_BAD_GATEWAY,
    504: status.HTTP_504_GATEWAY_TIMEOUT,
}