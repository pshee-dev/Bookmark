from django.conf import settings

from books.models import *


class Review(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)

    def __str__(self):
        return f"\n 도서 이름: {self.book}\n리뷰 제목: {self.title}\n작성자: {self.user.nickname} "
