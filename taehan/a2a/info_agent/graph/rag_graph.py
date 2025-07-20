from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from utils.tools import initialize_retriever_tool
from utils.grade_documents import grade_documents
from nodes.agent import agent
from nodes.generate import generate
from nodes.rewrite import rewrite
from langgraph.graph.state import CompiledStateGraph
from typing import Optional
from config.config import ResponseFormat

# 에이전트 상태를 정의하는 타입 딕셔너리, 메시지 시퀀스를 관리하고 추가 동작 정의
class AgentState(TypedDict):
    # add_messages reducer 함수를 사용하여 메시지 시퀀스를 관리
    messages: Annotated[Sequence[BaseMessage], add_messages]
    structured_response: Optional[ResponseFormat]

def create_rag_graph(memory=None) -> CompiledStateGraph:
    """
    RAG 그래프를 생성하는 함수입니다.
    
    Returns:
        AgentState: 생성된 RAG 그래프
    """
    # AgentState 기반 상태 그래프 워크플로우 초기화
    workflow = StateGraph(AgentState)

    # tool 초기화
    retriever_tool = initialize_retriever_tool()  # 검색 도구

    # 워크플로우 내 순환 노드 정의 및 추가
    workflow.add_node("agent", lambda state: agent(state, tools=[retriever_tool], memory=memory))  # 에이전트 노드
    retrieve = ToolNode([retriever_tool])
    workflow.add_node("retrieve", retrieve)  # 검색 노드
    workflow.add_node("rewrite", rewrite)  # 질문 재작성 노드
    workflow.add_node("generate", generate)  # 관련 문서 확인 후 응답 생성 노드

    # 시작점에서 에이전트 노드로 연결
    workflow.add_edge(START, "agent")

    # 검색 여부 결정을 위한 조건부 엣지 추가
    workflow.add_conditional_edges(
        "agent",
        # 에이전트 결정 평가
        tools_condition,
        {
            # 조건 출력을 그래프 노드에 매핑
            "tools": "retrieve",
            END: END,
        },
    )

    # 액션 노드 실행 후 처리될 엣지 정의
    workflow.add_conditional_edges(
        "retrieve",
        # 문서 품질 평가
        grade_documents,
    )
    workflow.add_edge("generate", END)
    workflow.add_edge("rewrite", "agent")

    # 워크플로우 그래프 컴파일
    graph = workflow.compile(checkpointer=memory)

    return graph
