from dotenv import load_dotenv
import os
from ..errors import *
import requests
from common.utils.safe_convert import str_to_int
from .book_thumnails_service import fetch_google_books_thumbnail
from ..models import ExternalCategoryMapping

load_dotenv()
session = requests.Session()

ALADIN_API_KEY = os.getenv("ALADIN_API_KEY")
ALADIN_VERSION = "20131101"
ALADIN_SEARCH_TARGET = "Book" # 국내도서로 검색결과 제한
ALADIN_ITEM_SEARCH_URL = "https://www.aladin.co.kr/ttb/api/"

#TODO 검색결과 개편: 검색 시 세트상품이 걸리지 않도록 자체 페이지네이션 구축. 세트상품의 경우 isbn값이 빈 문자열인 점을 이용.

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
    # 유효성검사
    if len(keyword) < 2:
        raise InvalidQuery(user_message="검색어는 2글자 이상 입력해주세요.")
    if field not in ("title", "author"):
        raise InvalidQuery(user_message="검색 타입이 올바르지 않습니다.")
    max_result = str_to_int(max_result, default=10)
    page = str_to_int(page, default=1)

    if not ALADIN_API_KEY:
        raise MissingTTBKey(dev_message="알라딘 API Key 누락")

    query_type = {
        "title": "Title",
        "author": "Author",
    }.get(field, "Title") # 검색필드 기본값: 책 제목(title)
    
    params = {
        "ttbkey": ALADIN_API_KEY,         
        "Query": keyword,                 # 검색어
        "QueryType": query_type,          # 검색필드 (Title / Author) 
        "MaxResults": max_result,         # 페이지당 최대 결과 수
        "start": page,                    # 페이지 번호
        "SearchTarget": ALADIN_SEARCH_TARGET,  # 불러올 아이템 종류(기본값: book)
        "output": "js",                   # 응답 타입
        "Version": ALADIN_VERSION,        # API 버전
        ### 필요시 아래 옵션 추가 ###
        # "Cover": "Mid",                 # 표지 이미지 크기 옵션
        # "outofStockfilter": 1,          # 품절 제외 옵션
        # "Omitkey": 1,                   # 결과 링크에 키 노출 제거 옵션
    }
    
    try:
        # timeout: 알라딘이 느릴 때 무한정 기다리지 않도록 제한하는 값
        response = session.get(ALADIN_ITEM_SEARCH_URL+'ItemSearch.aspx', params=params, timeout=2)
        # HTTP 상태코드가 200대가 아니면 예외 발생
        response.raise_for_status()
        # output=js로 JSON을 기대하므로 json()으로 파싱
        json_parsed_data = response.json()
    except requests.Timeout as e:
        raise TimeoutError(dev_message="알라딘 API 응답 시간 초과", cause=e)
    except requests.RequestException as e:
        raise ExternalAPIError(dev_message="알라딘 API 호출 실패", cause=e) 
    except ValueError as e:
        raise ExternalAPIError(dev_message="알라딘 API 응답 -> JSON 변환 실패", cause=e) 
    
    page_size = len(json_parsed_data["item"])
    total_size = json_parsed_data["totalResults"]
    has_next = (max_result*(page-1))+page_size < total_size 
    results = []
    for book in json_parsed_data["item"]:
        title = book["title"]
        thumbnail_url = fetch_google_books_thumbnail(title)
        small_sized_thumbnail_url = thumbnail_url.get("smallThumbnail")
            
        results.append({
            "title" : title,
            "isbn" : book["isbn13"],
            "author" : book["author"],
            "published_date" : book["pubDate"],
            "thumbnail" : small_sized_thumbnail_url,
            "categoryId" : book["categoryId"],
            ### 추후 필요 시 추가
            #"adult": book["adult"],
            #"salesPoint": book["salesPoint"],
            #"priceSales": book["priceSales"],
            #"priceStandard": book["priceStandard"],
        })

    return {
            "query": keyword,        # 사용자가 검색한 검색어
            "field": field,          # 검색한 필드(title/author)
            "page": page,            # 현재 페이지
            "page_size": page_size,  # 현재 조회한 페이지에 들어있는 요소 개수
            "total": total_size,     # 전체 결과 개수
            "has_next": has_next,    # 더보기 버튼 노출 여부
            "results": results       # 결과 목록
        }

def fetch_aladin_info_by_isbn(isbn: str) -> dict | None:
    """
    알라딘 TTB API를 이용해
    - 제목(title)
    - 저자(author)
    - 출판사(publisher)
    - 표지(cover)
    - 페이지 수(itemPage)
    를 가져오는 함수.

    정상적으로 가져오면 dict 반환,
    실패하면 None 반환.
    """
    
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
    if not items: 
        raise NotFoundError(dev_message='isbn과 일치하는 알라딘 도서 부재')
    item = items[0]
    title = item.get("title")
    
    thumbnail_url = fetch_google_books_thumbnail(title).get("thumbnail")
    cid = int(item.get("categoryId"))
    category_mapping = ExternalCategoryMapping.objects.get(external_cid=cid) #TODO 일치하는 카테고리 없는 경우 에러처리, 알라딘이 아닌 경우 분기
    category = category_mapping.category
    return {
        "isbn": isbn,
        "title": title,
        "author": item.get("author"),          
        "publisher": item.get("publisher"),
        "page": item.get("subInfo").get('itemPage'),
        "category_id": category.pk,
        "published_date": item.get('pubDate'),
        "thumbnail": thumbnail_url
    }
    
