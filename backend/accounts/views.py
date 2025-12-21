from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

from galfies.serializers import GalfySerializer
from reviews.serializers import ReviewSerializer
from .serializers import UserProfileSerializer, FollowListSerializer
from django.contrib.auth import get_user_model
from django.db.models import Count

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    reviews = member.reviews.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_galfy_list(request, user_id):
    member = get_object_or_404(User, id=user_id)
    galfies = member.galfies.all()
    serializer = GalfySerializer(galfies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feed(request, user_id):
    pass
