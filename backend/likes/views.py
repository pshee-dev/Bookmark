from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from comments.models import TargetType
from likes.errors import InvalidTarget, InvalidTargetType
from likes.models import Like

TARGET_TYPE_MAP = {
    "galfy":TargetType.GALFY.value,
    "review":TargetType.REVIEW.value,
}

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def like_toggle(request):

    raw_target_type = request.data.get("target_type")
    target_type = TARGET_TYPE_MAP.get(raw_target_type)
    target_id = request.data.get("target_id")

    if not target_type:
        raise InvalidTargetType()
    if not target_id:
        raise InvalidTarget()

    # 유저가 해당 게시글에 좋아요한 기록(Like 객체)이 없으면 생성
    like, created = Like.objects.get_or_create( # created == 생성 여부
        user=request.user,
        target_type=target_type,
        target_id=target_id,
    )
    if not created:
        like.delete()

    return #TODO Response()
