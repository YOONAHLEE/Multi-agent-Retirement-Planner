from typing import Dict, Any
from langchain_openai import ChatOpenAI
from utils.prompts import get_grade_hallucination_prompt, get_grade_answer_prompt
from config.config import MODEL_CONFIG, ResponseFormat

def grade_generation(state: Dict[str, Any]) -> Dict[str, Any]:
    """생성된 답변의 품질을 평가합니다.
    
    Args:
        state: 현재 상태를 담고 있는 딕셔너리
        
    Returns:
        업데이트된 상태 딕셔너리
    """
    print("---GRADE GENERATION---")
    
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # 프롬프트 템플릿 가져오기
    hallucination_prompt = get_grade_hallucination_prompt()
    answer_prompt = get_grade_answer_prompt()
    
    # 환각 평가
    hallucination_chain = hallucination_prompt | llm
    hallucination_result = hallucination_chain.invoke({
        "documents": state["documents"],
        "generation": state["generation"]
    })
    
    if "yes" in hallucination_result.content.lower():
        # 관련성 평가
        answer_chain = answer_prompt | llm
        answer_result = answer_chain.invoke({
            "question": state["question"],
            "generation": state["generation"]
        })
        
        if "yes" in answer_result.content.lower():
            print(" USEFUL")
            state["grade_decision"] = "useful"

            # structured_response 추가
            structured_response = ResponseFormat(
                status='completed',
                message=state["generation"]
            )
            state["structured_response"] = structured_response
        else:
            print(" NOT USEFUL")
            state["grade_decision"] = "not useful"
    else:
        print(" HALLUCINATION")
        state["grade_decision"] = "not supported"
    
    return state 