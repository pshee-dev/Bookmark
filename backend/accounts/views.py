from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
def detail(request, user_id):
    member = User.objects.get(id=user_id)
    serializer = UserProfileSerializer(member)
    return Response(serializer.data, status=status.HTTP_200_OK)


def follow(request, user_id):
    pass


def get_following_list(request, user_id):
    pass


def get_follower_list(request, user_id):
    pass


def get_review_list(request, user_id):
    pass


def get_galfy_list(request, user_id):
    pass


def get_feed(request, user_id):
    pass