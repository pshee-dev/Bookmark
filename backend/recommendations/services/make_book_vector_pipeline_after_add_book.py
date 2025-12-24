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
from recommendations.my_source.aladin_croller.get_reviews_from_aladin import (
    get_aladin_item_id,
    crawl_short_reviews as aladin_crawl_short_reviews,
)
from recommendations.my_source.summary.summarizer.summarize_aladin_short_reviews import (
    summarize_aladin_short_reviews,
)
from recommendations.my_source.embeddings import make_embeddings
from bs4 import BeautifulSoup


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

    book = Book.objects.filter(isbn=isbn).first()

    # ================================================================
    #  2) 알라딘 100자평 크롤링 시작
    # ================================================================
    item_id = get_aladin_item_id(isbn)
    if not item_id:
        return
    crawled_reviews = aladin_crawl_short_reviews(item_id, isbn, max_pages=1)

    #test 크롤링 잘 됐는지 테스트 print(crawled_reviews)


    # ================================================================
    #  3) 알라딘 100자평 전처리 (요약)
    # ================================================================

    review_texts = [
        review["review_text"]
        for review in crawled_reviews
        if review.get("review_text")
    ]
    striped_text = _clean_text(" ".join(review_texts))

    summarized_texts = summarize_aladin_short_reviews(review_texts)

    if not summarized_texts:
        summary = _fetch_book_summary(isbn) or (_fallback_summary(book) if book else "")
        return


    # ================================================================
    #  4) 요약결과 임베딩
    # ================================================================

    emb = make_embeddings(summarized_texts) # GMS OpenAI를 호출하여 텍스트데이터를 임베딩
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
    _upsert_chroma(book, summarized_texts, emb)


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


def _croll_aladin_reviews(isbn: str, max_pages: int = 2) -> list[str]:
    item_id = None#get_aladin_item_id(isbn)#임시
    if not item_id:
        return []

    reviews = crawl_short_reviews(item_id, isbn, max_pages=max_pages)
    return [review["review_text"] for review in reviews if review.get("review_text")]


def _fallback_summary(book: Book) -> str:
    parts = [
        book.title or "",
        book.author or "",
        book.publisher or "",
    ]
    return _clean_text(" ".join([p for p in parts if p]))


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



# ================================
#  100자평 크롤링
# ================================
def crawl_short_reviews(item_id, isbn, max_pages=1):

    reviews = []

    for page in range(1, max_pages + 1):

        url = (
            "https://www.aladin.co.kr/ucl/shop/product/ajax/GetCommunityListAjax.aspx"
            f"?ProductItemId={item_id}"
            f"&itemId={item_id}"
            f"&pageCount={max_pages}"
            "&communitytype=CommentReview"
            "&nemoType=-1"
            f"&page={page}"
            "&startNumber=1"
            "&endNumber=10"
            "&sort=2"
            "&IsOrderer=1"
            "&BranchType=1"
            "&IsAjax=true"
            "&pageType=0"
        )

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={item_id}",
            "X-Requested-With": "XMLHttpRequest"
        }
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        li_blocks = soup.select("li")

        if not li_blocks:
            print("⚠️ 100자평 AJAX 응답 없음 → 중단")
            break

        #  2개 li가 한 세트이므로 2칸씩 점프
        for i in range(0, len(li_blocks), 2):

            try:

                content_li = li_blocks[i]
                meta_li = li_blocks[i + 1]

                #  리뷰 본문 (스포일러 제외)
                text_tag = content_li.select_one(
                    "span[id^='spnPaper']:not([id*='Spoiler'])"
                )
                review_text = text_tag.text.strip() if text_tag else None

                #  블로그 링크
                blog_tag = content_li.select_one("a[href*='blog.aladin.co.kr']")
                blog_url = blog_tag["href"] if blog_tag else None

                # ⭐ 별점 (img 개수 기반, div.hundred_list 기준)
                hundred_box = content_li.find_parent("div", class_="hundred_list")

                if hundred_box:
                    star_tag = hundred_box.select_one("div.HL_star")

                    if star_tag:
                        star_imgs = star_tag.find_all("img")
                        star_on_count = sum(
                            1 for img in star_imgs
                            if "icon_star_on" in img.get("src", "")
                        )
                        rating = star_on_count * 2   # ✅ 10점 환산
                    else:
                        rating = None
                else:
                    rating = None


                #  날짜
                date_tag = meta_li.select_one("div.left span")
                review_date = date_tag.text.strip() if date_tag else None

                if review_text:
                    reviews.append({
                        "isbn13": isbn,
                        "source": "aladin_short",
                        "review_text": review_text,
                        "rating": rating,
                        "review_date": review_date,
                        "blog_url": blog_url
                    })

            except IndexError:
                continue   # ✅ 홀수 깨질 때 안전 처리

        time.sleep(1.5)

    return reviews
