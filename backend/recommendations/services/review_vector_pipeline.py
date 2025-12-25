import json
import threading

from django.db import close_old_connections

from recommendations.models import BookVector, UserProfileVector
from recommendations.my_source.embeddings import make_embeddings
from recommendations.my_source.summary.summarizer.summarize_user_reviews import (
    summarize_user_reviews,
)
from recommendations.services.make_book_vector_pipeline_after_add_book import (
    PROVIDER_MODEL_KEY,
    _upsert_chroma,
)
from reviews.models import Review


ALPHA = 0.2


def enqueue_review_vector_update(review_id: int) -> None:
    thread = threading.Thread(
        target=_update_vectors_for_review,
        args=(review_id,),
        daemon=True,
    )
    thread.start()


def _update_vectors_for_review(review_id: int) -> None:
    close_old_connections()

    review = (
        Review.objects.select_related("book", "user")
        .filter(id=review_id)
        .first()
    )
    if not review:
        return

    review_text = _make_review_text(review.title, review.content)
    if review_text:
        review_emb = make_embeddings(review_text)
        if review_emb:
            _update_user_profile_vector(review.user_id, review_emb)

    _update_book_vector_from_reviews(review.book)


def _make_review_text(title: str | None, content: str | None) -> str:
    parts = [str(x).strip() for x in [title, content] if x and str(x).strip()]
    return " ".join(parts).strip()


def _update_user_profile_vector(user_id: int, review_emb: list[float]) -> None:
    if not review_emb:
        return

    profile, created = UserProfileVector.objects.get_or_create(
        user_id=user_id,
        defaults={"vector": json.dumps(review_emb)},
    )
    if created:
        return

    try:
        old = json.loads(profile.vector)
    except Exception:
        old = None

    if not isinstance(old, list) or len(old) != len(review_emb):
        profile.vector = json.dumps(review_emb)
    else:
        new_vec = [
            (1 - ALPHA) * o + ALPHA * r
            for o, r in zip(old, review_emb)
        ]
        profile.vector = json.dumps(new_vec)

    profile.save(update_fields=["vector", "updated_at"])


def _update_book_vector_from_reviews(book) -> None:
    reviews = Review.objects.filter(book_id=book.id).values_list("title", "content")
    review_texts = []
    for title, content in reviews:
        text = _make_review_text(title, content)
        if text:
            review_texts.append(text)

    if not review_texts:
        return

    summary = summarize_user_reviews(review_texts)
    summary_text = _clean_text(summary.get("summary", ""))
    if not summary_text:
        return

    emb = make_embeddings(summary_text)
    if not emb:
        return

    BookVector.objects.update_or_create(
        book=book,
        defaults={
            "vector": json.dumps(emb),
            "embedding_model": PROVIDER_MODEL_KEY,
            "embedding_dim": len(emb),
        },
    )

    _upsert_chroma(book, summary_text, emb)


def _clean_text(text: str) -> str:
    return (text or "").strip()[:1500]
