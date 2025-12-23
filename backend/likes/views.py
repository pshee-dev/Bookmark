
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_200_OK

from comments.models import TargetType
from likes.errors import InvalidTarget, InvalidTargetType
from likes.models import Like
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

TARGET_TYPE_MAP = {
    "galfy":TargetType.GALFY.value,
    "review":TargetType.REVIEW.value,
}

@extend_schema(
    methods=['POST'],
    request=inline_serializer(
        name='LikeToggleRequest',
        fields={
            'target_type': serializers.CharField(),
            'target_id': serializers.IntegerField(),
        },
    ),
    responses=inline_serializer(
        name='LikeToggleResponse',
        fields={
            'target_type': serializers.CharField(),
            'target_id': serializers.IntegerField(),
            'is_liked': serializers.BooleanField(),
            'like_count': serializers.IntegerField(),
        },
    ),
    tags=['likes'],
)
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
    like, is_created = Like.objects.get_or_create( # created == 생성 여부
        user=request.user,
        target_type=target_type,
        target_id=target_id,
    )
    if not is_created:
        like.delete()

    like_count = Like.objects.filter(target_type=target_type, target_id=target_id).count()

    return Response({
        "target_type": target_type,
        "target_id": target_id,
        "is_liked": is_created,
        "like_count": like_count
    }, status=HTTP_200_OK)
