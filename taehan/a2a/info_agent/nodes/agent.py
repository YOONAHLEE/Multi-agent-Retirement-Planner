from langchain_openai import ChatOpenAI
from config.config import MODEL_CONFIG
from typing import Dict, List, Any
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import ResponseFormat

def agent(state: Dict[str, Any], tools: List[BaseTool] = None, memory = None) -> Dict[str, Any]:
    # 현재 상태에서 메시지 추출
    messages = state["messages"]

    # LLM 모델 초기화
    model = ChatOpenAI(temperature=0, streaming=True, model=MODEL_CONFIG["model"])
    # model = ChatGoogleGenerativeAI(model='gemini-2.0-flash', checkpoint=memory)

    # retriever tool 바인딩
    if tools:
        model = model.bind_tools(tools)

    # 에이전트 응답 생성
    response = model.invoke(messages)

    # structured_response 추가
    structured_response = ResponseFormat(
        status='completed',
        message=response.content if hasattr(response, 'content') else str(response)
    )

    # 기존 리스트에 추가되므로 리스트 형태로 반환
    return {"messages": [response],
            "structured_response": structured_response}