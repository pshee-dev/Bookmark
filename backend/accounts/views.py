from itertools import chain

from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from common.utils.paginations import apply_list_pagination, apply_queryset_pagination
from reviews.models import Review
from galfies.models import Galfy
from comments.models import Comment

from reviews.serializers import ReviewSerializer
from galfies.serializers import GalfySerializer
from comments.serializers import CommentSerializer
from .accounts_serializers.serializers import (
    UserProfileSerializer,
    FollowListSerializer,
)
from .accounts_serializers.feed_serializers import find_serializer_feed_item
from .errors import InvalidQuery

User = get_user_model()

@extend_schema(
    tags=["Accounts"],
    summary="유저 프로필 조회",
    description="""
    특정 유저의 프로필 정보를 조회합니다.

    - 팔로워 수 / 팔로잉 수 포함
    - 로그인 필수
    """,
    parameters=[OpenApiParameter("user_id", int, location=OpenApiParameter.PATH)],
    responses={
        200: UserProfileSerializer,
        404: OpenApiResponse(description="유저가 존재하지 않음"),
    }
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def profile(request, user_id):
    user_with_counts = User.objects.annotate(
        followings_count=Count('followings', distinct=True),
        followers_count=Count('followers', distinct=True),
    )
    member = get_object_or_404(user_with_counts, id=user_id)
    serializer = UserProfileSerializer(member)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Accounts"],
    summary="팔로우 / 언팔로우",
    description="""
    특정 유저를 팔로우하거나 언팔로우합니다.

    - 이미 팔로우 중이면 → 언팔로우 (204)
    - 팔로우 중이 아니면 → 팔로우 (200)
    - 자기 자신은 팔로우 불가
    """,
    parameters=[OpenApiParameter("user_id", int, location=OpenApiParameter.PATH)],
    responses={
        200: OpenApiResponse(description="팔로우 성공"),
        204: OpenApiResponse(description="언팔로우 성공"),
        404: OpenApiResponse(description="유저가 존재하지 않음"),
    }
)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def follow(request, user_id):
    me = request.user
    member = get_object_or_404(User, id=user_id)

    if me != member:
        if me in member.followers.all():
            member.followers.remove(me)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            member.followers.add(me)
            return Response(status=status.HTTP_200_OK)

@extend_schema(
    tags=["Accounts"],
    summary="팔로잉 목록 조회",
    parameters=[OpenApiParameter("user_id", int, location=OpenApiParameter.PATH)],
    responses={200: FollowListSerializer(many=True)}
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_following_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    followings = get_list_or_404(member.followings.all())
    serializer = FollowListSerializer(followings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Accounts"],
    summary="팔로워 목록 조회",
    parameters=[OpenApiParameter("user_id", int, location=OpenApiParameter.PATH)],
    responses={200: FollowListSerializer(many=True)}
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_follower_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    followers = get_list_or_404(member.followers.all())
    serializer = FollowListSerializer(followers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Accounts"],
    summary="유저 리뷰 목록 조회",
    parameters=[
        OpenApiParameter("user_id", int, location=OpenApiParameter.PATH),
        OpenApiParameter("page", int, description="page number"),
        OpenApiParameter("page_size", int, description="page size override"),
        OpenApiParameter("sort-field", str, description="정렬 기준 (created_at)"),
        OpenApiParameter("sort-direction", str, description="정렬 방향 (asc | desc)"),
    ],
    responses={200: ReviewSerializer(many=True)}
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_review_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    reviews = member.reviews.all()

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')
    validate_query(sort_field, sort_direction)

    page, paginator = apply_queryset_pagination(request, reviews, sort_field, sort_direction)
    serializer = ReviewSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@extend_schema(
    tags=["Accounts"],
    summary="유저 갈피 목록 조회",
    parameters=[
        OpenApiParameter("user_id", int, location=OpenApiParameter.PATH),
        OpenApiParameter("page", int, description="page number"),
        OpenApiParameter("page_size", int, description="page size override"),
        OpenApiParameter("sort-field", str, description="정렬 기준 (created_at)"),
        OpenApiParameter("sort-direction", str, description="정렬 방향 (asc | desc)"),
    ],
    responses={200: GalfySerializer(many=True)}
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_galfy_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    galfies = member.galfies.all()

    sort_direction = request.query_params.get('sort-direction', 'desc')
    sort_field = request.query_params.get('sort-field', 'created_at')
    validate_query(sort_field, sort_direction)

    page, paginator = apply_queryset_pagination(request, galfies, sort_field, sort_direction)
    serializer = GalfySerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)

@extend_schema(
    tags=["Feed"],
    summary="유저 활동 피드 조회",
    description="""
    유저의 리뷰 / 갈피 / 댓글을 시간순으로 통합하여 반환합니다.
    """,
    parameters=[
        OpenApiParameter("user_id", int, location=OpenApiParameter.PATH),
        OpenApiParameter("page", int, description="page number"),
        OpenApiParameter("page_size", int, description="page size override"),
    ],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_feed(request, user_id):
    member = get_object_or_404(User, id=user_id)

    reviews = Review.objects.filter(user=member)
    galfies = Galfy.objects.filter(user=member)
    comments = Comment.objects.filter(user=member)

    feed = list(chain(reviews, galfies, comments))
    feed.sort(key=lambda x: x.created_at, reverse=True)

    serialized_feed = [
        find_serializer_feed_item(obj, request=request).data
        for obj in feed
    ]

    page, paginator = apply_list_pagination(request, serialized_feed, "page")
    return paginator.get_paginated_response(page)

def validate_query(sort_field, sort_direction):
    if sort_field not in ('created_at',):
        raise InvalidQuery(dev_message="옳지 않은 sort_field 쿼리 파라미터입니다.")
    if sort_direction not in ('asc', 'desc'):
        raise InvalidQuery(dev_message="옳지 않은 sort_direction 쿼리 파라미터입니다.")
