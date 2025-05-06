from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import get_grade_documents_prompt
from config.config import MODEL_CONFIG

def grade_documents(state: Dict[str, Any]) -> Dict[str, Any]:
    """검색된 문서의 관련성을 평가합니다.
    
    Args:
        state: 현재 상태를 담고 있는 딕셔너리
        
    Returns:
        업데이트된 상태 딕셔너리
    """
    print("---GRADE DOCUMENTS---")
    
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # 프롬프트 템플릿 가져오기
    prompt = get_grade_documents_prompt()
    
    # 체인 생성
    chain = prompt | llm
    
    # 문서 필터링
    filtered_docs = []
    for doc in state["documents"]:
        result = chain.invoke({
            "question": state["question"],
            "document": doc.page_content
        })
        
        if "yes" in result.content.lower():
            filtered_docs.append(doc)
    
    # 결과 결정
    grade_decision = "has_documents" if filtered_docs else "no_documents"
    
    return {
        "question": state["question"],
        "documents": filtered_docs,
        "grade_decision": grade_decision
    } 