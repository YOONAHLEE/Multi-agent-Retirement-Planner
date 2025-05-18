from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import get_generate_prompt
from config.config import MODEL_CONFIG

def generate(state: Dict[str, Any]) -> Dict[str, Any]:
    """주어진 정보를 바탕으로 답변을 생성합니다.
    
    Args:
        state: 현재 상태를 담고 있는 딕셔너리
        
    Returns:
        업데이트된 상태 딕셔너리
    """
    print("---GENERATE ANSWER---")
    
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # 프롬프트 템플릿 가져오기
    prompt = get_generate_prompt()
    
    # 컨텍스트 생성
    context = "\n".join([doc.page_content for doc in state["documents"]])
    
    # 체인 생성 및 실행
    chain = prompt | llm
    answer = chain.invoke({
        "question": state["question"],
        "context": context
    })
    
    return {
        "question": state["question"],
        "documents": state["documents"],
        "generation": answer.content.strip()
    } 