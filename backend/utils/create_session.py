from fastapi import APIRouter, Depends, Cookie, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from pydantic import BaseModel
from .models import User, ChatSession
from .config import get_db

retirement_router = APIRouter()

class SessionCreateResponse(BaseModel):
    session_id: str
    user_id: str
    started_at: str

@retirement_router.post("/sessions", response_model=SessionCreateResponse)
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
