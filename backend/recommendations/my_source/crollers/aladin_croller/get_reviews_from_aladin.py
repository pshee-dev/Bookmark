# ================================
#  0. Library imports
# ================================

import time

import requests
from bs4 import BeautifulSoup


# ================================
#  1. Basic config (used in main only)
# ================================

INPUT_CSV = "final_books_top204.csv"
OUTPUT_CSV = "aladin_reviews.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


# ================================
#  2. ISBN -> Aladin itemId
# ================================

def get_aladin_item_id(isbn: str) -> str | None:
    search_url = (
        "https://www.aladin.co.kr/search/wsearchresult.aspx"
        f"?SearchTarget=Book&SearchWord={isbn}"
    )
    res = requests.get(search_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    book_boxes = soup.select("div.ss_book_box")
    if not book_boxes:
        print("ss_book_box not found -> search failed")
        return None

    link = book_boxes[0].select_one("a[href*='wproduct.aspx?ItemId=']")
    if not link:
        print("itemId link not found in search result")
        return None

    href = link.get("href")
    return href.split("ItemId=")[-1].split("&")[0]


# ================================
#  3. Short review crawl
# ================================

def crawl_short_reviews(item_id: str, isbn: str, max_pages: int = 1) -> list[dict]:
    reviews = []

    for page in range(1, max_pages + 1):
        url = (
            "https://www.aladin.co.kr/ucl/shop/product/ajax/GetCommunityListAjax.aspx"
            f"?ProductItemId={item_id}"
            f"&itemId={item_id}"
            "&pageCount=10"
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
            "X-Requested-With": "XMLHttpRequest",
        }
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        li_blocks = soup.select("li")
        if not li_blocks:
            print("short review ajax empty -> stop")
            break

        for i in range(0, len(li_blocks), 2):
            try:
                content_li = li_blocks[i]
                meta_li = li_blocks[i + 1]

                text_tag = content_li.select_one(
                    "span[id^='spnPaper']:not([id*='Spoiler'])"
                )
                review_text = text_tag.text.strip() if text_tag else None

                blog_tag = content_li.select_one("a[href*='blog.aladin.co.kr']")
                blog_url = blog_tag["href"] if blog_tag else None

                hundred_box = content_li.find_parent("div", class_="hundred_list")
                rating = None
                if hundred_box:
                    star_tag = hundred_box.select_one("div.HL_star")
                    if star_tag:
                        star_imgs = star_tag.find_all("img")
                        star_on_count = sum(
                            1 for img in star_imgs
                            if "icon_star_on" in img.get("src", "")
                        )
                        rating = star_on_count * 2

                date_tag = meta_li.select_one("div.left span")
                review_date = date_tag.text.strip() if date_tag else None

                if review_text:
                    reviews.append({
                        "isbn13": isbn,
                        "source": "aladin_short",
                        "review_text": review_text,
                        "rating": rating,
                        "review_date": review_date,
                        "blog_url": blog_url,
                    })
            except IndexError:
                continue

        time.sleep(1.5)

    return reviews


# ================================
#  4. Batch runner
# ================================

def main() -> None:
    import pandas as pd
    from tqdm import tqdm

    books_df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(books_df)} books")

    all_reviews = []
    for _, row in tqdm(books_df.iterrows(), total=len(books_df)):
        isbn = str(row["isbn13"]).strip()
        title = row["title"]

        print(f"\nCrawling: {title} ({isbn})")
        item_id = get_aladin_item_id(isbn)
        if not item_id:
            print("itemId not found -> skip")
            continue

        short_reviews = crawl_short_reviews(item_id, isbn, max_pages=50)
        print(f"short reviews: {len(short_reviews)}")
        all_reviews.extend(short_reviews)
        time.sleep(1)

    reviews_df = pd.DataFrame(all_reviews)
    reviews_df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Saved: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
