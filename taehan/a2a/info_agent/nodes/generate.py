from typing import Dict, Any
from langchain_openai import ChatOpenAI
from config.config import MODEL_CONFIG, ResponseFormat
from langchain import hub
from langchain_core.output_parsers import StrOutputParser

def generate(state):
    # 현재 상태에서 메시지 추출
    messages = state["messages"]

    # 원래 질문 추출
    question = messages[0].content

    # 가장 마지막 메시지 추출
    docs = messages[-1].content

    # RAG 프롬프트 템플릿 가져오기
    prompt = hub.pull("teddynote/rag-prompt")

    # LLM 모델 초기화
    llm = ChatOpenAI(model_name=MODEL_CONFIG["model"], temperature=0, streaming=True)

    # RAG 체인 구성
    rag_chain = prompt | llm | StrOutputParser()

    # 답변 생성 실행
    response = rag_chain.invoke({"context": docs, "question": question})

    # structured_response 추가
    structured_response = ResponseFormat(
        status='completed',
        message=response.content if hasattr(response, 'content') else str(response)
    )

    return {"messages": [response],
            "structured_response": structured_response}