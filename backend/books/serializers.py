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
            'id', 'title', 'author', 'thumbnail', 'category', 'publisher', 'published_date', 'page', 'isbn',
        ]
        read_only_fields = ['id']

class BookListSerializer(serializers.Serializer):
    keyword = serializers.CharField()  # 검색어
    field = serializers.CharField()  # 검색 필드 (예: title, author)
    current_page = serializers.IntegerField()  # 현재 페이지 번호
    page_size = serializers.IntegerField()  # 페이지 크기 (한 페이지에 표시될 항목 수)
    results = BookSerializer(many=True)  # 책 요약 목록

    class Meta:
        fields = ["keyword", "field", "current_page", "page_size", "results"]
