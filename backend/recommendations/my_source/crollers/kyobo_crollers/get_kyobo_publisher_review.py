# ================================
#  0. Library imports
# ================================

import re
import time

import requests


# ================================
#  1. Basic config (used in main only)
# ================================

INPUT_CSV = "../final_books_top204.csv"
OUTPUT_CSV = "final_kyobo_publisher_reviews.csv"


# ================================
#  2. ISBN -> Kyobo productId
# ================================


def get_kyobo_product_id(isbn: str) -> str | None:
    search_url = (
        "https://search.kyobobook.co.kr/search"
        f"?keyword={isbn}&target=total"
    )

    res = requests.get(
        search_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )

    if res.status_code != 200:
        return None

    match = re.search(r"/detail/(S\d{12})", res.text)
    if not match:
        return None

    return match.group(1)


# ================================
#  3. Kyobo publisher/contents crawl
# ================================


def crawl_kyobo_book_descriptions(product_id: str, isbn: str) -> list[dict]:
    results = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception:
        return results

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    driver.get(f"https://product.kyobobook.co.kr/detail/{product_id}")
    time.sleep(3)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
    time.sleep(2)

    target_sections = {
        "book_contents": "kyobo_book_contents",
        "book_publish_review": "kyobo_publisher_review",
        "book_recommend": "kyobo_recommendation",
    }

    for section_class, source_name in target_sections.items():
        try:
            elem = driver.find_element(
                By.CSS_SELECTOR,
                f"div.product_detail_area.{section_class} "
                "div.auto_overflow_inner > p.info_text",
            )
            text = elem.text.strip()
            if not text or len(text) < 50:
                continue

            results.append({
                "isbn13": isbn,
                "source": source_name,
                "review_text": text,
                "rating": None,
                "review_date": None,
                "blog_url": None,
            })
        except Exception:
            continue

    driver.quit()
    return results


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

        product_id = get_kyobo_product_id(isbn)
        if not product_id:
            print("productId not found -> skip")
            continue

        reviews = crawl_kyobo_book_descriptions(product_id, isbn)
        print(f"reviews: {len(reviews)}")

        all_reviews.extend(reviews)
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
