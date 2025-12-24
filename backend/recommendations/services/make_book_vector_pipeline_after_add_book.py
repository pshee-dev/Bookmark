import json
import os
import threading
import time

from django.conf import settings
from django.db import close_old_connections
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from books.models import Book
from recommendations.models import BookVector
from recommendations.my_source.crollers.aladin_croller.get_reviews_from_aladin import (
    get_aladin_item_id,
    crawl_short_reviews as aladin_crawl_short_reviews,
)
from recommendations.my_source.crollers.kyobo_crollers.get_reviews_from_kyobo import (
    get_kyobo_product_id,
    crawl_kyobo_reviews_selenium,
)
from recommendations.my_source.crollers.kyobo_crollers.get_kyobo_publisher_review import (
    get_kyobo_product_id as get_kyobo_publisher_product_id,
    crawl_kyobo_book_descriptions,
)
from recommendations.my_source.summary.summarizer.summarize_aladin_short_reviews import (
    summarize_aladin_short_reviews,
)
from recommendations.my_source.summary.summarizer.summarize_kyobo_reviews import (
    summarize_kyobo_reviews,
)
from recommendations.my_source.summary.summarizer.summarize_kyobo_publisher_reviews import (
    summarize_kyobo_publisher_reviews,
)
from recommendations.my_source.embeddings import make_embeddings


# Model + vector DB config
# 차원 수가 크고(3072) 정확도가 높은 OpenAI 임베딩 모델
MODEL_NAME = "text-embedding-3-large"

# 이 벡터가 어떤 공급자 + 어떤 모델로 만들어졌는지를 명시하는 식별자
PROVIDER_MODEL_KEY = "gms-openai::text-embedding-3-large"

# Chroma 내부 collection 이름으로, openai_large 임베딩만 담는 컬렉션의 논리적 이름
COLLECTION_NAME = "reviews_openai_large"

# 벡터 DB를 Django 프로젝트 내부에 파일로 저장할 때의 경로설정
    # - project/vectordb/openai_large/chroma.sqlite3 <- 메타데이터 + 내부 관리 데이터 DB
    # - project/vectordb/openai_large/index/ <- 실제 벡터 검색을 위한 고속 인덱스 (사람이 읽을 수 있는 데이터가 아님)
    # - 서버를 재시작해도 벡터가 유지(persist)된다.
VECTOR_DB_DIR = os.path.join(
    settings.BASE_DIR,
    "recommendations",
    "vector_db",
    "openai_large_test",
    "Book_vector_db",
)

# GMS OpenAI Gateway
OPENAI_EMBED_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"

# LangChain의 Embeddings 인터페이스 구현
    # - 임베딩을 내가 직접 계산해서 넣겠다는 선언
class PrecomputedEmbedding(Embeddings):

    # 벡터 차원 수 저장
        # - Chroma는 내부적으로 차원 정보를 필요로 한다.
    def __init__(self, dim: int | None):
        self.dim = dim

    # LangChain이 자동으로 임베딩 생성하지 못하게 차단한다.
    def embed_documents(self, texts):
        raise RuntimeError("Precomputed embeddings only") # 랭체인이 임베딩 생성시 에러

    # 검색 시에도 LangChain이 자동 임베딩 생성하지 못하게 차단한다.
        # - 쿼리 임베딩도 직접 생성하고자 한다.
        # - LangChain은 저장소 역할만 하고, 임베딩 생성은 우리 서비스가 수행하겠다는 것.
    def embed_query(self, text):
        raise RuntimeError("Query embedding must be generated separately")

# ================================================================
#  1) 외부에서 호출하는 함수로, 비동기 처리의 진입점
# ================================================================

def enqueue_book_vector_build(isbn: str) -> None:

    thread = threading.Thread( # 메인 요청 흐름을 막지 않도록 새 스레드 생성
        target=_build_book_vector,
        args=(isbn,),
        daemon=True, # 서버 종료 시 같이 종료
    )
    thread.start() # 실제 비동기 실행


#  << 책 하나 → 요약 → 임베딩 → DB + Chroma 저장까지의 벡터 생성 파이프라인 >>
def _build_book_vector(isbn: str) -> None:

    close_old_connections() # 기존 DB 커넥션 재사용으로 인한 에러 방지 (스레드 환경 필수)

    if not isbn: # ISBN 없는 책은 크롤링, 외부 요약 불가하므로 백터 생성 대상에서 제외
        return

    book = None
    for _ in range(5):
        book = Book.objects.filter(isbn=isbn).first()
        if book:
            break
        time.sleep(0.5)
    if not book:
        return

    print(f"[debug] start isbn={isbn}")

    # ================================================================
    #  2) 크롤링 시작
    # ================================================================
    item_id = get_aladin_item_id(isbn)
    if item_id:
        aladin_short_reviews = aladin_crawl_short_reviews(item_id, isbn, max_pages=1)
    else:
        aladin_short_reviews = []

    kyobo_reviews = []
    try:
        product_id = get_kyobo_product_id(isbn)
        if product_id:
            kyobo_reviews = crawl_kyobo_reviews_selenium(product_id, isbn)
    except Exception:
        kyobo_reviews = []

    kyobo_publisher_reviews = []
    try:
        product_id = get_kyobo_publisher_product_id(isbn)
        if product_id:
            kyobo_publisher_reviews = crawl_kyobo_book_descriptions(product_id, isbn)
    except Exception:
        kyobo_publisher_reviews = []

    print(
        f"[debug] aladin_count={len(aladin_short_reviews)} "
        f"kyobo_count={len(kyobo_reviews)} "
        f"kyobo_pub_count={len(kyobo_publisher_reviews)}"
    )


    # ================================================================
    #  3) 리뷰 전처리 (요약)
    # ================================================================

    aladin_texts = [
        review["review_text"]
        for review in aladin_short_reviews
        if review.get("review_text")
    ]
    kyobo_texts = [
        review["review_text"]
        for review in kyobo_reviews
        if review.get("review_text")
    ]
    kyobo_publisher_texts = [
        review["review_text"]
        for review in kyobo_publisher_reviews
        if review.get("review_text")
    ]

    aladin_summary = summarize_aladin_short_reviews(aladin_texts) if aladin_texts else {}
    kyobo_summary = summarize_kyobo_reviews(kyobo_texts) if kyobo_texts else {}
    kyobo_publisher_summary = (
        summarize_kyobo_publisher_reviews(kyobo_publisher_texts)
        if kyobo_publisher_texts
        else {}
    )

    print(
        f"[debug] aladin_summary_len={len(aladin_summary.get('summary',''))} "
        f"kyobo_summary_len={len(kyobo_summary.get('summary',''))} "
        f"kyobo_pub_summary_len={len(kyobo_publisher_summary.get('summary',''))}"
    )


    # ================================================================
    #  4) 요약결과 임베딩
    # ================================================================

    summary_parts = [
        aladin_summary.get("summary", ""),
        kyobo_summary.get("summary", ""),
        kyobo_publisher_summary.get("summary", ""),
    ]
    summary_text = _clean_text(" ".join([p for p in summary_parts if p]))
    if not summary_text:
        return

    print(f"[debug] final_summary_len={len(summary_text)}")

    emb = make_embeddings(summary_text) # GMS OpenAI를 호출하여 텍스트데이터를 임베딩
    if not emb:
        return

    # ================================================================
    #  5) 임베딩 -> 벡터화
    # ================================================================

    # 책당 하나의 벡터 DB
        # - 벡터 DB(Chroma 컬렉션)는 하나지만 그 안에 문서(=벡터)는 여러 개 있을 수 있는 것.
    BookVector.objects.update_or_create(
        book=book, # book이 unique key 역할을 한다.
        defaults={
            "vector": json.dumps(emb), # float 배열을 JSON 문자열로 저장
            "embedding_model": PROVIDER_MODEL_KEY, # 이 벡터가 어떤 모델인지 명시
            "embedding_dim": len(emb), # 벡터의 차원 (추후 검증 / 마이그레이션 시 사용)
        },
    )

    # 파일 기반 벡터 DB에 저장
    _upsert_chroma(book, summary_text, emb)








# 공백 제거
def _clean_text(text: str) -> str:
    text = (text or "").strip()
    return text[:1500]


# 파일 기반 벡터 DB에 저장
def _upsert_chroma(book: Book, summary: str, emb: list[float]) -> None:

    os.makedirs(VECTOR_DB_DIR, exist_ok=True) # 디렉터리가 없다면 생성
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DB_DIR,
        embedding_function=PrecomputedEmbedding(len(emb)),
    )

    doc = Document(

        # 검색 시 반환될 텍스트로, 나중에 RAG에서 그대로 LLM에 들어간다.
            # - LLM에 들어갈 프롬프트의 일부(context)인 것.
        page_content=summary,

        # 필터링 / 디버깅 / 재색인 시 핵심 메타데이터
        metadata={
            "isbn13": book.isbn,
            "model": PROVIDER_MODEL_KEY,
        },
    )

    # Chroma document id.
        # ISBN을 전역 유니크 키로 사용하게 된다.
    book_id = str(book.isbn)
    try:
        # 기존 벡터 삭제
        vectordb._collection.delete(ids=[book_id])
    except Exception:
        pass

    vectordb._collection.add( # documents / metadatas / embeddings / ids 모두 길이가 같아야 한다.
        documents=[doc.page_content],
        metadatas=[doc.metadata],
        embeddings=[emb],
        ids=[book_id],
    )

    # 디스크에 저장하여, 서버 재시작 후에도 유지되도록 한다.
    vectordb.persist()



