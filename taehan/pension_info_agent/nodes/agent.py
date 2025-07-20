from langchain_openai import ChatOpenAI
from config.config import MODEL_CONFIG
from typing import Dict, List, Any
from langchain_core.tools import BaseTool

def agent(state: Dict[str, Any], tools: List[BaseTool] = None) -> Dict[str, Any]:
    # 현재 상태에서 메시지 추출
    messages = state["messages"]

    # LLM 모델 초기화
    model = ChatOpenAI(temperature=0, streaming=True, model=MODEL_CONFIG["model"])

    # retriever tool 바인딩
    if tools:
        model = model.bind_tools(tools)

    # 에이전트 응답 생성
    response = model.invoke(messages)

    # 기존 리스트에 추가되므로 리스트 형태로 반환
    return {"messages": [response]}