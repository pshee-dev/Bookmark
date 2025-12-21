from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from galfies.models import Galfy
from galfies.serializers import GalfySerializer
from reviews.models import Review
from common.utils import paginations
from .errors import InvalidTargetType
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

    # 페이지네이션 정렬조건 설정
    page, paginator = paginations.apply_pagination(request, comments, 'created_at')
    serializer = CommentSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


def delete(request, target_id):
    pass
