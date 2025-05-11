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
        config = RunnableConfig(recursion_limit=10, configurable={"thread_id": thread_id})

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)