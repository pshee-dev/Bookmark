import os
import requests
from dotenv import load_dotenv

# =========================
# 환경변수
# =========================
load_dotenv()
GMS_KEY = os.getenv("GMS_KEY")
assert GMS_KEY, "GMS_KEY 없음 (.env 확인)"

# =========================
# 설정
# =========================
GMS_OPENAI_CHAT_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"


# =========================
# 유저 리뷰 묶기
# =========================
def make_user_bundle_text(reviews, max_reviews=30, max_chars=6000):
    buf, total = [], 0
    for r in reviews[:max_reviews]:
        r = str(r).strip()
        if not r:
            continue
        total += len(r)
        if total > max_chars:
            break
        buf.append(f"- {r}")
    return "\n".join(buf)


# =========================
# 요약 함수
# =========================
def summarize_user_reviews_with_gpt4o_mini(bundle_text: str) -> dict:
    prompt = f"""
당신은 독서 커뮤니티의 유저 리뷰 요약 전문가입니다.

아래는 동일한 책에 대해 여러 사용자가 남긴 리뷰입니다.
판매/배송/구매 경험보다는 실제 독서 경험과 취향, 감상 포인트를 중심으로 요약해주세요.

반드시 아래 형식으로 출력하세요.

[출력 형식]
요약: 4~5문장
감정: -1.0 ~ 1.0 사이의 숫자 하나
키워드: 키워드, 키워드, 키워드, 키워드, 키워드, 키워드

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
def summarize_user_reviews(reviews: list[str]) -> dict:
    if not reviews:
        return {"summary": "", "sentiment": "", "keywords": ""}
    bundle_text = make_user_bundle_text(reviews)
    return summarize_user_reviews_with_gpt4o_mini(bundle_text)
