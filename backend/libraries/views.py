from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import LibraryBookListSerializer, LibraryBookCreateSerializer, LibraryBookUpdateSerializer, LibraryBookDetailSerializer
from .models import Library
from common.utils.paginations import apply_queryset_pagination


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def library_book_list(request):
    # 내 서재 도서 목록 조회
    if request.method == 'GET':
        # [status] status 파라미터에 의해 상태 필터링
        reading_status = request.query_params.get('status', Library.StatusEnum.reading.value)
        if reading_status not in Library.StatusEnum.values: 
            reading_status = Library.StatusEnum.reading.value
        libraries = Library.objects.filter(user=request.user, status=reading_status)
        
        # [sort] 정렬 관련 파라미터에 의해 쿼리셋 정렬
        '''
        request 값을 그대로 order_by에 사용할 경우 SQL Injection 공격에 취약함
        허용한 값에 한해서 존재 여부 확인 후 매핑하는 방식이 안전함
        => 화이트리스트 방식 (허용한 값만 사용하고, 나머지는 무시)
        '''
        # SORT_TYPE_MAP: 정렬 기준 매핑할 딕셔너리 생성
        SORT_TYPE_MAP = {
            'created_at': 'created_at',
            'start_date': 'start_date',
            'rating': 'rating',
            'title': 'book__title',
        }
        # sort_type: 정렬 기준
        sort_type = request.query_params.get('sort-type', 'created_at')
        sort_field = SORT_TYPE_MAP.get(sort_type, 'created_at')

        # sort_direction: 정렬 방향
        sort_direction = request.query_params.get('sort-direction', 'asc')
        
        # pagination 적용
        page, paginator = apply_queryset_pagination(request, libraries, sort_field, sort_direction, 'limit')
        serializer = LibraryBookListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


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
        serializer = LibraryBookDetailSerializer(library)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
