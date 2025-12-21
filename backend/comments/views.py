from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_403_FORBIDDEN

from galfies.models import Galfy
from reviews.models import Review
from common.utils import paginations
from .errors import InvalidTargetType, InvalidQuery, NotFoundError
from .models import TargetType, Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from rest_framework.response import Response

# POST/PUT/PATCH/DELETE는 로그인 필수, GET은 로그인 없이 접근 가능
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, target_type, review_id=None, galfy_id=None):
    if target_type == TargetType.REVIEW.value:
        model = Review
        target = get_object_or_404(model, id=review_id)
        save_kwargs = {
            "user": request.user,
            "target_type": TargetType.REVIEW,
            "review": target,
        }
    elif target_type == TargetType.GALFY.value:
        model = Galfy
        target = get_object_or_404(model, id=galfy_id)
        save_kwargs = {
            "user": request.user,
            "target_type": TargetType.GALFY,
            "galfy": target,
        }
    else:
        raise InvalidTargetType(
            dev_message="댓글이 달린 게시글 타입이 유효하지 않습니다."
        )
    if request.method == 'POST':
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            created_Comment = serializer.save(**save_kwargs)
            return Response(CommentSerializer(created_Comment).data, status=status.HTTP_201_CREATED)

    # GET일 경우 댓글 리스트 반환
    if target_type == TargetType.REVIEW.value:
        comments = Comment.objects.filter(review_id=review_id).filter(target_type=target_type)
    elif target_type == TargetType.GALFY.value:
        comments = Comment.objects.filter(galfy_id=galfy_id).filter(target_type=target_type)
    else:
        raise NotFoundError(
            dev_message="타겟 게시물을 찾을 수 없습니다."
        )
    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')
    if sort_field not in ('created_at',): # 확장성을 위해 ==가 아닌 in 조건 사용
        raise InvalidQuery(dev_message="옳지 않은 sort_field 쿼리 파라미터가 전달되었습니다.")
    if sort_direction not in ('desc', 'asc'):
        raise InvalidQuery(dev_message="옳지 않은 sort_direction 쿼리 파라미터가 전달되었습니다.")

    # 페이지네이션 정렬조건 설정
    page, paginator = paginations.apply_queryset_pagination(request, comments, sort_field, sort_direction)
    serializer = CommentSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if not is_author(request, comment):
        return Response({
            "error": {
                "code": "invalid_user",
                "message": "잘못된 접근입니다."
            }
        }, status=HTTP_403_FORBIDDEN)
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

#TODO 추후 커스텀 퍼미션으로 정의하는 방식으로 리팩토링 가능(타 도메인 포함)
def is_author(request, comment):
    if comment.user != request.user:
        return False
    return True
