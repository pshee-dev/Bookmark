from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=150, blank=True)
    published_date = models.DateField(null=True)
    isbn = models.CharField(max_length=20, blank=True)
    page = models.IntegerField(null=True)
    thumbnail = models.URLField(max_length=500, blank=True)
    category = models.ForeignKey(
        to=Category,
        on_delete=models.PROTECT, 
        related_name='books',
    )

    def __str__(self):
        return self.title

#TODO 복합유니크 걸어야함 
class ExternalCategoryMapping(models.Model):
    provider = models.CharField(max_length=30, blank=True)  # 알라딘
    external_cid = models.CharField(max_length=50, blank=True)
    external_name = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='external_mappings',
    )
    
    def __str__(self):
        return f"cid: {self.external_cid}, Category: {self.category.name}"
    
    class Meta:
        db_table = 'books_external_category_mapping'
