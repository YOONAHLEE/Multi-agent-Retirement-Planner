from typing import Dict, Any
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 모델 설정
MODEL_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0,
    "max_tokens": 1000,
    "openai_api_key": OPENAI_API_KEY
}

# 임베딩 설정
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "openai_api_key": OPENAI_API_KEY
}

# 벡터 스토어 설정
VECTORSTORE_CONFIG = {
    "path": "./data/",
    "bm25_k": 4,
    "semantic_k": 4,
    "bm25_weight": 0.5,
    "semantic_weight": 0.5
}