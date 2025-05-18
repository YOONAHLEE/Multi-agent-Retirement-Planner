from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from config.config import PROMPT_CONFIG

def get_route_question_prompt() -> ChatPromptTemplate:
    """질문 라우팅을 위한 프롬프트 템플릿을 반환합니다."""
    return ChatPromptTemplate.from_template(PROMPT_CONFIG["route_question"])

def get_grade_documents_prompt() -> ChatPromptTemplate:
    """문서 평가를 위한 프롬프트 템플릿을 반환합니다."""
    return ChatPromptTemplate.from_template(PROMPT_CONFIG["grade_documents"])

def get_generate_prompt() -> ChatPromptTemplate:
    """답변 생성을 위한 프롬프트 템플릿을 반환합니다."""
    return ChatPromptTemplate.from_template(PROMPT_CONFIG["generate"])

def get_grade_hallucination_prompt() -> ChatPromptTemplate:
    """환각 평가를 위한 프롬프트 템플릿을 반환합니다."""
    return ChatPromptTemplate.from_template(PROMPT_CONFIG["grade_hallucination"])

def get_grade_answer_prompt() -> ChatPromptTemplate:
    """답변 평가를 위한 프롬프트 템플릿을 반환합니다."""
    return ChatPromptTemplate.from_template(PROMPT_CONFIG["grade_answer"]) 