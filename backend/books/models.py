from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=150, blank=True)
    published_date = models.CharField(null=True)
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

class ExternalCategoryMapping(models.Model):
    provider = models.CharField(max_length=30)  # 알라딘
    external_cid = models.CharField(max_length=100, blank=True)
    external_name = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='external_mappings',
    )
    
    def __str__(self):
        return f"cid: {self.external_cid}, Category: {self.category.name}"
    
    class Meta:
        db_table = 'books_external_category_mapping'
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_cid"], # 한 cid 출처에서 같은 cid가 존재할 수 없음
                name="uq_ext_category_map_provider_cid", # 마이그레이션 시 식별용
            )
        ]
