from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Library
from books.models import Book, Category

# 카테고리 이름 시리얼라이저
class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


# 서재에서 사용할 책 정보 기본 시리얼라이저
class BookBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author', 'publisher')


# [GET] 내 서재에 있는 도서 목록 조회 - /library/
class LibraryBookListSerializer(serializers.ModelSerializer):
    book = BookBaseSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('status', 'start_date', 'finish_date', 'rating', 'book')


# [POST] 내 서재에 독서 상태 등록 - /library/
class LibraryBookSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Library
        fields = ('status', 'start_date', 'finish_date', 'rating', 'book', 'user')
        
        # 유니크제약조건 유효성 검사
        validators = [
            UniqueTogetherValidator(
                queryset=Library.objects.all(),
                fields=['user', 'book'],
                message="이미 내 서재에 등록된 책입니다."
            )
        ]

        # Todo: start_date 없이 finish_date 설정 불가
        # Todo: rating 범위 (0~5)


# [GET] 내 서재에 있는 도서 상세 조회 - /library/{library_id}
