from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from config.database import get_db
from models.chat import User, ChatSession, ChatMessage
import uuid
from pydantic import BaseModel
from datetime import datetime
from graph.rag_graph import create_rag_graph, GraphState

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    user_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    response: Response,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # 쿠키에 user_id가 없으면 새로 생성
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"  # 더 짧고 읽기 쉬운 ID 생성
        # 새로운 사용자 생성
        user = User(user_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 쿠키 설정
        response.set_cookie(
            key="user_id",
            value=user_id,
            max_age=365*24*60*60,  # 1년
            httponly=True,
            samesite="lax"
        )
    else:
        # 기존 사용자 확인
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            # 쿠키는 있지만 DB에 없는 경우 (데이터 정합성 문제)
            user = User(user_id=user_id)
            db.add(user)
            db.commit()
            db.refresh(user)
    
    # 세션 확인 또는 생성
    if not chat_request.session_id:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            user_id=user.user_id,
            session_id=session_id
        )
        db.add(session)
        db.commit()
    else:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == chat_request.session_id,
            ChatSession.user_id == user.user_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = chat_request.session_id
    
    # 이전 대화 기록 조회
    previous_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.desc()).limit(5).all()
    
    # 대화 컨텍스트 구성
    conversation_context = ""
    if previous_messages:
        conversation_context = "이전 대화 내용:\n"
        for msg in reversed(previous_messages):  # 시간순으로 정렬
            conversation_context += f"{msg.sender}: {msg.message}\n"
    
    # 사용자 메시지 저장
    user_message = ChatMessage(
        session_id=session_id,
        sender="user",
        message=chat_request.message
    )
    db.add(user_message)
    db.commit()
    
    # RAG 시스템을 통한 답변 생성
    try:
        # RAG 그래프 생성
        rag_graph = create_rag_graph()
        
        # 초기 상태 설정 (대화 컨텍스트 포함)
        initial_state: GraphState = {
            "question": f"{conversation_context}\n현재 질문: {chat_request.message}",
            "documents": [],
            "generation": "",
            "grade_decision": "",
            "retry_count": 0
        }
        
        # 그래프 실행
        final_state = None
        for step in rag_graph.stream(initial_state):
            final_state = step
        
        if not final_state:
            raise HTTPException(status_code=500, detail="응답 생성 중 오류가 발생했습니다.")
        
        # 최종 상태에서 생성된 응답 가져오기
        last_step = list(final_state.keys())[-1]
        ai_response = final_state[last_step]["generation"]
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="응답이 생성되지 않았습니다.")
        
        # AI 응답 저장
        ai_message = ChatMessage(
            session_id=session_id,
            sender="ai",
            message=ai_response
        )
        db.add(ai_message)
        db.commit()
        
        return ChatResponse(
            session_id=session_id,
            message=ai_response,
            user_id=user_id
        )
    
    except Exception as e:
        # 오류 발생 시에도 사용자 메시지는 저장되어 있음
        error_message = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
        ai_message = ChatMessage(
            session_id=session_id,
            sender="ai",
            message=error_message
        )
        db.add(ai_message)
        db.commit()
        
        return ChatResponse(
            session_id=session_id,
            message=error_message,
            user_id=user_id
        )

@router.get("/chat/history")
async def get_chat_history(
    user_id: Optional[str] = Cookie(None),
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # 사용자 확인
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 세션별 또는 전체 대화 기록 조회
    if session_id:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
    else:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).all()
        messages = []
        for session in sessions:
            session_messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.session_id
            ).order_by(ChatMessage.created_at).all()
            messages.extend(session_messages)
    
    return messages

@router.get("/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    return {"message": "Database connection successful!"}

@router.get("/sessions")
def get_user_sessions(request: Request, db: Session = Depends(get_db)):
    """사용자의 모든 세션 목록을 조회합니다."""
    print("Sessions endpoint called")  # 디버그 로그
    
    # 쿠키에서 user_id 가져오기
    user_id = request.cookies.get("user_id")
    print(f"Cookie user_id: {user_id}")  # 디버그 로그
    
    if not user_id:
        print("No user_id in cookie")  # 디버그 로그
        # 새로운 사용자 생성
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        user = User(user_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created new user: {user_id}")  # 디버그 로그

    # 사용자의 모든 세션 조회
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.started_at.desc()).all()
    
    print(f"Found {len(sessions)} sessions")  # 디버그 로그
    
    # 세션 정보를 딕셔너리 리스트로 변환
    session_list = []
    for session in sessions:
        session_list.append({
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat() if session.started_at else None
        })
    
    return session_list
