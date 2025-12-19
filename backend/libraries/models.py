from django.db import models
from django.conf import settings
from books.models import Book

class Library(models.Model):
    
    class StatusEnum(models.TextChoices):
        # key = 'value', 'label'
        want = 'want', '읽고 싶은 책'
        reading = 'reading', '읽고 있는 책'
        finished = 'finished', '다 읽은 책'
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='library')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library')
    status = models.CharField(max_length=20, choices=StatusEnum.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True)
    finish_date = models.DateField(null=True)
    rating = models.PositiveIntegerField(null=True, default=0)
    current_page = models.PositiveIntegerField(null=True, default=0)

    class Meta:
        # 유니크제약조건 설정(uesr, book)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'], name="unique_user_book"
            )
        ]