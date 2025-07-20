from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config.config import MODEL_CONFIG
from pydantic import BaseModel, Field

# 데이터 모델 정의
class grade(BaseModel):
    """A binary score for relevance checks"""

    binary_score: str = Field(
        description="Response 'yes' if the document is relevant to the question or 'no' if it is not."
    )


def grade_documents(state) -> Literal["generate", "rewrite"]:
    # LLM 모델 초기화
    model = ChatOpenAI(temperature=0, model=MODEL_CONFIG["model"], streaming=True)

    # 구조화된 출력을 위한 LLM 설정
    llm_with_tool = model.with_structured_output(grade)

    # 프롬프트 템플릿 정의
    prompt = PromptTemplate(
        template="""You are a grader assessing relevance of a retrieved document 
        to a user question. \n 
        Here is the retrieved document: \n\n {context} \n\n
        Here is the user question: {question} \n
        If the document contains keyword(s) or semantic meaning related to the 
        user question, grade it as relevant. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document 
        is relevant to the question.""",
        input_variables=["context", "question"],
    )

    # llm + tool 바인딩 체인 생성
    # | 체이닝 연산자
    # 입력을 받아서 프롬프트를 생성(프롬프트 템플릿) -> llm에서 구조화된 결과로 출력(llm_with_tool)
    # 추후 invoke() 메서드로 호출 실행
    chain = prompt | llm_with_tool

    # 현재 상태에서 메시지 추출
    messages = state["messages"]

    # 가장 마지막 메시지 추출
    last_message = messages[-1]

    # 원래 질문 추출
    question = messages[0].content

    # 검색된 문서 추출
    retrieved_docs = last_message.content

    # 관련성 평가 실행
    scored_result = chain.invoke({"question": question, "context": retrieved_docs})

    # 관련성 여부 추출
    score = scored_result.binary_score

    # 관련성 여부에 따른 결정
    if score == "yes":
        # print("==== [DECISION: DOCS RELEVANT] ====")
        # print(retrieved_docs)
        return "generate"

    else:
        # print("==== [DECISION: DOCS NOT RELEVANT] ====")
        # print(score)
        return "rewrite"