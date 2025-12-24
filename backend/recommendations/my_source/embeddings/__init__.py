import os
from typing import Any, Optional

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


MODEL_NAME = "text-embedding-3-large"
OPENAI_EMBED_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"


def make_embeddings(data: Any) -> Optional[list[float]]:
    if isinstance(data, dict):
        text = str(data.get("summary", ""))
    elif isinstance(data, list):
        text = " ".join([str(x) for x in data])
    else:
        text = str(data or "")

    text = text.strip()[:1500]
    if not text:
        return None

    api_key = os.getenv("GMS_KEY")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "input": [text],
    }
    try:
        r = requests.post(OPENAI_EMBED_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["data"][0]["embedding"]
    except Exception:
        return None
