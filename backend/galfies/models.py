from django.conf import settings

from books.models import *

class Galfy(models.Model):
    page_number = models.IntegerField(null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='galfies',)
    book = models.ForeignKey(Book,
                             on_delete=models.PROTECT,
                             related_name='galfies',)

    def __str__(self):
        return f"\n 도서 이름: {self.book}\n작성자: {self.user.full_name}\n갈피 내용: {self.content}"
