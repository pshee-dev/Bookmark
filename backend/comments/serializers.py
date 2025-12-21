from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from .models import Comment, TargetType

class TargetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetType

class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "target_type", "target_id", "content", "created_at", "user"]
        read_only_fields = ["id"]

class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["content"]
