from typing import Dict, Any
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 모델 설정
MODEL_CONFIG = {
    "model": "gpt-4",
    "temperature": 0,
    "max_tokens": 1000,
    "openai_api_key": OPENAI_API_KEY
}

# 임베딩 설정
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "openai_api_key": OPENAI_API_KEY
}

# RAG 설정
RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 100,
    "top_k": 3
}

# 프롬프트 설정
PROMPT_CONFIG = {
    "system_message": """너는 세금을 절세하는 방법에 대해 전문적으로 아는 세금 절세 금융 전문가야. 
    너가 대답할 수 있는 질문 유형은 크게 3가지야. 
    1. 절세 관련 계좌 정보 제공(ISA, IRP, 연금저축), 
    2. 퇴직연금 관렬 절세 방법(납부, 운용, 수령), 
    3. 기타 세금 절세 방법 관련(연말정산)""",
    
    "route_question": """당신은 질문을 읽고, 어떤 정보 출처에서 답을 찾아야 할지 판단하는 역할입니다.

- IRP, ISA, 연금저축 등 절세계좌 관련 질문이면 "1번"
- 퇴직연금, 연금 수령 방식, 과세 관련이면 "2번"
- 연말 정산과 같은 기타 일반적인 절세 관련이면 "3번"

질문: {question}""",
    
    "grade_documents": """문서: {document}
질문: {question}
관련 있으면 yes, 없으면 no""",
    
    "generate": """<context>
{context}
</context>

질문: {question}
답변:""",
    
    "grade_hallucination": """문서: {documents}
답변: {generation}
사실이면 yes, 아니면 no""",
    
    "grade_answer": """질문: {question}
답변: {generation}
적절하면 yes, 아니면 no""",
    
    "question_rewriter": """질문을 더 정확하게 고쳐줘: {question}"""
}

# 벡터 스토어 설정
VECTORSTORE_CONFIG = {
    "1": {
        "pkl_files": [
            '/home/suhyeon/teddynote-parser-api-client/result/7edb5124-da10-45c0-8bcc-03aba84650a9/7edb5124-da10-45c0-8bcc-03aba84650a9_1-1.pkl',
            '/home/suhyeon/teddynote-parser-api-client/result/226c1d26-cb3a-42c1-9353-89549390d8d7/226c1d26-cb3a-42c1-9353-89549390d8d7_1-2.pkl'
        ]
    },
    "2": {
        "pkl_files": [
            '/home/suhyeon/teddynote-parser-api-client/result/cf59af43-64e5-4bdb-bcbd-72314ad7772f/cf59af43-64e5-4bdb-bcbd-72314ad7772f_2-1.pkl',
            '/home/suhyeon/teddynote-parser-api-client/result/a24915ff-6d9e-46ad-8d04-4c7e4511e225/a24915ff-6d9e-46ad-8d04-4c7e4511e225_2-2.pkl'
        ]
    },
    "3": {
        "pkl_files": [
            '/home/suhyeon/teddynote-parser-api-client/result/2603d37c-78bf-4316-b5f1-39c223b6f3ee/2603d37c-78bf-4316-b5f1-39c223b6f3ee_3-1.pkl',
            '/home/suhyeon/teddynote-parser-api-client/result/eba4cfb2-6131-426c-ad48-4b1d5305e7ba/eba4cfb2-6131-426c-ad48-4b1d5305e7ba_3-2.pkl'
        ]
    }
} 