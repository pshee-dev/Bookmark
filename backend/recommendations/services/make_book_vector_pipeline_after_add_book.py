import json
import os
import threading
from typing import Optional

import requests
from django.conf import settings
from django.db import close_old_connections
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from books.models import Book
from recommendations.models import BookVector

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
VECTOR_DB_ROOT = os.path.join(settings.BASE_DIR, "vectordb")
VECTOR_DB_DIR = os.path.join(VECTOR_DB_ROOT, "openai_large")

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

# 외부에서 호출하는 함수로, 비동기 처리의 진입점이다.
def enqueue_book_vector_build(book_id: int) -> None:

    thread = threading.Thread( # 메인 요청 흐름을 막지 않도록 새 스레드 생성
        target=_build_book_vector,
        args=(book_id,),
        daemon=True, # 서버 종료 시 같이 종료
    )
    thread.start() # 실제 비동기 실행

# 책 하나 → 요약 → 임베딩 → DB + Chroma 저장까지의 벡터 생성 파이프라인
def _build_book_vector(book_id: int) -> None:

    close_old_connections() # 기존 DB 커넥션 재사용으로 인한 에러 방지 (스레드 환경 필수)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist: # 책이 없다면 예외 던지지 않고 종료
        return
    if not book.isbn: # ISBN 없는 책은 외부 요약 불가하므로 백터 생성 대상에서 제외
        return

    ## TODO 크롤링 파이프라인 추가
        ## TODO aladin 리뷰 크롤링 파이프라인
        ## TODO 교보문고 리뷰 크롤링 파이프라인
        ## TODO 교보문고 출판사 서평 크롤링 파이프라인



    # TODO 요약 파이프라인 추가
    summary = None # 요약된 텍스트
    if not summary:
        return

    # TODO 임베딩 파이프라인 추가
    emb = _embed_text(summary) # GMS OpenAI를 호출하여 텍스트데이터를 임베딩
    if not emb:
        return

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
    _upsert_chroma(book, summary, emb)


def _fetch_book_summary(isbn: str) -> str:
    if not isbn:
        return ""
    from books.services import book_search_service
    try:
        data = book_search_service.fetch_google_books_api(
            {"q": f"isbn:{isbn}", "key": book_search_service.GOOGLE_BOOKS_API_KEY}
        )
    except Exception:
        return ""

    items = data.get("items") or []
    if not items:
        return ""
    info = items[0].get("volumeInfo") or {}
    description = info.get("description") or ""
    return _clean_text(description)


def _fallback_summary(book: Book) -> str:
    parts = [
        book.title or "",
        book.author or "",
        book.publisher or "",
    ]
    return _clean_text(" ".join([p for p in parts if p]))


def _clean_text(text: str) -> str:
    text = (text or "").strip()
    return text[:1500]


def _embed_text(text: str) -> Optional[list[float]]:
    api_key = os.getenv("GMS_KEY")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "input": [text],
    }
    try:
        r = requests.post(OPENAI_EMBED_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["data"][0]["embedding"]
    except Exception:
        return None

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
