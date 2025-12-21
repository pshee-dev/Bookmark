from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse, OpenApiExample,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN

from books.models import Book
from common.utils.paginations import apply_queryset_pagination
from .models import Galfy
from .serializers import (
    GalfyCreateSerializer,
    GalfySerializer,
    GalfyUpdateSerializer,
)


@extend_schema(
    tags=["Galfy"],
    summary="갈피 목록 조회 및 갈피 작성",

    description="""
    특정 도서에 대한 갈피(Galfy)를 조회하거나 생성합니다.

    ### 동작
    - **GET**
        - 특정 도서에 속한 갈피 목록을 조회합니다.
        - 정렬 및 페이지네이션을 지원합니다.
    - **POST**
        - 특정 도서에 갈피를 작성합니다.
        - 로그인 필수

    ### 권한
    - GET: 비로그인 가능
    - POST: 로그인 필수
    """,
    request=GalfyCreateSerializer,
    responses={
        200: GalfySerializer,
        201: GalfySerializer,
    },
    examples=[
        OpenApiExample(
            "갈피 생성 예",
            value={
                "page_number": "3",
                "content": "대유잼"
            },
            request_only=True
        )
    ]
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, book_id):
    """
    [Galfy] 갈피 목록 조회 / 갈피 생성 API
    """

    # ======================
    # POST: 갈피 생성
    # ======================
    if request.method == 'POST':
        book = get_object_or_404(Book, pk=book_id)

        serializer = GalfyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        galfy = serializer.save(
            user=request.user,
            book=book
        )

        return Response(
            GalfySerializer(galfy).data,
            status=status.HTTP_201_CREATED
        )

    # ======================
    # GET: 갈피 목록 조회
    # ======================
    queryset = Galfy.objects.filter(book_id=book_id)

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    SORT_TYPE_MAP = {
        'popularity': 'popularity',
        'created_at': 'created_at',
    }

    # 기본 정렬: created_at
    sort_field = SORT_TYPE_MAP.get(sort_field, 'created_at')

    page, paginator = apply_queryset_pagination(
        request,
        queryset,
        sort_field,
        sort_direction
    )

    serializer = GalfySerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["Galfy"],
    summary="갈피 상세 조회 / 수정 / 삭제",
    description="""
    단일 갈피(Galfy)에 대한 상세 조회, 수정, 삭제를 수행합니다.

    ### 동작
    - **GET**: 갈피 상세 조회
    - **PATCH**: 갈피 수정 (작성자만 가능)
    - **DELETE**: 갈피 삭제 (작성자만 가능)

    ### 권한
    - GET: 비로그인 가능
    - PATCH / DELETE: 로그인 + 작성자 본인
    """,
    request=GalfyUpdateSerializer,
    examples=[
        OpenApiExample(
            "갈피 수정 예",
            value={
                "page_number": "9",
                "content": "멍노잼"
            },
            request_only=True
        )
    ],
    responses={
        200: GalfySerializer,
        204: OpenApiResponse(description="삭제 성공"),
        403: OpenApiResponse(description="작성자 아님"),
        404: OpenApiResponse(description="갈피 없음"),
    }
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def detail_and_update_and_delete(request, galfy_id):
    """
    [Galfy] 갈피 상세 / 수정 / 삭제 API
    """

    galfy = get_object_or_404(Galfy, id=galfy_id)

    # ======================
    # PATCH: 갈피 수정
    # ======================
    if request.method == 'PATCH':
        if not is_author(request, galfy):
            return Response(
                {
                    "error": {
                        "code": "invalid_user",
                        "message": "잘못된 접근입니다."
                    }
                },
                status=HTTP_403_FORBIDDEN
            )

        serializer = GalfyUpdateSerializer(
            galfy,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            GalfySerializer(galfy).data,
            status=status.HTTP_200_OK
        )

    # ======================
    # DELETE: 갈피 삭제
    # ======================
    if request.method == 'DELETE':
        if not is_author(request, galfy):
            return Response(
                {
                    "error": {
                        "code": "invalid_user",
                        "message": "잘못된 접근입니다."
                    }
                },
                status=HTTP_403_FORBIDDEN
            )

        galfy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ======================
    # GET: 갈피 상세 조회
    # ======================
    return Response(
        GalfySerializer(galfy).data,
        status=status.HTTP_200_OK
    )


# ======================
# 공통 유틸
# ======================
def is_author(request, galfy):
    """
    요청 유저가 갈피 작성자인지 확인
    """
    return galfy.user == request.user
