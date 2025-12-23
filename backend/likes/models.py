from django.db import models
from django.conf import settings

class Like(models.Model):
    class TargetType(models.TextChoices):
        REVIEW = "REVIEW", "리뷰"
        GALFY = "GALFY", "갈피"

    id = models.BigAutoField(primary_key=True)

    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices
    )

    target_id = models.IntegerField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target_type", "target_id"],
                name="unique_like_per_user_per_target"
            )
        ]

    def __str__(self):
        return f"{self.user.full_name} 유저가 {self.target_type} {self.target_id} 게시글에 남긴 좋아요"
