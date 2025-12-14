from rest_framework.serializers import ModelSerializer
from .models import Book, Category

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", 'name']
        read_only_fields = ["id"]

class BookSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = ["id", 'title', 'author', 'publisher', 'published_date', 'isbn', 'page', 'thumbnail', 'category']
        read_only_fields = ["id"]
    #TODO 유효성검사 로직 필요
    
