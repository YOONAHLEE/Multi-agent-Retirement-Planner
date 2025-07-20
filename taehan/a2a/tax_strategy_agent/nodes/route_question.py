from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import get_route_question_prompt
from config.config import MODEL_CONFIG
from embedding import initialize_vectorstores

# 벡터 스토어 초기화
qa_chains = initialize_vectorstores()

def route_question(state: Dict[str, Any]) -> Dict[str, Any]:
    """질문을 분석하고 적절한 정보 출처를 결정합니다."""
    print("---ROUTE QUESTION---")
    
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # 프롬프트 템플릿 가져오기
    prompt = get_route_question_prompt()
    
    # 체인 생성 및 실행
    chain = prompt | llm
    result = chain.invoke({"question": state["question"]})
    
    # 결과 처리
    source = result.content.lower()
    
    # retriever 선택
    if "1번" in source:
        retriever = qa_chains["1"]
    elif "2번" in source:
        retriever = qa_chains["2"]
    elif "3번" in source:
        retriever = qa_chains["3"]
    else:
        retriever = qa_chains["1"]  # fallback
    
    # 문서 검색
    docs = retriever.retriever.invoke(state["question"])
    
    return {
        "question": state["question"],
        "documents": docs,
        "grade_decision": source
    } 