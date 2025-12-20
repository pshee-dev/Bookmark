from dotenv import load_dotenv
import os
from ..errors import *
import requests
from common.utils.safe_convert import str_to_int
from ..models import ExternalCategoryMapping, Category

load_dotenv()
session = requests.Session()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
GOOGLE_BOOKS_SEARCH_URL = "https://www.googleapis.com/books/v1/volumes/"

ALADIN_API_KEY = os.getenv("ALADIN_API_KEY")
ALADIN_VERSION = "20131101"
ALADIN_SEARCH_TARGET = "Book" # 국내도서로 검색결과 제한
ALADIN_ITEM_SEARCH_URL = "https://www.aladin.co.kr/ttb/api/"

# 알라딘 api를 통해 사용자 검색어의 검색결과 리스트 반환 
def search_books(keyword, field, max_result, page):
    """
    검색조건들을 문자열로 받아, 해당 키워드의 검색결과인 도서 정보 리스트를 반환한다.
    \n
    검색어(keyword), 
    검색필드(field), 
    페이지당 최대 개수(max_result), 
    조회할 페이지(page), 
    """
    # 입력 값 검증
    if len(keyword) < 2:
        raise InvalidQuery(user_message="검색어는 2글자 이상 입력해주세요.")

    if field not in ("title", "author"):
        raise InvalidQuery(user_message="검색 타입이 올바르지 않습니다.")

    max_result = str_to_int(max_result, default=10)
    max_result = max(1, min(max_result, 40))  # 1과 40 사이로 제한

    field_map = {
        "title": "intitle",
        "author": "inauthor",
    }
    field = field_map.get(field, "intitle")  # 기본적으로 제목(title) 검색
    page = str_to_int(page, default=1)

    if not GOOGLE_BOOKS_API_KEY:
        raise MissingTTBKey(dev_message="구글북스 API Key 누락")

    params = {
        "q": f"{field}:{keyword}",
        "maxResults": max_result,
        "printType": "books",
        "startIndex": page,
        "key": GOOGLE_BOOKS_API_KEY,
    }

    # api 응답 받아오기
    try:
        # timeout: api가 느릴 때 무한정 기다리지 않도록 제한하는 값
        response = session.get(GOOGLE_BOOKS_SEARCH_URL, params=params, timeout=2)
        # HTTP 상태코드가 200대가 아니면 예외 발생
        response.raise_for_status()
        # output=js로 JSON을 기대하므로 json()으로 파싱
        json_parsed_data = response.json()
        print(response.request.url)
    except requests.Timeout as e:
        raise TimeoutError(dev_message="구글북스 API 응답 시간 초과", cause=e)
    except requests.RequestException as e:
        raise ExternalAPIError(dev_message="구글북스 API 호출 실패", cause=e)
    except ValueError as e:
        raise ExternalAPIError(dev_message="구글북스 API 응답 -> JSON 변환 실패", cause=e)

    if not json_parsed_data["items"]:
        return {
            "keyword": "",        # 사용자가 검색한 검색어
            "field": "",          # 검색한 필드(title/author)
            "page": 1,            # 현재 페이지
            "page_size": 0,  # 현재 조회한 페이지에 들어있는 요소 개수
            "results": [],       # 결과 목록
        }
    page_size = len(json_parsed_data["items"])
    # total_size = json_parsed_data["totalItems"] 구글북스의 토탈사이즈는 정확하지 않음.

    results = []

    for book in json_parsed_data["items"]:
        volume_info = book.get("volumeInfo") or {}
        if not volume_info:
            continue

        title = volume_info.get("title") or ""
        authors = volume_info.get("authors") or []
        authors = ', '.join(authors)
        published_date = volume_info.get("publishedDate") or ""
        all_book_isbns = volume_info.get("industryIdentifiers") or {}
        book_page = volume_info.get("pageCount") or -1 # 결측치 임시 처리

        isbn_13 = ""
        for isbn_N in all_book_isbns: # ISBN 종류
            if isbn_N.get("type") == "ISBN_13":
                isbn_13 = isbn_N.get("identifier")
                break
        if not isbn_13: # isbn13이 결측치라면 검색결과에 추가하지 않고 넘어감
            continue

        category = get_aladin_category_cid_by_isbn_13(isbn_13)
        thumbnail_url_set = volume_info.get("imageLinks") or {}
        # Google Books가 주는 대표 키들 (항상 있는 건 아님)
        thumbnail_url = (
                thumbnail_url_set.get("thumbnail")
                or thumbnail_url_set.get("small")
                or thumbnail_url_set.get("smallThumbnail")
                or thumbnail_url_set.get("medium")
                or thumbnail_url_set.get("large")
                or thumbnail_url_set.get("extraLarge")
                or ""
        )

        results.append({
            "title" : title,
            "isbn" : isbn_13,
            "author" : authors,
            "published_date" : published_date,
            "thumbnail" : thumbnail_url,
            "category" : category,
            "page" : book_page,
        })

    return {
            "keyword": keyword,        # 사용자가 검색한 검색어
            "field": field,          # 검색한 필드(title/author)
            "current_page": page,            # 현재 페이지
            "page_size": page_size,  # 현재 조회한 페이지에 들어있는 요소 개수
            "results": results,       # 결과 목록
            }

def get_aladin_category_cid_by_isbn_13(isbn: str) -> Category:
    """
    도서 isbn 값을 이용해 cid 값을 찾아낸 후, 자체 카테고리로 매핑한다.
        - cid 값이 결측치이거나 자체 카테고리와 매핑되는 분류가 아닐 경우, pk 22(일본서적, 기타)인 Category로 매핑된다.
    반환값: Category
    """
    category_others = Category.objects.get(pk=22)
    if not isbn:
        raise InvalidIsbn(dev_message="isbn 파라미터 부재")

    params = {
        "ttbkey": ALADIN_API_KEY,    
        "itemIdType": "ISBN13",      
        "ItemId": isbn,            
        "output": "js",              
        "Version": ALADIN_VERSION,
        "OptResult": "itemPage",
        
    }

    try:
        res = session.get(ALADIN_ITEM_SEARCH_URL+'ItemLookUp.aspx', params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except requests.Timeout as e:
        raise TimeoutError(dev_message="알라딘 API 응답 시간 초과", cause=e)
    except requests.RequestException as e:
        raise ExternalAPIError(dev_message="알라딘 API 호출 실패", cause=e) 
    except ValueError as e:
        raise ExternalAPIError(dev_message="알라딘 API 응답 -> JSON 변환 실패", cause=e)

    items = data.get("item")

    if not items: # isbn과 일치하는 도서 부재 시 빈 딕셔너리 반환
        return category_others
    item = items[0]

    cid = item.get("categoryId")
    if not cid:
        return category_others
    category_mapping = ExternalCategoryMapping.objects.filter(external_cid=cid)
    if category_mapping:
        category = category_mapping[0].category
    else:
        category = category_others
    return category

    
