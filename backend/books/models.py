from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=150)
    published_date = models.DateField()
    isbn = models.CharField(max_length=20)
    page = models.IntegerField()
    thumbnail = models.URLField(max_length=500)
    category = models.ForeignKey(
        to=Category,
        on_delete=models.PROTECT,
        related_name='books',
    )

    def __str__(self):
        return self.title
    