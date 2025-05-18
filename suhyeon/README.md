
# 퇴직연금 RAG 기반 챗봇

이 프로젝트는 퇴직연금 관련 정보를 제공하는 RAG(Retrieval-Augmented Generation) 기반의 챗봇 시스템입니다.

## 주요 기능

- 사용자별 대화 세션 관리
- RAG를 통한 정확한 퇴직연금 정보 제공
- 대화 기록 저장 및 조회
- 쿠키 기반의 사용자 식별

## 프로젝트 구조

```
agent/
├── main.py                 # FastAPI 서버 실행 파일
├── requirements.txt        # 의존성 패키지 목록
├── .env                    # 환경 변수 설정 파일
├── README.md              # 프로젝트 문서
├── api/
│   └── v1/
│       └── endpoints/
│           └── chat.py     # 채팅 API 엔드포인트
├── config/
│   ├── database.py        # 데이터베이스 설정
│   └── config.py          # 전역 설정 파일
├── models/
│   └── chat.py           # 데이터베이스 모델
├── nodes/                 # RAG 시스템 노드 구현
│   ├── __init__.py
│   ├── route_question.py  # 질문 라우팅 로직
│   ├── generate.py        # 응답 생성 로직
│   ├── grade_generation.py # 생성된 응답 평가
│   └── grade_documents.py # 검색된 문서 평가
├── state/                 # RAG 시스템 상태 관리
│   └── state.py          # 상태 정의 및 관리
├── utils/                 # 유틸리티 함수
│   ├── __init__.py
│   └── prompts.py        # 프롬프트 템플릿 관리
└── graph/
    └── rag_graph.py      # RAG 시스템 구현
```

### 파일 설명

- `main.py`: FastAPI 서버 실행 및 라우터 등록
- `requirements.txt`: 필요한 Python 패키지 목록
- `.env`: 데이터베이스 연결 정보와 API 키 설정
- `chat.py`: 채팅 API 엔드포인트 구현
- `database.py`: PostgreSQL 데이터베이스 연결 설정
- `config.py`: 전역 설정 (API 키, 모델 설정 등)
- `chat.py` (models): User, ChatSession, ChatMessage 모델 정의
- `rag_graph.py`: RAG 시스템 구현
- `nodes/`: RAG 시스템의 각 단계별 처리 로직
  - `route_question.py`: 질문 분석 및 처리 방향 결정
  - `generate.py`: 최종 응답 생성
  - `grade_generation.py`: 생성된 응답 품질 평가
  - `grade_documents.py`: 검색된 문서 관련성 평가
- `state/`: RAG 시스템의 상태 관리
  - `state.py`: 시스템 상태 정의 및 관리 (질문, 문서, 생성된 응답 등)
- `utils/`: 유틸리티 함수 모음
  - `prompts.py`: RAG 시스템에서 사용되는 프롬프트 템플릿 관리 (질문 라우팅, 문서 평가, 답변 생성, 환각 평가, 답변 평가)

### 주의사항

- `__pycache__/` 폴더는 Python 캐시 파일이므로 git에 포함하지 않습니다.
- `.env` 파일은 보안을 위해 git에 포함하지 않습니다.
- 로컬 데이터베이스 파일(`*.db`)은 git에 포함하지 않습니다.

## 기술 스택

- FastAPI: 백엔드 API 서버
- PostgreSQL: 대화 기록 및 사용자 정보 저장
- LangChain: RAG 시스템 구현
- ChromaDB: 벡터 저장소
- Sentence Transformers: 텍스트 임베딩

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd agent
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정합니다:
```
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
OPENAI_API_KEY=your-api-key
```

## 실행 방법

```bash
python main.py
```

서버가 실행되면 `http://localhost:8000`에서 API 문서를 확인할 수 있습니다.

## API 엔드포인트

### POST /api/v1/chat
채팅 메시지를 전송하고 AI 응답을 받습니다.

#### 새로운 대화 시작
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "퇴직연금에 대해 알려줘"
         }'
```

응답 예시:
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "퇴직연금은 근로자가 퇴직 후에도 안정적인 소득을 유지할 수 있도록 하는 제도입니다...",
    "user_id": "user_12345678"
}
```

#### 기존 세션에 메시지 추가
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
           "message": "IRP와 연금저축의 차이점은?",
           "session_id": "550e8400-e29b-41d4-a716-446655440000"
         }'
```

응답 예시:
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "IRP와 연금저축의 주요 차이점은 다음과 같습니다...",
    "user_id": "user_12345678"
}
```

### GET /api/v1/sessions
사용자의 모든 채팅 세션 목록을 조회합니다.

```bash
curl -X GET "http://localhost:8000/api/v1/sessions"
```

응답 예시:
```json
[
    {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "user_12345678",
        "started_at": "2024-03-20T10:30:00"
    },
    {
        "session_id": "660e8400-e29b-41d4-a716-446655440000",
        "user_id": "user_12345678",
        "started_at": "2024-03-20T11:45:00"
    }
]
```

## 주의사항

1. 모든 API 요청은 자동으로 쿠키를 통해 사용자를 식별합니다.
2. 새로운 사용자의 경우 자동으로 user_id가 생성되고 쿠키에 저장됩니다.
3. session_id를 지정하지 않으면 새로운 세션이 생성됩니다.
4. 기존 세션에 메시지를 추가할 때는 반드시 유효한 session_id를 지정해야 합니다.

