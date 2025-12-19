from rest_framework import serializers
from unicodedata import category

from .models import Book, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'thumbnail', 'category',
        ]
        read_only_fields = ['id']

class BookSummarySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'thumbnail', 'category',
        ]
        read_only_fields = ['id']

class BookListSerializer(serializers.Serializer):
    query = serializers.CharField()  # 검색어
    field = serializers.CharField()  # 검색 필드 (예: title, author)
    page = serializers.IntegerField()  # 현재 페이지 번호
    page_size = serializers.IntegerField()  # 페이지 크기 (한 페이지에 표시될 항목 수)
    results = BookSummarySerializer(many=True)  # 책 요약 목록

    class Meta:
        fields = ["query", "field", "page", "page_size", "results"]