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
INPUT_CSV = "final_kyobo_reviews.csv"
#INPUT_CSV = "final_kyobo_reviews.csv"
OUT_CSV = "kyobo_reviews_summaries_with_gpt4o_mini.csv"

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
def summarize_with_gpt4o_mini(bundle_text: str) -> dict:
    prompt = f"""
너는 책 리뷰 요약 전문가다.

아래는 교보문고에서 수집한 동일한 책에 대한 리뷰이다.
리뷰는 길이와 성격이 다양하며, 일부는 짧은 한줄평이거나
구매/배송 관련 언급일 수 있다.

요약 시 지침:
- 책의 내용, 주제, 문체, 전반적 독서 경험을 중심으로 요약하라
- 짧은 감상은 분위기를 보조하는 용도로 반영하라
- 구매/배송 언급은 핵심 평가가 아닐 경우 최소화하라

반드시 아래 형식을 정확히 지켜서 출력하라.

[출력 형식]
요약: 한글 4~5줄
감정: -1.0 ~ 1.0 사이 소수점 숫자 하나
키워드: 키워드1, 키워드2, 키워드3, 키워드4, 키워드5

[리뷰 목록]
{bundle_text}
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
        "sentiment": text.split("감정:")[-1].split("키워드:")[0].strip(),
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
            res = summarize_with_gpt4o_mini(bundle_text)

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

    print("✅ 교보문고 요약 CSV 저장 완료:", OUT_CSV)
