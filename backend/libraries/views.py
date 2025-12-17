from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import LibraryBookListSerializer, LibraryBookSerializer
from .models import Library

@api_view(['GET', 'POST'])
def library_book_list(request):
    # 내 서재 도서 목록 조회
    if request.method == 'GET':
        libraries = Library.objects.filter(user=request.user).select_related('book')
        serializer = LibraryBookListSerializer(libraries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 내 서재 독서 상태 등록
    elif request.method == 'POST':
        serializer = LibraryBookSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

@api_view(['PATCH', 'DELETE'])
def library_book(request, library_id):
    pass