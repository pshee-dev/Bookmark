
#%% =========================
# 1) 환경 / 라이브러리
# =========================
import os
import re
import json
import math
import time
import hashlib
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


#%% =========================
# 2) 설정
# =========================
INPUT_CSV = r"C:\Users\SSAFY\Desktop\asdf\AI_Recomendation_for_Bookmark\embeddings\kyobo_publisher_reviews_summaries_with_gpt4o_mini.csv"
OUT_DIR = ""
os.makedirs(OUT_DIR, exist_ok=True)

# OpenAI (GMS OpenAI Gateway)
GMS_KEY = os.getenv("GMS_KEY")
assert GMS_KEY, "GMS_KEY 없음"

FINAL_MODEL = "text-embedding-3-large"
PROVIDER_MODEL_KEY = "gms-openai::text-embedding-3-large"

# ✅ GMS OpenAI Gateway URL
OPENAI_EMBED_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"

CACHE_PATH = os.path.join(OUT_DIR, "embed_cache.jsonl")

MAX_TEXT_CHARS = 1500      # 더 안전
MAX_EMBED_BATCH = 16      # ⬅️ GMS 안전값 (중요)

#%% =========================
# 3) 유틸
# =========================
def clean_text(text: str) -> str:
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return ""
    text = str(text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\sㄱ-ㅎ가-힣.,!?]", "", text)
    return text.strip()

def stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def make_bundle_text(
        reviews: List[str],
        max_reviews: int = 30,
        max_chars: int = 6000,
) -> str:
    buf, total = [], 0
    for r in reviews[:max_reviews]:
        r = str(r).strip()
        total += len(r)
        if total > max_chars:
            break
        buf.append(r)
    return "\n".join(buf)


#%% =========================
# 4) 데이터 로드 & 전처리 (REFAC)
# =========================
df = pd.read_csv(INPUT_CSV)

# 필수 컬럼 체크
required_cols = ["isbn13", "summary"]
for col in required_cols:
    assert col in df.columns, f"{col} 컬럼 없음"

# summary 정제
df["summary"] = df["summary"].apply(clean_text)
df = df[df["summary"].str.len() > 30]

texts = df["summary"].tolist()
isbns = df["isbn13"].tolist()

print("books:", len(df))


#%% =========================
# 5) 캐시
# =========================
def load_cache(path: str) -> Dict[Tuple[str, str], List[float]]:
    cache = {}
    if not os.path.exists(path):
        return cache
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            cache[(obj["provider_model"], obj["text_hash"])] = obj["vec"]
    return cache

def append_cache(
        path: str,
        provider_model: str,
        text: str,
        vec: List[float],
) -> None:
    rec = {
        "provider_model": provider_model,
        "text_hash": stable_hash(text),
        "vec": vec,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

cache = load_cache(CACHE_PATH)
print("cache size:", len(cache))


#%% =========================
# 6) GMS OpenAI 임베딩 클라이언트
# =========================
class OpenAIEmbedder:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def embed(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # ✅ GMS KEY
            "Content-Type": "application/json",
        }
        payload = {
            "model": FINAL_MODEL,
            "input": texts,
        }
        r = requests.post(
            OPENAI_EMBED_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return [item["embedding"] for item in data["data"]]


embedder = OpenAIEmbedder(GMS_KEY)



#%% =========================
# 7) 임베딩 실행 (번들 텍스트 안전 처리 + 캐시)
# =========================

def split_text_by_chars(text: str, max_chars: int = 2000) -> List[str]:
    """
    GMS payload 제한을 피하기 위한 안전 분할
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars
    return chunks



def embed_final(texts: List[str]) -> np.ndarray:
    out = [None] * len(texts)
    miss_idx, miss_texts = [], []

    # 1) 캐시 조회
    for i, t in enumerate(texts):
        key = (PROVIDER_MODEL_KEY, stable_hash(t))
        if key in cache:
            out[i] = cache[key]
        else:
            miss_idx.append(i)
            miss_texts.append(t)

    # 2) 임베딩
    for idx, text in tqdm(
            list(zip(miss_idx, miss_texts)),
            desc="embedding",
            total=len(miss_texts),
    ):
        pieces = split_text_by_chars(text)

        vecs = []
        for s in range(0, len(pieces), MAX_EMBED_BATCH):
            batch = pieces[s:s + MAX_EMBED_BATCH]
            vecs.extend(embedder.embed(batch))
            time.sleep(0.2)

        mean_vec = np.mean(vecs, axis=0).tolist()
        out[idx] = mean_vec

        cache_key = (PROVIDER_MODEL_KEY, stable_hash(text))
        cache[cache_key] = mean_vec
        append_cache(
            CACHE_PATH,
            PROVIDER_MODEL_KEY,
            text,
            mean_vec,
        )

    return np.array(out, dtype=np.float32)


#%% =========================
# 8) 실행
# =========================
embeddings=None
def run_embed(texts: List[str], output_path: str) -> np.ndarray:
    embeddings = embed_final(texts, output_path)
    OUT_DIR = output_path
print("embedding shape:", embeddings.shape)


#%% =========================
# 9) 최종 산출물 저장
# =========================

out = df.copy()
out["embedding"] = [
    json.dumps(vec.tolist(), ensure_ascii=False)
    for vec in embeddings
]
out["embedding_model"] = PROVIDER_MODEL_KEY
out["embedding_dim"] = embeddings.shape[1]

out_path = os.path.join(
    OUT_DIR, 'kyobo_publisher_reviews_embeddings_with_gpt4o_mini.csv'
)
out.to_csv(out_path, index=False, encoding="utf-8-sig")

print("saved:", out_path)
