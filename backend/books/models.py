from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, null=True)
    publisher = models.CharField(max_length=150, null=True)
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
    