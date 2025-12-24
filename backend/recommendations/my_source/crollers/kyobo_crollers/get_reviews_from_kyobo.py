# ================================
#  0. Library imports
# ================================

import re
import time

import requests


# ================================
#  1. Basic config (used in main only)
# ================================

INPUT_CSV = "final_books_top204.csv"
OUTPUT_CSV = "final_kyobo_reviews.csv"


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
#  3. Kyobo review crawl (Selenium)
# ================================


def crawl_kyobo_reviews_selenium(product_id: str, isbn: str) -> list[dict]:
    reviews = []

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception:
        return reviews

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

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    review_items = driver.find_elements(By.CSS_SELECTOR, "div.comment_item")

    for elem in review_items:
        try:
            text_elem = elem.find_element(By.CSS_SELECTOR, "div.comment_text")
            review_text = text_elem.text.strip()
        except Exception:
            continue

        if not review_text:
            continue

        rating = None
        rating_input = elem.find_elements(By.CSS_SELECTOR, "input.rating-input")
        if rating_input:
            try:
                rating = int(rating_input[0].get_attribute("value"))
            except Exception:
                rating = None

        review_date = None
        date_candidates = elem.find_elements(By.XPATH, ".//span[contains(text(), '.')]")
        for d in date_candidates:
            t = d.text.strip()
            if len(t) == 10 and t.count('.') == 2:
                review_date = t
                break

        reviews.append({
            "isbn13": isbn,
            "source": "kyobo_review",
            "review_text": review_text,
            "rating": rating,
            "review_date": review_date,
            "blog_url": None,
        })

    driver.quit()
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

        product_id = get_kyobo_product_id(isbn)
        if not product_id:
            print("productId not found -> skip")
            continue

        reviews = crawl_kyobo_reviews_selenium(product_id, isbn)
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
