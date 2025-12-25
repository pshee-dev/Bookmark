
import json
import os
import random
import re
from datetime import datetime

import requests

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from langchain_community.vectorstores import Chroma

from books.serializers import BookSummarySerializer
from recommendations.services.make_book_vector_pipeline_after_add_book import (
    COLLECTION_NAME,
    VECTOR_DB_DIR,
    PrecomputedEmbedding,
)
from recommendations.my_source.embeddings import make_embeddings
from reviews.models import Review

GMS_OPENAI_CHAT_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
GMS_LLM_MODEL = "gpt-4o-mini"
LLM_RAW_LOG_PATH = os.path.join(os.path.dirname(__file__), "llm_raw.log")


@api_view(["GET"])
def recommend_book(request, review_id):
    review = get_object_or_404(Review.objects.select_related("book"), id=review_id)

    review_text = _make_review_text(review.title, review.content)
    if not review_text:
        return Response(
            {"error": {"code": "empty_review", "message": "Review content is empty."}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    review_emb = make_embeddings(review_text)
    if not review_emb:
        return Response(
            {"error": {"code": "embedding_failed", "message": "Embedding failed."}},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DB_DIR,
        embedding_function=PrecomputedEmbedding(len(review_emb)),
    )
    results = vectordb._collection.query(
        query_embeddings=[review_emb],
        n_results=10,
        include=["metadatas", "documents"],
    )

    metadatas = (results.get("metadatas") or [[]])[0]
    documents = (results.get("documents") or [[]])[0]
    isbns = []
    for md in metadatas:
        isbn = str(md.get("isbn13", "")).strip()
        if not isbn or isbn == review.book.isbn:
            continue
        if isbn in isbns:
            continue
        isbns.append(isbn)
        if len(isbns) >= 5:
            break

    books = BookSummarySerializer(
        _ordered_books_by_isbn(isbns),
        many=True,
    ).data

    keyword_texts = [review_text] + [doc for doc in documents if doc]
    keywords = _extract_keywords_from_lexicon(keyword_texts, max_keywords=5)
    if not keywords:
        keywords = _extract_keywords_with_llm(keyword_texts, max_keywords=5)
    if not keywords:
        keywords = _extract_keywords(keyword_texts, max_keywords=5)

    for idx, book in enumerate(books):
        book["reason"] = _build_reason_for_book(book, review.book, keywords, idx)

    return Response(
        {
            "review_id": review.id,
            "keywords": keywords,
            "books": books,
        },
        status=status.HTTP_200_OK,
    )


def _make_review_text(title: str | None, content: str | None) -> str:
    parts = [str(x).strip() for x in [title, content] if x and str(x).strip()]
    return " ".join(parts).strip()


def _build_reason_draft(category_name: str, keywords: list[str], review_summary: str) -> str:
    parts = []
    if category_name:
        parts.append(f"category: {category_name}")
    if keywords:
        parts.append(f"keywords: {', '.join(keywords[:5])}")
    if review_summary:
        parts.append(f"review_summary: {review_summary[:200]}")
    return " | ".join(parts)


def _extract_keywords(texts: list[str], max_keywords: int = 5) -> list[str]:
    if not texts:
        return []

    stopwords = {
        "그리고", "하지만", "그래서", "그런데", "정말", "너무", "조금", "그냥", "이런",
        "저런", "이것", "저것", "그거", "이거", "책", "작품", "이야기", "문장", "내용",
        "느낌", "생각", "사건", "사람", "마음", "독자", "작가", "시선", "부분", "장면",
        "읽다", "읽고", "읽는", "읽었다", "있다", "없다", "하다", "된다", "처럼", "때문",
    }

    unigram_counts: dict[str, int] = {}
    bigram_counts: dict[str, int] = {}

    for text in texts:
        cleaned = re.sub(r"[^0-9a-zA-Z가-힣\s]", " ", str(text))
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
        tokens = [t for t in tokens if len(t) >= 2 and t not in stopwords]

        for token in tokens:
            unigram_counts[token] = unigram_counts.get(token, 0) + 1
        for a, b in zip(tokens, tokens[1:]):
            if a in stopwords or b in stopwords:
                continue
            bigram = f"{a} {b}"
            bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1

    candidates: list[tuple[str, float]] = []
    for term, count in bigram_counts.items():
        candidates.append((term, count * 3.0))
    for term, count in unigram_counts.items():
        candidates.append((term, count * 1.5))

    candidates.sort(key=lambda x: (-x[1], -len(x[0])))

    seen = set()
    keywords: list[str] = []
    for term, _score in candidates:
        if term in seen:
            continue
        seen.add(term)
        keywords.append(term)
        if len(keywords) >= max_keywords:
            break

    return keywords


def _extract_keywords_from_lexicon(texts: list[str], max_keywords: int = 5) -> list[str]:
    joined = " ".join([str(t) for t in texts if t]).strip()
    if not joined:
        return []

    lexicon = [
        (r"(역사|역사의|역사적|근현대|현대사|사건|항쟁|민주화|학살|참사|전쟁|분단|독재|군사정권|광주)", "역사적 사건"),
        (r"(아픔|상처|비극|슬픔|고통|상흔|트라우마)", "아픔의 기억"),
        (r"(기억|회상|되새김|잊지|추모|기억하는)", "아픔의 기억"),
        (r"(무거운|묵직한|암울한|침울한|음울한|비장한)", "무거운 분위기"),
        (r"(분노|격정|분개|억울함)", "분노"),
        (r"(슬픔|애도|눈물|비애)", "슬픔"),
        (r"(소년|아이|청소년)", "소년"),
        (r"(잔인|폭력|비정)", "잔인함"),
        (r"(여운|잔상|오래 남)", "여운"),
        (r"(기억|추억)", "기억"),
    ]

    found = []
    seen = set()
    for pattern, keyword in lexicon:
        if keyword in seen:
            continue
        if re.search(pattern, joined):
            found.append(keyword)
            seen.add(keyword)
        if len(found) >= max_keywords:
            break

    return found[:max_keywords]


def _extract_keywords_with_llm(texts: list[str], max_keywords: int = 5) -> list[str]:
    api_key = os.getenv("GMS_KEY")
    if not api_key:
        return []

    context = _make_context_snippet(texts, max_chars=2000)
    if not context:
        return []

    prompt = (
        "Extract 3-5 concise Korean keyphrases from the text.\n"
        "Use only information present in the text.\n"
        "Return only a JSON array of strings, no extra text.\n"
        "Keyphrases should be 2-6 words and meaningful for recommendation reasons.\n"
        "TEXT:\n"
        f"{context}"
    )

    payload = {
        "model": GMS_LLM_MODEL,
        "messages": [
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        r = requests.post(
            GMS_OPENAI_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return []

    keywords = _parse_llm_json_array(content)
    if not keywords:
        return []

    cleaned = []
    for keyword in keywords:
        if isinstance(keyword, str):
            kw = keyword.strip()
            if kw:
                cleaned.append(kw)
    return cleaned[:max_keywords]


def _make_context_snippet(texts: list[str], max_chars: int = 800) -> str:
    buf = []
    total = 0
    for text in texts:
        t = str(text).strip()
        if not t:
            continue
        remaining = max_chars - total
        if remaining <= 0:
            break
        buf.append(t[:remaining])
        total += len(buf[-1])
        if total >= max_chars:
            break
    return " ".join(buf)

def _build_reason(keywords: list[str]) -> str:
    if not keywords:
        return "리뷰에서 뚜렷한 키워드를 찾지 못했어요."

    primary = keywords[0]
    secondary = keywords[1] if len(keywords) > 1 else None

    if secondary:
        pair = _join_with_particle(primary, f" {secondary}", "과", "와")
        templates = [
            "{pair}에서 느껴지는 정서와 여운이 잘 맞는 책이에요.",
            "{pair}의 결을 따라가며 차분히 읽기 좋아요.",
            "{pair}을 떠올리게 하는 이야기를 담고 있어요.",
            "{pair}이 자연스럽게 이어지는 흐름이 돋보여요.",
            "{pair}의 분위기를 좋아한다면 만족스러울 거예요.",
        ]
        template = random.choice(templates)
        return template.format(pair=pair)

    obj = _join_with_particle(primary, "", "을", "를").strip()
    templates = [
        "{primary}이 중심에 놓인 이야기에요.",
        "{obj} 자연스럽게 마음에 남는 책이에요.",
        "{primary}을 따라가며 차분히 읽기 좋아요.",
        "{obj} 곁에 두고 천천히 읽기 좋아요.",
        "{primary}을 좋아한다면 잘 맞을 거예요.",
    ]
    template = random.choice(templates)
    return template.format(primary=primary, obj=obj)


def _expand_keywords(keywords: list[str]) -> list[str]:
    keyword_map = {
        "죽음": "죽음 앞의 성찰",
        "성찰": "깊은 성찰",
        "성장": "인물의 성장",
        "모험": "흥미진진한 모험",
        "감정": "섬세한 감정의 흐름",
        "치유": "조용한 위로와 치유",
        "관계": "관계의 변화",
        "희망": "작은 희망",
        "불안": "흔들리는 마음",
        "우정": "따뜻한 우정",
        "가족": "가족의 온기",
        "삶": "삶에 대한 질문",
        "시간": "시간의 흐름",
        "기억": "기억의 조각",
        "전쟁": "전쟁의 기억",
        "역사": "역사의 숨결",
        "과학": "과학적 호기심",
        "철학": "사유의 깊이",
    }

    expanded = []
    for k in keywords:
        k = k.strip()
        if not k:
            continue
        if " " in k:
            expanded.append(k)
            continue
        expanded.append(keyword_map.get(k, f"{k}의 결"))

    if len(expanded) >= 2:
        return expanded[:5]
    if len(expanded) == 1:
        fallback = [
            "감정의 여운",
            "잔잔한 문장",
            "조용한 시선",
            "따뜻한 온기",
        ]
        for extra in fallback:
            if extra not in expanded:
                expanded.append(extra)
                if len(expanded) >= 2:
                    break

    return expanded[:5]


def _refine_reasons_with_llm(
    books: list[dict],
    keywords: list[str],
    review_summary: str,
) -> list[str] | None:
    if not books:
        return None

    api_key = os.getenv("GMS_KEY")
    if not api_key:
        return None

    items = []
    for book in books:
        category_name = (book.get("category") or {}).get("name") or ""
        items.append(
            {
                "title": str(book.get("title", "")).strip(),
                "author": str(book.get("author", "")).strip(),
                "category": str(category_name).strip(),
                "reason_draft": str(book.get("reason", "")).strip(),
            }
        )

    payload_data = {
        "keywords": keywords[:5],
        "review_context": review_summary or "",
        "items": items,
    }

    prompt = (
        "Rewrite each reason_draft to be more natural and readable in Korean.\n"
        "Return only a JSON array of strings, same length and order as items.\n"
        "Do not include code fences, explanations, or extra text.\n"
        "Rules:\n"
        "- Output exactly one sentence per item (about 60-120 chars).\n"
        "- Use a warm and considerate tone.\n"
        "- Do not add new facts beyond the provided data.\n"
        "- Focus on connecting the user's review (keywords/context) to the recommendation.\n"
        "- Include at least one keyword from the user's review verbatim in each item.\n"
        "- Avoid generic book-description tone; keep it user-centric.\n"
        "- Do not mention title or author.\n"
        "- Make each item distinct; do not repeat the same sentence across items.\n"
        "- If reason_draft is empty, return an empty string for that item.\n"
        "DATA:\n"
        f"{json.dumps(payload_data, ensure_ascii=True)}"
    )

    payload = {
        "model": GMS_LLM_MODEL,
        "messages": [
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    try:
        r = requests.post(
            GMS_OPENAI_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        print("[recommendations] LLM request failed")
        return None
    _append_llm_raw_log(content)

    reasons = _parse_llm_json_array(content)
    if reasons is None:
        print("[recommendations] LLM response parse failed:", content[:500])
        return None

    if not isinstance(reasons, list):
        return None
    if len(reasons) < len(books):
        reasons = reasons + ([""] * (len(books) - len(reasons)))
    if len(reasons) > len(books):
        reasons = reasons[: len(books)]

    cleaned = []
    for book, reason in zip(books, reasons):
        if not isinstance(reason, str):
            cleaned.append("")
            continue
        candidate = reason.strip()
        cleaned.append(
            candidate
            if _is_reason_safe(candidate, book) and _has_keyword(candidate, keywords)
            else ""
        )
    return cleaned


def _parse_llm_json_array(content: str) -> list[str] | None:
    if not content:
        return None

    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, list) else None
    except Exception:
        pass

    # Try to extract a JSON array from surrounding text or code fences.
    start = content.find("[")
    end = content.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        parsed = json.loads(content[start : end + 1])
    except Exception:
        return None

    return parsed if isinstance(parsed, list) else None


def _is_reason_safe(reason: str, book: dict) -> bool:
    if not reason:
        return False

    forbidden_markers = ["제목", "저자", "title:", "author:"]
    if any(marker in reason for marker in forbidden_markers):
        return False

    title = str(book.get("title", "")).strip()
    author = str(book.get("author", "")).strip()
    if title and title in reason:
        return False
    if author and author in reason:
        return False

    return True


def _has_keyword(reason: str, keywords: list[str]) -> bool:
    if not reason:
        return False
    for keyword in keywords:
        if keyword and keyword in reason:
            return True
    return False


def _append_llm_raw_log(content: str) -> None:
    if content is None:
        return
    try:
        with open(LLM_RAW_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n--- {datetime.now().isoformat()} ---\n")
            f.write(content)
            f.write("\n")
    except Exception:
        pass


def _join_with_particle(word: str, tail: str, with_final: str, without_final: str) -> str:
    if not word:
        return tail

    last = word[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3:
        has_final = (code - 0xAC00) % 28 != 0
    else:
        has_final = False

    particle = with_final if has_final else without_final
    return f"{word}{particle}{tail}"


def _ordered_books_by_isbn(isbns):
    if not isbns:
        return []
    from books.models import Book

    qs = Book.objects.filter(isbn__in=isbns)
    by_isbn = {b.isbn: b for b in qs}
    return [by_isbn[i] for i in isbns if i in by_isbn]


def _fixed_reason_for_book(book: dict, review_book, keywords: list[str]) -> str | None:
    review_author = _normalize_author(getattr(review_book, "author", ""))
    book_author = _normalize_author(str(book.get("author", "")))

    if review_author and book_author and review_author == book_author:
        return "같은 작가의 다른 작품이에요."

    return None


def _build_reason_for_book(
    book: dict,
    review_book,
    keywords: list[str],
    index: int,
) -> str:
    fixed_reason = _fixed_reason_for_book(book, review_book, keywords)
    if fixed_reason:
        return fixed_reason

    keyword_reason = _reason_from_keywords(_rotate_keywords(keywords, index))
    if keyword_reason:
        return keyword_reason

    if keywords:
        return f"리뷰에서 느낀 '{keywords[index % len(keywords)]}' 분위기와 잘 맞는 책이에요."

    return "리뷰 분위기와 잘 맞는 책이에요."


def _rotate_keywords(keywords: list[str], index: int) -> list[str]:
    if not keywords:
        return []
    if index <= 0:
        return keywords
    pivot = index % len(keywords)
    return keywords[pivot:] + keywords[:pivot]


def _normalize_author(name: str) -> str:
    if not name:
        return ""
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\s+", "", name)
    return name.strip()


def _reason_from_keywords(keywords: list[str]) -> str | None:
    if not keywords:
        return None

    keyword_map = {
        "역사적 사건": "아픈 역사적 사건을 담담한 문체로 풀어냈어요.",
        "아픔의 기억": "아픔의 기억을 조용히 들여다보는 책이에요.",
        "무거운 분위기": "무거운 분위기를 끝까지 놓지 않고 이어가요.",
        "기억": "기억을 곱씹게 되는 책이에요.",
        "슬픔": "슬픔의 결을 차분히 따라가는 책이에요.",
        "분노": "분노의 감정을 절제된 문장으로 담아냈어요.",
        "소년": "소년의 시선과 정서를 떠올리게 해요.",
        "잔인함": "잔인한 현실을 담담하게 비추는 책이에요.",
        "감정": "감정의 흐름을 섬세하게 따라가요.",
        "여운": "읽고 난 뒤 여운이 오래 남는 책이에요.",
    }

    for keyword in keywords:
        if keyword in keyword_map:
            return keyword_map[keyword]

    return None


LITERATURE_TEMPLATES = [
    "이 책은 조용히 마음 가까이 다가와 오래 머무는 이야기를 들려줍니다.",
    "이 책은 한 장면 한 장면이 마음에 천천히 내려앉습니다.",
    "이 책은 말없이 감정을 건네며 독자를 따라옵니다.",
    "이 책은 읽는 동안보다 덮은 뒤에 더 깊이 스며듭니다.",
    "이 책은 마음 한편을 살짝 건드리는 순간들로 가득합니다.",
    "이 책은 크게 말하지 않지만, 분명한 감정을 남깁니다.",
    "이 책은 감정을 설명하지 않고 그대로 놓아둡니다.",
    "이 책은 조용한 문장으로 마음을 오래 붙잡습니다.",
    "이 책은 쉽게 잊히지 않는 장면을 남깁니다.",
    "이 책은 마음으로 천천히 읽게 되는 이야기입니다.",
]

HISTORY_TEMPLATES = [
    "이 책은 과거의 이야기를 조용히 불러와 지금의 마음에 놓아줍니다.",
    "이 책은 사건을 넘어, 그 시대의 숨결을 따라가게 합니다.",
    "이 책은 시간을 거슬러 사람들의 삶 가까이 다가갑니다.",
    "이 책은 지나간 이야기를 차분히 바라볼 시간을 건넵니다.",
    "이 책은 과거를 단정하지 않고, 조용히 생각하게 합니다.",
    "이 책은 우리가 서 있는 자리를 다시 한 번 돌아보게 합니다.",
    "이 책은 세상을 바라보는 시선을 조금 느리게 만듭니다.",
    "이 책은 복잡한 이야기 속에서도 사람을 놓치지 않습니다.",
    "이 책은 생각의 방향을 부드럽게 틀어줍니다.",
    "이 책은 오래 곱씹게 되는 질문을 남깁니다.",
]

SCIENCE_TEMPLATES = [
    "이 책은 낯설게 느껴졌던 개념을 차분히 가까이 데려옵니다.",
    "이 책은 복잡한 이야기를 하나씩 풀어내며 안심시켜 줍니다.",
    "이 책은 이해의 속도를 재촉하지 않습니다.",
    "이 책은 개념을 따라가며 자연스럽게 고개를 끄덕이게 합니다.",
    "이 책은 알고 싶다는 마음을 부담 없이 이어줍니다.",
    "이 책은 생각의 매듭을 천천히 풀어줍니다.",
    "이 책은 어려운 이야기도 조심스럽게 설명합니다.",
    "이 책은 이해하는 과정 자체를 존중합니다.",
    "이 책은 지식을 쌓는 시간을 편안하게 만들어 줍니다.",
    "이 책은 배움에 대한 긴장을 조금 내려놓게 합니다.",
]

WORKBOOK_TEMPLATES = [
    "이 책은 공부의 흐름을 조용히 곁에서 잡아줍니다.",
    "이 책은 혼자 공부하는 시간을 덜 막막하게 만들어 줍니다.",
    "이 책은 서두르지 않고 차근차근 나아가게 합니다.",
    "이 책은 학습의 리듬을 부드럽게 유지해 줍니다.",
    "이 책은 부담을 덜어낸 구성으로 함께 걸어갑니다.",
    "이 책은 반복 속에서도 지치지 않게 배려합니다.",
    "이 책은 공부의 방향을 잃지 않게 도와줍니다.",
    "이 책은 혼자서도 충분히 따라갈 수 있도록 곁을 지킵니다.",
    "이 책은 매일 조금씩 이어가기 좋습니다.",
    "이 책은 공부가 혼자가 아니라는 느낌을 줍니다.",
]

ECONOMY_TEMPLATES = [
    "이 책은 복잡한 생각을 차분히 정리할 수 있게 돕습니다.",
    "이 책은 현실을 마주하는 방식을 조금 부드럽게 바꿔줍니다.",
    "이 책은 스스로를 돌아볼 시간을 만들어 줍니다.",
    "이 책은 삶의 방향을 조용히 점검하게 합니다.",
    "이 책은 지금의 고민을 천천히 내려놓게 합니다.",
    "이 책은 생각을 정돈하며 읽기 좋습니다.",
    "이 책은 삶에 바로 닿는 이야기들을 담고 있습니다.",
    "이 책은 부담 없이 곱씹어 볼 지점을 건넵니다.",
    "이 책은 일상 속 선택을 다시 생각하게 합니다.",
    "이 책은 조용히 삶의 균형을 돌아보게 합니다.",
]

LIFE_TEMPLATES = [
    "이 책은 일상 가까이에서 천천히 도움을 건넵니다.",
    "이 책은 생활 속에서 바로 떠올리기 좋습니다.",
    "이 책은 필요할 때 곁에 두고 펼치기 좋습니다.",
    "이 책은 무리하지 않고 실천할 수 있는 이야기를 담고 있습니다.",
    "이 책은 삶의 리듬을 부드럽게 정리해 줍니다.",
    "이 책은 생활을 조금 더 편안하게 바라보게 합니다.",
    "이 책은 작은 습관을 돌아보게 합니다.",
    "이 책은 일상에 자연스럽게 스며듭니다.",
    "이 책은 꾸준히 곁에 두기 좋습니다.",
    "이 책은 생활의 숨을 고르게 해줍니다.",
]

KIDS_TEMPLATES = [
    "이 책은 이야기를 따라가며 자연스럽게 마음을 엽니다.",
    "이 책은 부담 없이 호기심을 키워줍니다.",
    "이 책은 처음 만나는 이야기로 잘 어울립니다.",
    "이 책은 천천히 이해해도 괜찮다고 말해줍니다.",
    "이 책은 생각하는 재미를 살짝 건넵니다.",
    "이 책은 이야기를 통해 자연스럽게 다가옵니다.",
    "이 책은 읽는 시간을 편안하게 만들어 줍니다.",
    "이 책은 친근한 방식으로 마음을 엽니다.",
    "이 책은 호기심이 이어지도록 도와줍니다.",
    "이 책은 처음부터 부담을 주지 않습니다.",
]

TRAVEL_TEMPLATES = [
    "이 책은 장면을 따라 천천히 걸어가듯 읽힙니다.",
    "이 책은 잠시 다른 곳에 다녀온 기분을 줍니다.",
    "이 책은 시선을 환기시키는 순간을 건넵니다.",
    "이 책은 분위기를 느끼며 넘기기 좋습니다.",
    "이 책은 감각을 조용히 깨워줍니다.",
    "이 책은 일상에서 잠시 벗어나게 합니다.",
    "이 책은 장면 하나하나를 음미하게 합니다.",
    "이 책은 마음을 가볍게 열어줍니다.",
    "이 책은 천천히 즐기기 좋은 책입니다.",
    "이 책은 감각적인 여운을 남깁니다.",
]

ETC_TEMPLATES = [
    "이 책은 필요할 때 자연스럽게 손이 갑니다.",
    "이 책은 곁에 두고 오래 보기 좋습니다.",
    "이 책은 목적에 맞게 편안하게 활용할 수 있습니다.",
    "이 책은 생활의 한 부분처럼 자리 잡습니다.",
    "이 책은 부담 없이 펼쳐보기 좋습니다.",
]

CATEGORY_ID_TO_TEMPLATES = {
    12: LITERATURE_TEMPLATES,
    15: LITERATURE_TEMPLATES,
    25: LITERATURE_TEMPLATES,
    17: HISTORY_TEMPLATES,
    11: HISTORY_TEMPLATES,
    21: HISTORY_TEMPLATES,
    6: SCIENCE_TEMPLATES,
    7: SCIENCE_TEMPLATES,
    9: SCIENCE_TEMPLATES,
    4: WORKBOOK_TEMPLATES,
    29: WORKBOOK_TEMPLATES,
    31: WORKBOOK_TEMPLATES,
    13: WORKBOOK_TEMPLATES,
    3: ECONOMY_TEMPLATES,
    23: ECONOMY_TEMPLATES,
    1: LIFE_TEMPLATES,
    2: LIFE_TEMPLATES,
    28: LIFE_TEMPLATES,
    14: KIDS_TEMPLATES,
    20: KIDS_TEMPLATES,
    30: KIDS_TEMPLATES,
    16: TRAVEL_TEMPLATES,
    18: TRAVEL_TEMPLATES,
    8: ETC_TEMPLATES,
    22: ETC_TEMPLATES,
    24: ETC_TEMPLATES,
    26: ETC_TEMPLATES,
}
