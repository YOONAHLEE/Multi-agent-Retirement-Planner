from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph.rag_graph import create_rag_graph
from langchain_core.runnables import RunnableConfig
from utils.stream_graph import stream_graph, display_final_result

# Initialize FastAPI app
app = FastAPI(
    title="Info Agent API", description="Retirement Pension Information Agent", version="1.0.0"
)

rag_graph = create_rag_graph()

class UserInput(BaseModel):
    """User input model."""
    thread_id: str
    messages: str

@app.post("/info_agent")
async def info_agent(user_input: UserInput):
    """Info agent endpoint."""
    try:
        # Validate input
        if not user_input.messages or not isinstance(user_input.messages, str):
            raise HTTPException(status_code=400, detail="Invalid messages format.")
        
        # Extract thread_id and messages
        thread_id = user_input.thread_id
        messages = user_input.messages

        # config 설정(재귀 최대 횟수, thread_id)
        config = RunnableConfig(recursion_limit=5, configurable={"thread_id": thread_id})

        # 사용자의 에이전트 메모리 유형에 대한 질문을 포함하는 입력 데이터 구조 정의
        inputs = {
            "messages": [
                ("user", messages),
            ]
        }

        final_state = display_final_result(rag_graph, inputs, config)
        last_message = final_state['messages'][-1]
        if hasattr(last_message, 'content'):
            result = last_message.content
        else:
            result = str(last_message)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_info_agent(thread_id: str, messages: str) -> str:
    """
    RAG 기반 퇴직연금 정보 에이전트를 실행하여 사용자 질의에 대한 응답을 생성합니다.

    Args:
        thread_id (str): 대화 세션을 식별하기 위한 고유 ID
        messages (str): 사용자의 입력 메시지 (질문 또는 요청 내용)

    Returns:
        str: 에이전트가 생성한 응답 메시지 (최종 결과)
    
    Raises:
        ValueError: messages 입력이 유효하지 않을 경우 발생
        Exception: 에이전트 실행 중 발생하는 기타 예외를 그대로 전달
    """
    if not messages or not isinstance(messages, str):
        raise ValueError("Invalid messages format.")
    
    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=5, configurable={"thread_id": thread_id})

    # 사용자의 에이전트 메모리 유형에 대한 질문을 포함하는 입력 데이터 구조 정의
    inputs = {
        "messages": [
            ("user", messages),
        ]
    }

    final_state = display_final_result(rag_graph, inputs, config)
    last_message = final_state['messages'][-1]
    if hasattr(last_message, 'content'):
        return last_message.content
    else:
        return str(last_message)


if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    try:
        result = run_info_agent("abc123", "IRP의 연간 납입 한도는 얼마인가요?")
        print("결과:", result)
    except Exception as e:
        print("오류:", e)
