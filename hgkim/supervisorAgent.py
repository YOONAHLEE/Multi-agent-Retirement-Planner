from pydantic import BaseModel
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import operator
from State import AgentState
from langchain_core.messages import BaseMessage
from Schemas import RouteResponse, members, options_for_next
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver


def get_next(state):
    return state["next"]

def supervisor_agent(state):
    # 시스템 프롬프트 정의: 작업자 간의 대화를 관리하는 감독자 역할
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:  {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    # ChatPromptTemplate 생성
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? "
                "Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options_for_next), members=", ".join(members))


    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # 일단은 gpt-4o, 추후에 claude로 교체
    
    supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
    
    return supervisor_chain.invoke(state)
