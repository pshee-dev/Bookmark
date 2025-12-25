from django.conf import settings
from django.db import models
from books.models import Book

class UserProfileVector(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_vector",
    )
    vector = models.TextField()  # 문자열 리스트
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"profile_vector:{self.user_id}"


class BookVector(models.Model):
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name="vector",
    )

    # 실제 임베딩 벡터 저장용.
    # JSON 문자열로 list[float] 직렬화해서 저장.
    vector = models.TextField()  # JSON string of list[float]

    # 어떤 임베딩 모델로 만든 벡터인지 기록 (예: gms-openai::text-embedding-3-large).
    # 나중에 모델이 여러 개일 때 구분/검증용.
    embedding_model = models.CharField(max_length=100)

    # 벡터 차원 수 (예: 3072).
    # 모델별 차원 확인 및 검증용.
    embedding_dim = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"book_vector:{self.book_id}"
