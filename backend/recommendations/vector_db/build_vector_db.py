import os
import ast
import pandas as pd

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# =========================================================
# 0. 설정
# =========================================================

CSV_PATH = r"C:\Users\SSAFY\Desktop\asdf\AI_Recomendation_for_Bookmark\embeddings\review_embeddings\embedding_csv_result\kyobo\publisher_reviews\kyobo_publisher_reviews_embeddings_with_gpt4o_mini.csv"
VECTOR_DB_ROOT = "vectordb"

MODEL_CONFIG = {
    "gms-openai::text-embedding-3-small": {
        "persist_dir": os.path.join(VECTOR_DB_ROOT, "openai_small"),
        "collection": "reviews_openai_small",
        "dim": 1536,
    },
    "gms-openai::text-embedding-3-large": {
        "persist_dir": os.path.join(VECTOR_DB_ROOT, "openai_large_main"),
        "collection": "reviews_openai_large",
        "dim": 3072,
    },
    "gms-gemini::text-embedding-004": {
        "persist_dir": os.path.join(VECTOR_DB_ROOT, "gemini"),
        "collection": "reviews_gemini",
        "dim": None,
    },
}

# =========================================================
# 1. Precomputed Embedding Wrapper
# =========================================================

class PrecomputedEmbedding(Embeddings):
    def __init__(self, dim: int | None):
        self.dim = dim

    def embed_documents(self, texts):
        raise RuntimeError("Precomputed embeddings only")

    def embed_query(self, text):
        raise RuntimeError("Query embedding must be generated separately")

# =========================================================
# 2. CSV 로드
# =========================================================

def load_df():
    df = pd.read_csv(CSV_PATH)

    # embedding 문자열 → list[float]
    if "embedding" in df.columns:
        df["embedding"] = df["embedding"].dropna().apply(ast.literal_eval)
    else:
        raise RuntimeError("CSV에 embedding 컬럼이 없습니다")

    return df


# =========================================================
# 3. 모델별 Vector DB 생성
# =========================================================

def build_vectordb(df, model_name, cfg):
    os.makedirs(cfg["persist_dir"], exist_ok=True)

    sub_df = df[df["embedding_model"] == model_name]

    docs, embeddings, ids = [], [], []

    for _, row in sub_df.iterrows():
        emb = row.get("embedding")
        if not isinstance(emb, list):
            continue

        docs.append(
            Document(
                page_content=row["summary"],   # bundle_text 없으니 summary
                metadata={
                    "isbn13": row["isbn13"],
                    "model": model_name,
                },
            )
        )
        embeddings.append(emb)
        ids.append(str(row["isbn13"]))

    print(f"[INFO] {model_name}: {len(docs)} documents")

    if not docs:
        print(f"[SKIP] {model_name} (no rows)")
        return

    vectordb = Chroma(
        collection_name=cfg["collection"],
        persist_directory=cfg["persist_dir"],
        embedding_function=PrecomputedEmbedding(cfg["dim"]),
    )

    vectordb._collection.add(
        documents=[d.page_content for d in docs],
        metadatas=[d.metadata for d in docs],
        embeddings=embeddings,
        ids=ids,
    )

    vectordb.persist()
    print(f"[SAVED] {cfg['persist_dir']}")


# =========================================================
# 4. main
# =========================================================

def main():
    df = load_df()

    for model_name, cfg in MODEL_CONFIG.items():
        build_vectordb(df, model_name, cfg)

    print("\n✅ Vector DB build completed")

if __name__ == "__main__":
    main()
