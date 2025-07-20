from graph.rag_graph import create_rag_graph
from langchain_core.runnables import RunnableConfig
from utils.stream_graph import stream_graph, display_final_result

def main():
    """RAG 시스템을 실행합니다."""
    # RAG 그래프 생성
    rag_graph = create_rag_graph()
    
    # config 설정(재귀 최대 횟수, thread_id)
    config = RunnableConfig(recursion_limit=10, configurable={"thread_id": "0"})

    # 사용자의 에이전트 메모리 유형에 대한 질문을 포함하는 입력 데이터 구조 정의
    # inputs = {
    #     "messages": [
    #         ("user", "노후 대비를 위한 회사 제공 자산관리 옵션은 뭐가 있어?"),
    #     ]
    # }
    
    # inputs = {
    #     "messages": [
    #         ("user", "방탄소년단 멤버 소개해줘"),
    #     ]
    # }

    inputs = {
        "messages": [
            ("user", "퇴직연금 확정급여형(DB형)과 확정기여형(DC형)의 차이점을 검색해서 알려줘"),
        ]
    }

    # 그래프 실행
    stream_graph(rag_graph, inputs, config, ["agent", "rewrite", "generate"])
    # display_final_result(rag_graph, inputs, config)

if __name__ == "__main__":
    main()