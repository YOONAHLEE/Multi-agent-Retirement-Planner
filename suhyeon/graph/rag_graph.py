from typing import Dict, Any, Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain.schema import Document
from nodes.route_question import route_question
from nodes.grade_documents import grade_documents
from nodes.generate import generate
from nodes.grade_generation import grade_generation
from langchain_openai import ChatOpenAI
from config.config import MODEL_CONFIG

class GraphState(TypedDict):
    """그래프 상태를 정의하는 클래스"""
    question: str
    documents: List[Document]
    generation: str
    grade_decision: str
    retry_count: int  # 재시도 횟수를 추적하는 필드 추가

def transform_query(state: GraphState) -> GraphState:
    """질문을 변환합니다."""
    print("---TRANSFORM QUERY---")
    
    # 재시도 횟수 증가
    state["retry_count"] = state.get("retry_count", 0) + 1
    
    # 최대 재시도 횟수(3회)를 초과한 경우
    if state["retry_count"] > 3:
        state["generation"] = "죄송합니다. 여러 번 시도했지만 적절한 답변을 생성하지 못했습니다."
        state["grade_decision"] = "not supported"
        return state
    
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # 질문 수정 프롬프트
    transform_prompt = f"질문을 더 정확하게 고쳐줘: {state['question']}"
    
    # 질문 수정
    transformed_question = llm.invoke(transform_prompt).content.strip()
    print(f"수정된 질문: {transformed_question}")
    
    # 상태 업데이트
    state["question"] = transformed_question
    state["grade_decision"] = "retry"
    
    return state

def create_rag_graph() -> StateGraph:
    """RAG 워크플로우를 생성합니다."""
    # 그래프 초기화
    workflow = StateGraph(GraphState)
    
    # 노드 추가
    workflow.add_node("route_question", route_question)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("generate", generate)
    workflow.add_node("grade_generation", grade_generation)
    workflow.add_node("transform_query", transform_query)
    
    # 엣지 정의
    def decide_after_grade_documents(state: GraphState) -> str:
        """문서 평가 후 다음 단계 결정"""
        return "generate" if state["grade_decision"] == "has_documents" else "transform_query"
    
    def decide_after_grade_generation(state: GraphState) -> str:
        """생성 평가 후 다음 단계 결정"""
        return "useful" if state["grade_decision"] == "useful" else "transform_query"
    
    def decide_after_transform_query(state: GraphState) -> str:
        """질문 변환 후 다음 단계 결정"""
        if state["retry_count"] > 3:
            return "useful"
        return "route_question"
    
    # 엣지 추가
    workflow.add_edge(START, "route_question")
    workflow.add_edge("route_question", "grade_documents")
    
    workflow.add_conditional_edges(
        "grade_documents",
        decide_after_grade_documents,
        {
            "generate": "generate",
            "transform_query": "transform_query",
        }
    )
    
    workflow.add_conditional_edges(
        "transform_query",
        decide_after_transform_query,
        {
            "useful": END,
            "route_question": "route_question",
        }
    )
    
    workflow.add_edge("generate", "grade_generation")
    
    workflow.add_conditional_edges(
        "grade_generation",
        decide_after_grade_generation,
        {
            "useful": END,
            "transform_query": "transform_query",
        }
    )
    
    # 그래프 컴파일
    return workflow.compile() 

