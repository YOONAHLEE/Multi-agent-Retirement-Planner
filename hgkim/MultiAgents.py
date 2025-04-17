from State import AgentState
from Schemas import members
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from SupervisorAgent import supervisor_agent, get_next


class MultiAgentRetirementPlanner:
    def __init__(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("Supervisor", supervisor_agent)
        # 멤버 노드 > Supervisor 노드로 엣지 추가
        for member in members:
            workflow.add_edge(member, "Supervisor")

        # 조건부 엣지 추가 (
        conditional_map = {k: k for k in members}
        conditional_map["FINISH"] = END

        # Supervisor 노드에서 조건부 엣지 추가
        workflow.add_conditional_edges("Supervisor", get_next, conditional_map)

        # 시작점
        workflow.add_edge(START, "Supervisor")

        # 그래프 컴파일
        graph = workflow.compile(checkpointer=MemorySaver())

        return graph