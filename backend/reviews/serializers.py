from rest_framework import serializers

from .models import Review
from accounts.serializers import UserProfileSerializer
from books.serializers import BookSummarySerializer


class ReviewSerializer(serializers.ModelSerializer):
    book = BookSummarySerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
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
            # TODO 좋아요 개수 추가
            # TODO 서재 평점 추가
            # TODO 댓글 개수 추가
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'book']

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'content']

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'content']
