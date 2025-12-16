from dotenv import load_dotenv
import os
import requests
from ..errors import *

load_dotenv()
session = requests.Session()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
GOOGLE_BOOKS_ENDPOINT = "https://www.googleapis.com/books/v1/volumes"

# isbn 검색 시 검색결과에 썸네일이 누락되는 경우가 많아, isbn이 아닌 책 제목을 이용해 검색합니다. 
def fetch_google_books_thumbnail(title: str):
    """
    책 제목으로 Google Books 검색 → 썸네일 URL을 뽑아서 반환.
    반환 예시:
    {
        "found": True,
        "thumbnail": "...",
        "smallThumbnail": "...",
        "volume_id": "...",
        "title": "...",
        "authors": [...],
        "raw_imageLinks": {...}
    }
    """
    if not GOOGLE_BOOKS_API_KEY:
        raise MissingTTBKey(dev_message="구글북스 API Key 누락")

    params = {
        "q": f"{title}",
        "maxResults": 5, 
        "printType": "books", 
        "key": GOOGLE_BOOKS_API_KEY,
    }

    try:
        response = session.get(GOOGLE_BOOKS_ENDPOINT, params=params, timeout=2)
        response.raise_for_status()
        
        data = response.json()

    except requests.Timeout:
        raise TimeoutError(dev_message="구글북스 API 응답 시간 초과", cause=e)
    except requests.RequestException as e:
        raise ExternalAPIError(dev_message="구글북스 API 호출 실패", cause=e) 
    except ValueError:
        raise ExternalAPIError(dev_message="구글북스 API 응답 -> JSON 변환 실패", cause=e)
    
    items = data.get("items") or []
    
    if not items:
        return {}

    # 보통 첫 번째가 가장 잘 맞지만, 혹시 몰라 1~5개 중에서 imageLinks 있는 걸 우선 선택
    best = None
    for it in items:
        vi = it.get("volumeInfo") or {}
        if vi.get("imageLinks"):
            best = it
            break
    if best is None:
        best = items[0]

    vi = best.get("volumeInfo") or {}
    image_links = vi.get("imageLinks") or {}

    # Google Books가 주는 대표 키들 (항상 있는 건 아님)
    thumbnail = (
        image_links.get("thumbnail")
        or image_links.get("small")
        or image_links.get("smallThumbnail")
        or image_links.get("medium")
        or image_links.get("large")
        or image_links.get("extraLarge")
    )

    # http로 온 링크의 경우, https로 정리
    if isinstance(thumbnail, str) and thumbnail.startswith("http://"):
        thumbnail = "https://" + thumbnail[len("http://") :]

    return {
        "found": bool(thumbnail),
        "thumbnail": thumbnail,
        "smallThumbnail": image_links.get("smallThumbnail"),
        "volume_id": best.get("id"),
        "title": vi.get("title"),
        "authors": vi.get("authors") or [],
        "raw_imageLinks": image_links,
    }