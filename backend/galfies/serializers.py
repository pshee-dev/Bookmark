from rest_framework import serializers

from books.serializers import BookSimpleSerializer
from .models import Galfy
from accounts.accounts_serializers.serializers import UserProfileSerializer


class GalfySerializer(serializers.ModelSerializer):
    book = BookSimpleSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    class Meta:
        model = Galfy
        fields = [
            'id',
            'page_number',
            'content',
            'created_at',
            'updated_at',
            'user',
            'book',
            'comments_count',
            # TODO 좋아요 개수 추가
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'book']

class GalfyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Galfy
        fields = ['page_number', 'content']

class GalfyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Galfy
        fields = ['page_number', 'content']
