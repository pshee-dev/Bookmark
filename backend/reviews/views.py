from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN
from books.models import Book
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer

# POST/PUT/PATCH/DELETE는 로그인 필수, GET은 로그인 없이 접근 가능
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


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def detail_and_update_and_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'PATCH':
        if not is_author(request, review):
            return Response({
                "error": {
                    "code": "invalid_user",
                    "message": "잘못된 접근입니다."
                }
            }, status=HTTP_403_FORBIDDEN)

        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK
        )

    if request.method == 'DELETE':
        if not is_author(request, review):
            return Response({
                "error": {
                    "code": "invalid_user",
                    "message": "잘못된 접근입니다."
                }
            }, status=HTTP_403_FORBIDDEN)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # GET일 경우
    return Response(
        ReviewSerializer(review).data,
        status=status.HTTP_200_OK
    )

# 추후 커스텀 퍼미션으로 정의하는 방식으로 리팩토링 가능
def is_author(request, review):
    if review.user != request.user:
        return False
    return True

