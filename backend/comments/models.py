from django.db import models
from django.conf import settings

from galfies.models import Galfy
from reviews.models import Review
from .errors import ValidationError

# TODO 공통 enum으로 리팩토링
class TargetType(models.TextChoices):
    REVIEW = 'REVIEW', '리뷰 댓글'
    GALFY = 'GALFY', '갈피 댓글'

class Comment(models.Model):
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
    )
    galfy = models.ForeignKey(
        Galfy,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
    )
    def clean(self):
        if self.target_type == TargetType.REVIEW:
            if not self.review or self.galfy:
                raise ValidationError(dev_message = "리뷰 댓글은 review만 설정해야 합니다.")
        elif self.target_type == TargetType.GALFY:
            if not self.galfy or self.review:
                raise ValidationError(dev_message="갈피 댓글은 galfy만 설정해야 합니다.")

    def __str__(self):
        return '\n'.join([
            f"작성된 게시글 타입: {self.target_type}",
            f"작성된 게시글 id: {self.target_id}",
            f"댓글 id: {self.pk}",
            f"댓글 작성자: {self.user.full_name}",
            f"댓글 내용: {self.content}"
        ])

