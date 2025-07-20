from collections.abc import AsyncIterable
from typing import Any, Dict, List

from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from graph.rag_graph import create_rag_graph, GraphState
from config.config import ResponseFormat


memory = MemorySaver()

class TaxStrategyAgent:
    def __init__(self):
        """Agent 초기화"""
        # Create the RAG graph with memory
        self.rag_graph = create_rag_graph()
        self.conversation_history = []

    def _add_to_history(self, role: str, message: str):
        """대화 기록에 메시지 추가"""
        self.conversation_history.append({"role": role, "message": message})
        
    def _get_conversation_context(self, config: RunnableConfig) -> str:
        """대화 컨텍스트 생성"""
        try:
            # 현재 상태에서 메시지 히스토리 가져오기
            current_state = self.rag_graph.get_state(config)
            if current_state and current_state.values.get('messages'):
                messages = current_state.values['messages']
                
                context = "이전 대화 내용:\n"
                # 최근 10개 메시지만 컨텍스트로 사용 (성능 최적화)
                recent_messages = messages[-10:] if len(messages) > 10 else messages
                
                for msg in recent_messages:
                    if isinstance(msg, tuple) and len(msg) >= 2:
                        role, content = msg[0], msg[1]
                        context += f"{role}: {content}\n"
                    elif hasattr(msg, 'type') and hasattr(msg, 'content'):
                        context += f"{msg.type}: {msg.content}\n"
                
                return context
        except Exception as e:
            print(f"컨텍스트 생성 중 오류: {e}")
            
        return ""

    def invoke(self, query: str, sessionId: str) -> Dict[str, Any]:
        """
        사용자 메시지에 대한 동기 응답을 생성합니다.
        
        Args:
            query (str): 사용자 질문
            sessionId (str): 세션 ID
            
        Returns:
            Dict[str, Any]: 응답 정보
        """
        # Configure the graph with the session ID
        recursion_limit = 3
        config = RunnableConfig(
            recursion_limit=recursion_limit, 
            configurable={"thread_id": sessionId}
        )
        
        # 대화 컨텍스트 생성
        # conversation_context = self._get_conversation_context(config)
        
        # 초기 상태 설정
        initial_state: GraphState = {
            #"question": f"{conversation_context}\n현재 질문: {query}",
            "question": f"현재 질문: {query}",
            "documents": [],
            "generation": "",
            "grade_decision": "",
            "retry_count": 0
        }
        
        try:
            # Invoke the graph
            self.rag_graph.invoke(initial_state, config)
            
            # Return the response
            return self.get_agent_response(config)
            
        except Exception as e:
            print(f"Agent invoke 중 오류: {e}")
            return {
                'is_task_complete': False,
                'require_user_input': True,
                'content': '죄송합니다. Agent invoke 중 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해주세요.',
            }

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[Dict[str, Any]]:
        """
        Stream the response processing steps.
        
        Args:
            query (str): 사용자 질문
            sessionId (str): 세션 ID
            
        Returns:
            AsyncIterable[Dict[str, Any]]: 스트리밍 응답
        """
        
        # 대화 컨텍스트 생성
        # conversation_context = self._get_conversation_context(config)
        
        # 컨텍스트가 있으면 질문에 포함
        # enhanced_query = query
        # if conversation_context:
        #     enhanced_query = f"{conversation_context}\n현재 질문: {query}"

        # 초기 상태 설정
        initial_state: GraphState = {
            "question": f"현재 질문: {query}",
            "documents": [],
            "generation": "",
            "grade_decision": "",
            "retry_count": 0
        }
        
        try:
            # Stream the graph execution
            for item in self.rag_graph.stream(initial_state):
                final_output = None
                # item은 {node_name: node_output} 형태
                for node_name, node_output in item.items():
                    print(f"Node: {node_name}")
                    if node_name == "route_question":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '세금 계산 도구를 호출하는 중...',
                        }
                    elif node_name == "grade_documents":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '퇴직연금 세금 정보를 검색하는 중...',
                        }
                    elif node_name == "transform_query":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '세금 계산 정보를 정리하는 중...',
                        }
                    elif node_name == "generate":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '세금 전략 답변을 생성하는 중...',
                        }
                    elif node_name == "grade_generation":
                        final_output = node_output['structured_response'].message
                        print(f"Final output: {final_output}")
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '세금 전략 답변을 평가하는 중...',
                        }

            # Yield the final response
            yield self.get_agent_response(final_output)
            
        except Exception as e:
            print(f"Agent stream 중 오류: {e}")
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': '죄송합니다. Agent stream 중 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해주세요.',
            }
        
    def get_agent_response(self, ai_response):

        if not ai_response:
            return "죄송합니다. 응답을 생성하지 못했습니다."
            
        print(f"Final message: {ai_response}")
        return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': ai_response,
            }

    # A2A 호환성을 위한 지원 컨텐츠 타입
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']