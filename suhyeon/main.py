from typing import Dict, Any
from graph.rag_graph import create_rag_graph, GraphState

def main():
    """RAG 시스템을 실행합니다."""
    # RAG 그래프 생성
    rag_graph = create_rag_graph()
    
    # # 초기 상태 설정
    # initial_state: GraphState = {
    #     "question": "퇴직연금을 연금으로 수령할 때의 세금 혜택은 무엇인가요?",
    #     "documents": [],
    #     "generation": "",
    #     "grade_decision": ""
    # }
    
    # initial_state: GraphState = {
    #     "question": "방탄소년단 멤버 소개해줘",
    #     "documents": [],
    #     "generation": "",
    #     "grade_decision": "",
    #     "retry_count": 0
    # }
    
    initial_state: GraphState = {
        "question": "퇴직연금 수령 시 납세자에게 유리한 인출순서가 뭐야?",
        "documents": [],
        "generation": "",
        "grade_decision": "",
        "retry_count": 0
    }
    
    # 그래프 실행
    for step in rag_graph.stream(initial_state):
        for key, val in step.items():
            print(f"🧩 Step: {key}")
            if isinstance(val, dict):
                for k, v in val.items():
                    if isinstance(v, str) and len(v) < 1000:
                        print(f"{k}: {v}")
            print("---")
    
    # 최종 응답 출력
    print("\n최종 응답:", step[list(step.keys())[-1]]["generation"])

if __name__ == "__main__":
    main() 