from django.shortcuts import render
from .models import Book
from .serializers import BookSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data)

def create(request):
    pass

def review_list_and_create(request, book_id):
    pass

def galfy_list_and_create(request, book_id):
    pass
