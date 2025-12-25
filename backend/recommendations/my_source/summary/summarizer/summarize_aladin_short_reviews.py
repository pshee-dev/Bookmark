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
INPUT_CSV = "aladin_short_reviews.csv"
OUT_CSV = "../outputs/summarized_aladin_reviews"

GMS_OPENAI_CHAT_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"


# =========================
# 유틸
# =========================
def make_bundle_text(reviews, max_reviews=30, max_chars=6000):
    buf, total = [], 0
    for r in reviews[:max_reviews]:
        r = str(r).strip()
        total += len(r)
        if total > max_chars:
            break
        buf.append(r)
    return "\n".join(buf)

# =========================
# 요약 함수
# =========================
def summarize_with_gpt4o_mini(bundle_text: str) -> dict:
    prompt = f"""
너는 책 리뷰 분석 전문가다.

아래는 동일한 책에 대한 여러 독자 리뷰이다.
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
# 단건 요약
# =========================
def summarize_aladin_short_reviews(reviews: list[str]) -> dict:
    if not reviews:
        return {"summary": "", "sentiment": "", "keywords": ""}
    bundle_text = make_bundle_text(reviews)
    return summarize_with_gpt4o_mini(bundle_text)

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
            bundle_text = make_bundle_text(reviews)
            res = summarize_with_gpt4o_mini(bundle_text)

            rows.append({
                "isbn13": isbn,
                "summary": res["summary"],
                "sentiment": res["sentiment"],
                "keywords": res["keywords"],
                "model": "gpt-4o-mini"
            })

        except Exception as e:
            print("요약 실패:", isbn, e)

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("✅ 요약 CSV 저장 완료:", OUT_CSV)
