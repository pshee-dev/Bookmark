from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import LibraryBookListSerializer, LibraryBookCreateSerializer, LibraryBookUpdateSerializer
from .models import Library

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def library_book_list(request):
    # 내 서재 도서 목록 조회
    if request.method == 'GET':
        libraries = Library.objects.filter(user=request.user).select_related('book')
        serializer = LibraryBookListSerializer(libraries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 독서 상태 등록
    elif request.method == 'POST':
        serializer = LibraryBookCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def library_book(request, library_id):
    # 현재 로그인된 유저의 library 객체에만 접근 가능하도록 설정하여 타 유저의 서재에 있는 도서에 대한 상세 조회/수정/삭제 접근을 막음
    library = get_object_or_404(Library, pk=library_id, user=request.user)

    # 독서 상태 상세 조회
    if request.method == 'GET':
        pass

    # 독서 상태 수정
    elif request.method == 'PATCH':
        serializer = LibraryBookUpdateSerializer(library, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # 독서 상태 삭제
    elif request.method == 'DELETE':
        library.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)