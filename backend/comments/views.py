from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.response import Response

from galfies.models import Galfy
from reviews.models import Review
from common.utils import paginations
from .errors import InvalidTargetType, InvalidQuery, NotFoundError
from .models import TargetType, Comment
from .serializers import CommentSerializer, CommentCreateSerializer


@extend_schema(
    tags=["Comments"],
    summary="댓글 목록 조회 및 댓글 작성",
    description="""
    특정 게시글(리뷰 / 갈피)에 달린 댓글을 조회하거나 생성합니다.

    - target_type에 따라 리뷰 또는 갈피에 댓글이 달립니다.
    - GET: 댓글 목록 조회 (비로그인 가능)
    - POST: 댓글 작성 (로그인 필수)

    🔹 target_type
    - review : 리뷰 댓글
    - galfy  : 갈피 댓글
    """,
    parameters=[
        OpenApiParameter(
            name="target_type",
            description="댓글 대상 타입 (review | galfy)",
            required=True,
            type=str,
            location=OpenApiParameter.PATH,
        ),
        OpenApiParameter(
            name="sort-field",
            description="정렬 기준 필드 (created_at만 허용)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="sort-direction",
            description="정렬 방향 (asc | desc)",
            required=False,
            type=str,
        ),
    ],
    request=CommentCreateSerializer,
    examples=[
        OpenApiExample(
            name="댓글 생성 예시",
            value={"content": "이 부분 정말 공감돼요."},
            request_only=True,
        )
    ],
    responses={
        200: CommentSerializer,
        201: CommentSerializer,
        400: OpenApiResponse(description="잘못된 요청"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="대상 게시글 없음"),
    },
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, target_type, review_id=None, galfy_id=None):
    """
    [Comments] 댓글 목록 조회 / 댓글 생성 API
    """

    # -----------------------------------
    # 댓글 대상 판별 (Review / Galfy)
    # -----------------------------------
    if target_type == TargetType.REVIEW.value:
        target = get_object_or_404(Review, id=review_id)
        save_kwargs = {
            "user": request.user,
            "target_type": TargetType.REVIEW,
            "review": target,
        }

    elif target_type == TargetType.GALFY.value:
        target = get_object_or_404(Galfy, id=galfy_id)
        save_kwargs = {
            "user": request.user,
            "target_type": TargetType.GALFY,
            "galfy": target,
        }

    else:
        raise InvalidTargetType(
            dev_message="댓글이 달린 게시글 타입이 유효하지 않습니다."
        )

    # -----------------------------------
    # POST : 댓글 생성
    # -----------------------------------
    if request.method == 'POST':
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(**save_kwargs)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

    # -----------------------------------
    # GET : 댓글 목록 조회
    # -----------------------------------
    if target_type == TargetType.REVIEW.value:
        comments = Comment.objects.filter(
            review_id=review_id,
            target_type=target_type
        )
    elif target_type == TargetType.GALFY.value:
        comments = Comment.objects.filter(
            galfy_id=galfy_id,
            target_type=target_type
        )
    else:
        raise NotFoundError(
            dev_message="타겟 게시물을 찾을 수 없습니다."
        )

    # 정렬 파라미터
    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    if sort_field not in ('created_at',):
        raise InvalidQuery(
            dev_message="옳지 않은 sort_field 쿼리 파라미터가 전달되었습니다."
        )
    if sort_direction not in ('desc', 'asc'):
        raise InvalidQuery(
            dev_message="옳지 않은 sort_direction 쿼리 파라미터가 전달되었습니다."
        )

    page, paginator = paginations.apply_queryset_pagination(
        request,
        comments,
        sort_field,
        sort_direction
    )

    serializer = CommentSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["Comments"],
    summary="댓글 삭제",
    description="""
    댓글 작성자만 댓글을 삭제할 수 있습니다.

    - 로그인 필수
    - 작성자가 아닐 경우 403 반환
    """,
    responses={
        204: OpenApiResponse(description="댓글 삭제 성공"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="댓글 없음"),
    },
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def delete(request, comment_id):
    """
    [Comments] 댓글 삭제 API
    """

    comment = get_object_or_404(Comment, id=comment_id)

    if not is_author(request, comment):
        return Response(
            {
                "error": {
                    "code": "invalid_user",
                    "message": "잘못된 접근입니다."
                }
            },
            status=HTTP_403_FORBIDDEN
        )

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------
# 작성자 검증 헬퍼
# -----------------------------------
def is_author(request, comment):
    return comment.user == request.user
