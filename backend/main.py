from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.news_scrap import fetch_financial_news

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요시 프론트엔드 주소로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/news")
def get_news():
    """
    최신 금융 뉴스를 반환하는 엔드포인트
    """
    news = fetch_financial_news()
    return {"news": news} 