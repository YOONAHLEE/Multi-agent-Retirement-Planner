from typing import Dict, Any, Optional
from graph.rag_graph import create_rag_graph, GraphState
from config.config import PROMPT_CONFIG

class Agent:
    def __init__(self):
        """Agent 초기화"""
        self.rag_graph = create_rag_graph()
        self.conversation_history = []

    def _add_to_history(self, role: str, message: str):
        """대화 기록에 메시지 추가"""
        self.conversation_history.append({"role": role, "message": message})

    def _get_conversation_context(self) -> str:
        """대화 컨텍스트 생성"""
        if not self.conversation_history:
            return ""
        
        context = "이전 대화 내용:\n"
        for msg in self.conversation_history[-5:]:  # 최근 5개 메시지만 사용
            context += f"{msg['role']}: {msg['message']}\n"
        return context

    def chat(self, message: str) -> str:
        """
        사용자 메시지에 대한 응답을 생성합니다.
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            str: AI 응답
        """
        # 대화 기록에 사용자 메시지 추가
        self._add_to_history("user", message)
        
        # 대화 컨텍스트 생성
        conversation_context = self._get_conversation_context()
        
        # 초기 상태 설정
        initial_state: GraphState = {
            "question": f"{conversation_context}\n현재 질문: {message}",
            "documents": [],
            "generation": "",
            "grade_decision": "",
            "retry_count": 0
        }
        
        # RAG 그래프 실행
        final_state = None
        for step in self.rag_graph.stream(initial_state):
            final_state = step
        
        if not final_state:
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
        
        # 최종 상태에서 생성된 응답 가져오기
        last_step = list(final_state.keys())[-1]
        ai_response = final_state[last_step]["generation"]
        
        if not ai_response:
            return "죄송합니다. 응답을 생성하지 못했습니다."
        
        # 대화 기록에 AI 응답 추가
        self._add_to_history("ai", ai_response)
        
        return ai_response

# 사용 예시
if __name__ == "__main__":
    agent = Agent()
    
    # 테스트 메시지
    test_message = "퇴직연금 절세 방법에 대해 알려주세요."
    response = agent.chat(test_message)
    print(f"사용자: {test_message}")
    print(f"AI: {response}") 