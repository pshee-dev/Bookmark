from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Book, Category

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']

class BookSerializer(ModelSerializer):
    category_id = PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'publisher', 'published_date', 
            'isbn', 'page', 'thumbnail', 'category_id', 'category'
        ]
        read_only_fields = ['id']
    #TODO 유효성검사 로직 필요
    
