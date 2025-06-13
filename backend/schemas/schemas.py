from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):
    """에이전트 상태 기본 스키마"""
    messages: List[Any]  # BaseMessage 객체들을 포함
    chat_history: List[Dict[str, str]]
    next: Optional[str] = None

class AgentResponse(BaseModel):
    """에이전트 응답 기본 스키마"""
    content: str
    metadata: Optional[Dict[str, Any]] = None

class SupervisorResponse(BaseModel):
    """슈퍼바이저 응답 스키마"""
    response: str
    agent_type: str
    chat_history: List[Dict[str, str]] 