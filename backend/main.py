from fastapi import FastAPI, Depends, Cookie, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.news_scrap import fetch_financial_news
from utils.create_session import SessionCreateResponse
from utils.models import User, ChatSession
from utils.config import get_db
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from utils.config import Base, engine
from utils.show_graph import get_kospi_sp500_graph
from fastapi.responses import JSONResponse
import yfinance as yf

# FastAPI 앱 생성 직후에 추가
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요시 프론트엔드 주소로 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/retirement/sessions", response_model=SessionCreateResponse)
async def create_session(
    response: Response,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 쿠키에 user_id가 없으면 새로 생성
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        user = User(user_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        response.set_cookie(
            key="user_id",
            value=user_id,
            max_age=365*24*60*60,
            httponly=True,
            samesite="lax"
        )
    else:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id)
            db.add(user)
            db.commit()
            db.refresh(user)

    # 새로운 세션 생성
    session_id = str(uuid.uuid4())
    session = ChatSession(
        user_id=user.user_id,
        session_id=session_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionCreateResponse(
        session_id=session.session_id,
        user_id=user.user_id,
        started_at=session.started_at.isoformat() if session.started_at else None
    )

@app.get("/news")
def get_news():
    """
    최신 금융 뉴스를 반환하는 엔드포인트
    """
    news = fetch_financial_news()
    return {"news": news} 

@app.get("/graph/kospi_sp500")
def get_kospi_sp500_graph_api():
    """
    코스피/S&P500 그래프 이미지를 base64로 반환하는 API
    """
    img_base64 = get_kospi_sp500_graph()
    return JSONResponse(content={"image_base64": img_base64})

@app.get("/market-index/{symbol}")
def get_market_data(symbol: str):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5d", interval="30m")
    info = ticker.info
    return {
        "price": info.get("regularMarketPrice"),
        "change": info.get("regularMarketChange"),
        "percent": info.get("regularMarketChangePercent"),
        "history": hist["Close"].dropna().tolist(),
        "timestamps": hist.index.strftime('%m-%d %H:%M').tolist(),
        "label": info.get("shortName", symbol)
    }