from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from books.models import Book
from .serializers import ReviewCreateSerializer, ReviewSerializer

# POST/PUT/DELETE는 로그인 필수, GET은 로그인 없이 접근 가능
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = serializer.save(
            user=request.user,
            book=book
        )
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED
        )
    return None #TODO get메서드일때의 리스트 반환 로직 추가
