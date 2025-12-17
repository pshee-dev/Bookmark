from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['title', 'content']

