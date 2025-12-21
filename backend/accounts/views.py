from itertools import chain

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

from common.utils.paginations import apply_list_pagination, apply_queryset_pagination
from galfies.models import Galfy
from galfies.serializers import GalfySerializer
from reviews.models import Review
from comments.models import Comment
from reviews.serializers import ReviewSerializer
from .accounts_serializers.serializers import UserProfileSerializer, FollowListSerializer
from .accounts_serializers.feed_serializers import find_serializer_feed_item
from django.contrib.auth import get_user_model
from django.db.models import Count
from .errors import InvalidQuery

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request, user_id):
    user_with_counts = User.objects.annotate(
        followings_count=Count('followings', distinct=True),
        followers_count=Count('followers', distinct=True),
        # reviews_count=Count('reviews', distinct=True),
        # galfies_count=Count('galfies', distinct=True),
    )
    member = get_object_or_404(user_with_counts, id=user_id)
    serializer = UserProfileSerializer(member)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request, user_id):
    me = request.user
    member = get_object_or_404(User, id=user_id)
    # 자기 자신은 팔로우 할 수 없음
    if me != member:
        if me in member.followers.all():
            # 언팔로우
            member.followers.remove(me)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 팔로우
            member.followers.add(me)
            return Response(status=status.HTTP_200_OK)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    followings = get_list_or_404(member.followings.all())
    serializer = FollowListSerializer(followings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follower_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    followers = get_list_or_404(member.followers.all())
    serializer = FollowListSerializer(followers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#TODO 추후 리뷰, 갈피, 피드 코드 중복 제거 리팩토링 필요
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    reviews = member.reviews.all()

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    validate_query(sort_field, sort_direction) # 유효하지 않은 정렬조건 쿼리의 경우, 에러 발생

    # 페이지네이션 정렬조건 설정
    page, paginator = apply_queryset_pagination(request, reviews, sort_field, sort_direction)
    serializer = ReviewSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_galfy_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    galfies = member.galfies.all()

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')

    validate_query(sort_field, sort_direction) # 유효하지 않은 정렬조건 쿼리의 경우, 에러 발생

    # 페이지네이션 정렬조건 설정
    page, paginator = apply_queryset_pagination(request, galfies, sort_field, sort_direction)
    serializer = GalfySerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feed(request, user_id):
    member = get_object_or_404(User, id=user_id)

    reviews = Review.objects.filter(user=member)
    galfies = Galfy.objects.filter(user=member)
    comments = Comment.objects.filter(user=member)

    feed = list(chain(reviews, galfies, comments))
    feed.sort(key=lambda x: x.created_at, reverse=True)

    serialized_feed = [find_serializer_feed_item(obj, request=request).data for obj in feed]
    page, paginator = apply_list_pagination(request, serialized_feed, "page")
    return paginator.get_paginated_response(page)


def validate_query(sort_field, sort_direction):
    if sort_field not in ('created_at',): # 확장성을 위해 ==가 아닌 in 조건 사용
        raise InvalidQuery(dev_message="옳지 않은 sort_field 쿼리 파라미터가 전달되었습니다.")
    if sort_direction not in ('desc', 'asc'):
        raise InvalidQuery(dev_message="옳지 않은 sort_direction 쿼리 파라미터가 전달되었습니다.")



