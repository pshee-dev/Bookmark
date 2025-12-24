# ================================
#  0. 라이브러리 import
# ================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm


# ================================
#  1. 기본 설정
# ================================

crolling_platform = 'aladin'
crolling_data_type = 'reviews'

## TODO csv가 아닌, 동기 코드(books.views.resolve)에서 저장할 도서의 정보를 받아와 INPUT 값으로 사용하도록 변경
INPUT_CSV = f"final_books_top204.csv"   #  입력 csv

OUTPUT_CSV = f"{crolling_platform}_{crolling_data_type}.csv"      #  최종 리뷰 저장 CSV
#저장 형식: isbn13,source,review_text,rating,review_date,blog_url

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
#  알라딘은 User-Agent 없으면 응답이 불안정한 경우 있음


# ================================
#  2. CSV 로드
# ================================

books_df = pd.read_csv(INPUT_CSV)
print(f"✅ 총 {len(books_df)}권 로드 완료")


# ================================
# 3. ISBN → 알라딘 ItemId 추출
# ================================

def get_aladin_item_id(isbn):
    """
    ISBN으로 알라딘 검색 후,
    div.ss_book_box 내부의 첫 번째 도서 ItemId 추출
    """

    search_url = (
        "https://www.aladin.co.kr/search/wsearchresult.aspx"
        f"?SearchTarget=Book&SearchWord={isbn}"
    )
    res = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    book_boxes = soup.select("div.ss_book_box")

    if not book_boxes:
        print("ss_book_box 없음 → 검색 실패")
        return None

    # 첫 번째 책 박스만 선택
    box = book_boxes[0]

    # 그 안에서 wproduct.aspx 링크 찾기
    link = box.select_one("a[href*='wproduct.aspx?ItemId=']")

    if not link:
        print("❌ ss_book_box 안에 ItemId 링크 없음")
        return None
    
    href = link.get("href")
    item_id = href.split("ItemId=")[-1].split("&")[0]

    return item_id



# ================================
#  4. 100자평 크롤링
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

# ================================
#  5. 마이리뷰 크롤링
# ================================

def crawl_my_reviews(isbn, max_pages=50):

    reviews = []

    for page in range(1, max_pages + 1):

        url = (
            "https://www.aladin.co.kr/shop/product/getContents.aspx"
            f"?ISBN={isbn}"
            "&name=MyReview"
            "&type=0"
            f"&page={page}"
        )
        print(url)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.aladin.co.kr",
            "X-Requested-With": "XMLHttpRequest"
        }

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        review_boxes = soup.select("div.hundred_list")

        if not review_boxes:
            print("⚠️ 마이리뷰 더 이상 없음 → 중단")
            break

        for box in review_boxes:
            # 별점 계산
            star_tag = box.select_one("div.HL_star")

            if star_tag:
                star_imgs = star_tag.find_all("img")
                
                # on / off 상관없이 img 개수로 세는 방식
                star_on_count = sum(
                    1 for img in star_imgs 
                    if "icon_star_on" in img.get("src", "")
                )

                rating = star_on_count * 2   # 10점 만점으로 별점 환산
            else:
                rating = None

            #  짧은 리뷰
            short_tag = box.select_one("div[id^='divPaper']")
            review_text = short_tag.text.strip() if short_tag else None

            #  전체 리뷰 (더보기 눌렀을 때 나오는 것)
            full_tag = box.select_one("div[id^='paperAll_']")
            if full_tag and full_tag.text.strip():
                review_text = full_tag.text.strip()

            if review_text:
                reviews.append({
                    "isbn13": isbn,
                    "source": "aladin_myreview",
                    "review_text": review_text,
                    "rating": rating,
                    "review_date": None,
                    "blog_url": None
                })

        time.sleep(1.2)

    return reviews





# ================================
# 6. 전체 ISBN 순회
# ================================

all_reviews = []

print(" 알라딘 리뷰 크롤링 시작")

for idx, row in tqdm(books_df.iterrows(), total=len(books_df)):
    isbn = str(row["isbn13"]).strip()
    title = row["title"]

    print(f"\n📘 크롤링 중: {title} ({isbn})")

    # 1단계: ItemId 추출
    item_id = get_aladin_item_id(isbn)

    if not item_id:
        print("❌ ItemId 못 찾음 → 스킵")
        continue

    print(f"ItemId 추출 성공: {item_id}")


    # 2단계: 100자평
    short_reviews = crawl_short_reviews(item_id, isbn, max_pages=50)
    print(f"100자평 {len(short_reviews)}개")

    """# 3단계: 마이리뷰
    #my_reviews = crawl_my_reviews(isbn, max_pages=10)
    my_reviews = new_crawl_my_reviews(item_id, max_pages=10)
    print(f"마이리뷰 {len(my_reviews)}개")"""



    all_reviews.extend(short_reviews)
    #all_reviews.extend(my_reviews)

    # ISBN 하나 처리 후 쉬기
    time.sleep(1)


# ================================
# 7. CSV 저장
# ================================

reviews_df = pd.DataFrame(all_reviews)

reviews_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print("알라딘 리뷰 크롤링 완료!")
print(f"저장 파일: {OUTPUT_CSV}")
