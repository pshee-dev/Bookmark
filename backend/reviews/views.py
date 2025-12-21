from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN

from books.models import Book
from common.utils.paginations import apply_queryset_pagination
from .models import Review
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
)

@extend_schema(
    tags=["Reviews"],
    summary="리뷰 목록 조회 / 리뷰 작성",
    description="""
    특정 도서에 대한 리뷰 목록을 조회하거나,
    로그인 사용자가 리뷰를 작성합니다.

    ### 권한
    - GET: 비로그인 가능
    - POST: 로그인 필수
    """,
    parameters=[
        OpenApiParameter(
            name="sort-field",
            description="정렬 기준 (created_at | popularity)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="sort-direction",
            description="정렬 방향 (asc | desc)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="page",
            description="페이지 번호",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="page_size",
            description="페이지당 개수",
            required=False,
            type=int,
        ),
    ],
    request=ReviewCreateSerializer,
    responses={
        200: ReviewSerializer(many=True),
        201: ReviewSerializer,
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, book_id):
    """
    [Reviews] 리뷰 목록 조회 및 작성 API
    """

    # --------------------
    # POST: 리뷰 작성
    # --------------------
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

    # --------------------
    # GET: 리뷰 목록 조회
    # --------------------
    queryset = Review.objects.filter(book_id=book_id)

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    SORT_TYPE_MAP = {
        'popularity': 'popularity',
        'created_at': 'created_at',
    }

    sort_field = SORT_TYPE_MAP.get(sort_field, 'created_at')

    page, paginator = apply_queryset_pagination(
        request,
        queryset,
        sort_field,
        sort_direction
    )

    serializer = ReviewSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@extend_schema(
    tags=["Reviews"],
    summary="리뷰 상세 조회 / 수정 / 삭제",
    description="""
    특정 리뷰를 조회, 수정, 삭제합니다.

    ### 권한
    - GET: 비로그인 가능
    - PATCH / DELETE: 작성자만 가능
    """,
    request=ReviewUpdateSerializer,
    responses={
        200: ReviewSerializer,
        204: OpenApiResponse(description="삭제 완료"),
        403: OpenApiResponse(description="작성자 아님"),
        404: OpenApiResponse(description="리뷰 없음"),
    },
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def detail_and_update_and_delete(request, review_id):
    """
    [Reviews] 리뷰 상세 / 수정 / 삭제 API
    """

    review = get_object_or_404(Review, id=review_id)

    # --------------------
    # PATCH: 리뷰 수정
    # --------------------
    if request.method == 'PATCH':
        if not is_author(request, review):
            return Response(
                {
                    "error": {
                        "code": "invalid_user",
                        "message": "잘못된 접근입니다."
                    }
                },
                status=HTTP_403_FORBIDDEN
            )

        serializer = ReviewUpdateSerializer(
            review,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK
        )

    # --------------------
    # DELETE: 리뷰 삭제
    # --------------------
    if request.method == 'DELETE':
        if not is_author(request, review):
            return Response(
                {
                    "error": {
                        "code": "invalid_user",
                        "message": "잘못된 접근입니다."
                    }
                },
                status=HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # --------------------
    # GET: 리뷰 상세 조회
    # --------------------
    return Response(
        ReviewSerializer(review).data,
        status=status.HTTP_200_OK
    )

def is_author(request, review):
    """
    요청 유저가 리뷰 작성자인지 확인
    """
    return request.user == review.user

