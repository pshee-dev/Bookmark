from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN
from books.models import Book
from common.utils.paginations import apply_queryset_pagination
from likes.models import Like
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer
from django.db.models import Count, OuterRef, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

# POST/PUT/PATCH/DELETE는 로그인 필수, GET은 로그인 없이 접근 가능
@extend_schema(
    methods=['GET'],
    parameters=[
        OpenApiParameter(name='book_id', type=int, location=OpenApiParameter.PATH),
        OpenApiParameter(name='mine', type=bool, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='sort-field', type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='sort-direction', type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY),
    ],
    responses=ReviewSerializer(many=True),
    tags=['Reviews'],
)
@extend_schema(
    methods=['POST'],
    request=ReviewCreateSerializer,
    responses=ReviewSerializer,
    tags=['Reviews'],
)
@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(['GET', 'POST'])
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

    # GET일 경우 리뷰 리스트 반환
    queryset = Review.objects.filter(book_id=book_id)
    mine = request.query_params.get('mine')
    if mine in ('true', 'True', '1'):
        if not request.user.is_authenticated:
            return Response({
                "error": {
                    "code": "requiresAuth",
                    "message": "Authentication required."
                }
            }, status=HTTP_403_FORBIDDEN)
        queryset = queryset.filter(user=request.user)
    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    # 정렬 기준 필드
    SORT_TYPE_MAP = {
        'popularity': 'popularity',
        'created_at': 'created_at',
    }

    sort_field = SORT_TYPE_MAP.get(sort_field, 'popularity')
    # TODO 페이지 사이즈 추가

    if sort_field == 'popularity':
        like_counts = Like.objects.filter(
            target_type=Like.TargetType.REVIEW,
            target_id=OuterRef('pk')
        ).values('target_id').annotate(
            c=Count('id')
        ).values('c')
        queryset = queryset.annotate(
            like_count=Coalesce(Subquery(like_counts, output_field=IntegerField()), Value(0))
        )
        sort_field = 'like_count'

    page, paginator = apply_queryset_pagination(request, queryset, sort_field, sort_direction)
    serializer = ReviewSerializer(page, many=True)

    response = paginator.get_paginated_response(serializer.data)
    response.data["page_size"] = len(page)
    return response


@extend_schema(
    methods=['GET'],
    parameters=[OpenApiParameter(name='review_id', type=int, location=OpenApiParameter.PATH)],
    responses=ReviewSerializer,
    tags=['Reviews'],
)
@extend_schema(
    methods=['PATCH'],
    request=ReviewUpdateSerializer,
    responses=ReviewSerializer,
    tags=['Reviews'],
)
@extend_schema(
    methods=['DELETE'],
    responses=OpenApiResponse(description='No response body.'),
    tags=['Reviews'],
)
@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(['GET', 'PATCH', 'DELETE'])
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
    elif request.method == 'DELETE':
        if not is_author(request, review):
            return Response({
                "error": {
                    "code": "invalid_user",
                    "message": "잘못된 접근입니다."
                }
            }, status=HTTP_403_FORBIDDEN)

        # 해당 리뷰에 달린 좋아요 기록도 함께 삭제
        Like.objects.filter( # 외래키 참조관계가 아니므로 역참조 불가
            target_type=Like.TargetType.REVIEW,
            target_id=review.id
        ).delete()

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if request.method == 'GET':
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK
        )

# 추후 커스텀 퍼미션으로 정의하는 방식으로 리팩토링 가능
def is_author(request, review):
    if review.user != request.user:
        return False
    return True

