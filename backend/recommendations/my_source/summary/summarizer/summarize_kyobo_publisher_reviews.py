import os
import requests
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# =========================
# 환경변수
# =========================
load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")
assert GMS_KEY, "GMS_KEY 없음 (.env 확인)"

# =========================
# 설정
# =========================
INPUT_CSV = "final_kyobo_publisher_reviews.csv"
#INPUT_CSV = "final_kyobo_reviews.csv"
OUT_CSV = "kyobo_publisher_reviews_embeddings_with_gpt4o_mini.csv"

GMS_OPENAI_CHAT_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"

# =========================
# 리뷰 분류 유틸
# =========================
def classify_review(text: str) -> str:
    text = str(text).strip()

    if len(text) <= 80:
        return "short_opinion"

    purchase_keywords = ["배송", "포장", "상태", "빠르", "하자", "굿즈", "책상태"]
    if any(k in text for k in purchase_keywords):
        return "purchase_review"

    return "content_review"


def make_kyobo_bundle_text(
        reviews,
        max_total_chars=6000,
        max_per_section=20
):
    sections = {
        "content_review": [],
        "short_opinion": [],
        "purchase_review": [],
    }

    for r in reviews:
        category = classify_review(r)
        sections[category].append(str(r).strip())

    def join_with_limit(texts):
        buf, total = [], 0
        for t in texts[:max_per_section]:
            total += len(t)
            if total > max_total_chars:
                break
            buf.append(f"- {t}")
        return "\n".join(buf)

    bundle = f"""
[콘텐츠 평가 리뷰]
{join_with_limit(sections["content_review"])}

[짧은 감상 / 한줄평]
{join_with_limit(sections["short_opinion"])}

[구매·배송 관련 언급]
{join_with_limit(sections["purchase_review"])}
""".strip()

    return bundle


# =========================
# 요약 함수
# =========================
def summarize_book_publisher_reviews_with_gpt4o_mini(raw_text: str) -> dict:
    """
    교보문고 책 소개 / 줄거리 / 추천사 / 서평 혼합 텍스트 요약
    → csv 생성
    """

    prompt = f"""
너는 도서 추천 시스템을 위한 책 소개 요약 전문가다.

아래 텍스트는 한 권의 책을 설명하기 위해 제공된 자료로,
줄거리, 출판사 서평, 추천사, 수상 이력, 평론가 코멘트 등이
뒤섞여 있을 수 있다.

요약 지침:
- 이 책이 어떤 책인지 핵심적으로 설명하라
- 소설의 경우 사건 전개나 결말은 언급하지 마라
- 책의 주제, 배경, 분위기, 문제의식, 독서 경험을 중심으로 정리하라
- 수상 이력, 인용문, 추천사 문장은 직접 인용하지 말고 의미만 반영하라
- 마케팅 문구나 과장된 표현은 중립적으로 정제하라
- 독자가 검색창에 입력할 법한 표현으로 작성하라

반드시 아래 형식을 정확히 지켜서 출력하라.

[출력 형식]
요약: 한글 4~5문장
감정: -1.0 ~ 1.0 사이 소수점 숫자 하나
키워드: 키워드1, 키워드2, 키워드3, 키워드4, 키워드5

[책 소개 원문]
{raw_text}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}"
    }

    r = requests.post(
        GMS_OPENAI_CHAT_URL,
        headers=headers,
        json=payload,
        timeout=120
    )
    r.raise_for_status()

    text = r.json()["choices"][0]["message"]["content"]

    return {
        "summary": text.split("요약:")[-1].split("감정:")[0].strip(),
        "sentiment": float(
            text.split("감정:")[-1].split("키워드:")[0].strip()
        ),
        "keywords": text.split("키워드:")[-1].strip(),
    }



# =========================
# 실행
# =========================
if __name__ == "__main__":
    df = pd.read_csv(INPUT_CSV)

    # isbn 기준 리뷰 묶기
    grouped = df.groupby("isbn13")["review_text"].apply(list).reset_index()

    rows = []

    for _, row in tqdm(grouped.iterrows(), total=len(grouped)):
        isbn = row["isbn13"]
        reviews = row["review_text"]

        try:
            bundle_text = make_kyobo_bundle_text(reviews)
            res = summarize_book_publisher_reviews_with_gpt4o_mini(bundle_text)

            rows.append({
                "isbn13": isbn,
                "summary": res["summary"],
                "sentiment": res["sentiment"],
                "keywords": res["keywords"],
                "model": "gpt-4o-mini",
                "source": "kyobo"
            })

        except Exception as e:
            print("요약 실패:", isbn, e)

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("✅ 교보문고 책 소개 요약 CSV 저장 완료:", OUT_CSV)
