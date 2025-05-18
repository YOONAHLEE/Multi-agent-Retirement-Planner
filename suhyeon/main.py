from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config.database import init_db
from api.v1.endpoints.chat import router as chat_router

app = FastAPI(
    title="FastAPI LLM Agent",
    description="퇴직연금 agent 시스템을 위한 API 엔드포인트",
    version="1.0.0"
)

# 데이터베이스 초기화
init_db()

# 라우터 등록
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    """루트 경로 접속 시 docs로 리다이렉트"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 