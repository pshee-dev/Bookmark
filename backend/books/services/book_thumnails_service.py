from dotenv import load_dotenv
import os
import requests
from ..errors import *

load_dotenv()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
GOOGLE_BOOKS_ENDPOINT = "https://www.googleapis.com/books/v1/volumes"

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
        response = requests.get(GOOGLE_BOOKS_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        return {"found": False, "reason": "timeout"}
    except requests.RequestException as e:
        return {"found": False, "reason": "request_error", "detail": str(e)}
    except ValueError:
        return {"found": False, "reason": "invalid_json"}
    
    items = data.get("items") or []
    if not items:
        return {"found": False, "reason": "not_found"}

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

    # 일부 링크는 http로 오기도 해서 https로 정리(가능하면)
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


if __name__ == "__main__":
    isbn = "9788937461637"
    result = fetch_google_books_thumbnail_by_isbn(isbn)