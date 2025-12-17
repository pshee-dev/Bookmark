from rest_framework import serializers
from .models import Library
from books.models import Book, Category

# 카테고리 이름 시리얼라이저
class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


# 서재에서 사용할 책 정보 기본 시리얼라이저
class BookBaseSerializer(serializers.ModelSerializer):
    category = CategoryNameSerializer(read_only=True)
    class Meta:
        model = Book
        fields = ('title', 'author', 'publisher')


# [GET] 내 서재에 있는 도서 목록 조회 - /library/
class LibraryBookListSerializer(serializers.ModelSerializer):
    book = BookBaseSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('status', 'start_date', 'finish_date', 'rating')

