from rest_framework import serializers
from .models import Book, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]

class BookBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title")
        read_only_fields = ["id"]

class BookSerializer(BookBaseSerializer):
    category = CategorySerializer(read_only=True)
    class Meta(BookBaseSerializer.Meta):
        fields =  (
                BookBaseSerializer.Meta.fields
                   + ("author", "publisher","thumbnail", "category", "published_date", "page", "isbn",)
        )

        read_only_fields = ["id"]

class ISBNResolveSerializer(serializers.Serializer):
    """
    ISBN Resolve API 요청 바디용 Serializer
    (Swagger 문서화 전용)
    """
    isbn = serializers.CharField(
        help_text="확인 또는 생성할 도서의 ISBN 값",
        max_length=20
    )


class BookSimpleSerializer(BookBaseSerializer):
    category = CategorySerializer(read_only=True)
    class Meta(BookBaseSerializer.Meta):
        fields =  (
            BookBaseSerializer.Meta.fields
             + ("author", "publisher","thumbnail", "category", "isbn", )
        )


class BookWithReviewAndGalfiesSerializer(BookBaseSerializer):
    category = CategorySerializer(read_only=True)
    class Meta(BookBaseSerializer.Meta):
        pass

    galfies = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    def get_galfies(self, obj):
        from galfies.serializers import GalfySerializer
        return GalfySerializer(obj.galfies.all(), many=True).data

    def get_reviews(self, obj):
        from reviews.serializers import ReviewSerializer
        return ReviewSerializer(obj.reviews.all(), many=True).data

    class Meta(BookBaseSerializer.Meta):
        fields = (
                BookBaseSerializer.Meta.fields
                + ("author", "publisher", "thumbnail", "category",
                   "published_date", "page", "isbn",
                   "galfies", "reviews")
        )
class BookWithReviewAndGalfiesSerializerInLibrary(BookWithReviewAndGalfiesSerializer):
    class Meta(BookWithReviewAndGalfiesSerializer.Meta):
        pass


class BookListSerializer(serializers.Serializer):
    keyword = serializers.CharField()  # 검색어
    field = serializers.CharField()  # 검색 필드 (예: title, author)
    current_page = serializers.IntegerField()  # 현재 페이지 번호
    page_size = serializers.IntegerField()  # 페이지 크기 (한 페이지에 표시될 항목 수)
    results = BookSerializer(many=True)  # 책 요약 목록

    class Meta:
        fields = ["keyword", "field", "current_page", "page_size", "results"]

class BookSummarySerializer(BookBaseSerializer):
    category = CategorySerializer(read_only=True)
    class Meta(BookBaseSerializer.Meta):
        fields = (
                BookBaseSerializer.Meta.fields
                + ("author", "publisher", "thumbnail", "category")
        )
        read_only_fields = ["id"]
