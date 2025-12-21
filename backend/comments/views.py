from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_403_FORBIDDEN

from galfies.models import Galfy
from common.utils import safe_convert
from reviews.models import Review
from common.utils import paginations
from .errors import InvalidTargetType, InvalidQuery
from .models import TargetType, Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from rest_framework.response import Response

# POST/PUT/PATCH/DELETE는 로그인 필수, GET은 로그인 없이 접근 가능
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def list_and_create(request, target_type, review_id=None, galfy_id=None):

    if target_type == TargetType.REVIEW.value:
        model = Review
        target_id = review_id
    elif target_type == TargetType.GALFY.value:
        model = Galfy
        target_id = galfy_id
    else:
        raise InvalidTargetType(
            dev_message="댓글이 달린 게시글 타입이 유효하지 않습니다."
        )

    # 타겟이 실제로 존재하는 게시글인지 확인
        # - 시리얼라이저에 객체가 아닌 id를 넘기게되므로 시리얼라이저에서 검증에서 걸리지 않기 때문.
        #TODO 리뷰, 갈피 게시글 삭제 시 댓글 삭제도 연동되게끔 하는 로직 추가
    target = get_object_or_404(model, id=target_id)

    if request.method == 'POST':
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_comment = serializer.save(
            user=request.user,
            target_type=target_type,
            target_id=target_id,
        )

        return Response(CommentSerializer(created_comment).data, status=status.HTTP_201_CREATED)

    # GET일 경우 댓글 리스트 반환
    comments = Comment.objects.filter(target_id=target_id)
    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')
    if sort_field not in ('created_at'): # 확장성을 위해 ==가 아닌 in 조건 사용
        raise InvalidQuery(dev_message="옳지 않은 sort_field 쿼리 파라미터가 전달되었습니다.")
    if sort_direction not in ('desc', 'asc'):
        raise InvalidQuery(dev_message="옳지 않은 sort_direction 쿼리 파라미터가 전달되었습니다.")

    # 페이지네이션 정렬조건 설정
    page, paginator = paginations.apply_pagination(request, comments, sort_field, sort_direction)
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
