from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from galfies.serializers import GalfySerializer
from reviews.serializers import ReviewSerializer
from .models import Comment, TargetType

class TargetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TargetType

class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)
    galfy = GalfySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "target_type", "content", "created_at", "user", "review", "galfy"]
        read_only_fields = ["id"]

class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["content"]
