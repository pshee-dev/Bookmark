from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from .models import Galfy
from accounts.serializers import UserProfileSerializer
from books.serializers import BookSummarySerializer

class GalfySerializer(serializers.ModelSerializer):
    book = BookSummarySerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)
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
            # TODO 좋아요 개수 추가
            # TODO 댓글 개수 추가
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
