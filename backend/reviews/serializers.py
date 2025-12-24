from rest_framework import serializers

from .models import Review
from accounts.accounts_serializers.serializers import UserProfileSerializer
from books.serializers import BookSimpleSerializer
from comments.models import TargetType

# TODO 공통 enum으로 리팩토링
TARGET_TYPE_MAP = {
    "review": TargetType.REVIEW.value,
}


class ReviewSerializer(serializers.ModelSerializer):
    book = BookSimpleSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'updated_at',
            'user',
            'book',
            # TODO 서재 평점 추가
            "comments_count",
            "likes_count",
            "is_liked",
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'book', 'likes_count', 'is_liked']

    def get_likes_count(self, obj):
        from likes.models import Like
        return Like.objects.filter(
            target_type=TARGET_TYPE_MAP.get("review"),
            target_id=obj.id
        ).count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        from likes.models import Like
        return Like.objects.filter(
            user=request.user,
            target_type=TARGET_TYPE_MAP.get("review"),
            target_id=obj.id
        ).exists()


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'content']


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'content']
