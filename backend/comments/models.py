from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

class TargetType(models.TextChoices):
    REVIEW = 'REVIEW', '리뷰 댓글'
    GALFY = 'GALFY', '갈피 댓글'

class Comment(models.Model):
    target_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    target_id = models.IntegerField()
    target = GenericForeignKey('target_type', 'target_id')

    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             )

    def __str__(self):
        return '\n'.join([
            f"작성된 게시글 타입: {self.target_type}",
            f"작성된 게시글 id: {self.target_id}",
            f"댓글 id: {self.pk}",
            f"댓글 작성자: {self.user.full_name}",
            f"댓글 내용: {self.content}"
        ])

