from collections.abc import AsyncIterable
from typing import Any

from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from graph.rag_graph import create_rag_graph
from config.config import ResponseFormat


memory = MemorySaver()

class RetirementPensionAgent:
    def __init__(self):
        # Create the RAG graph
        self.graph = create_rag_graph(memory=memory)

    def invoke(self, query, sessionId) -> str:
        """
        Synchronously process a user query.
        
        Args:
            query: The user's question or input
            sessionId: Unique identifier for the conversation session
            
        Returns:
            A dictionary with response information
        """
        # Configure the graph with the session ID
        recursion_limit = 10
        config = RunnableConfig(
            recursion_limit=recursion_limit, 
            configurable={"thread_id": sessionId}
        )
        
        # Format the input for the graph
        inputs = {
            "messages": [
                ("user", query),
            ]
        }
        
        # Invoke the graph
        self.graph.invoke(inputs, config)
        
        # Return the response
        return self.get_agent_response(config)

    async def stream(self, query, sessionId) -> AsyncIterable[dict[str, Any]]:
        """
        Stream the response processing steps.
        
        Args:
            query: The user's question or input
            sessionId: Unique identifier for the conversation session
            
        Returns:
            An async iterable of response dictionaries
        """
        # Format the input for the graph
        inputs = {
            "messages": [
                ("user", query),
            ]
        }
        
        # Configure the graph with the session ID
        recursion_limit = 10
        config = RunnableConfig(
            recursion_limit=recursion_limit, 
            configurable={"thread_id": sessionId}
        )
        
        for item in self.graph.stream(inputs, config, stream_mode='updates'):
            # item은 {node_name: node_output} 형태
            for node_name, node_output in item.items():
                if node_name == "agent":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': '도구 호출 중...',
                    }
                elif node_name == "retrieve":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': '검색 중...',
                    }
                elif node_name == "rewrite":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': '정보를 정리하는 중...',
                    }
                elif node_name == "generate":
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': '답변을 생성하는 중...',
                    }

        # Yield the final response
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        """
        Get the final response from the current state of the graph.
        
        Args:
            config: The configuration used for the graph
            
        Returns:
            A dictionary with the final response information
        """
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')

        print(f"Structured response status: {structured_response.status if structured_response else 'None'}")
        print(f"type of structured_response: {type(structured_response)}")

        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if structured_response.status == 'completed':
                print(f"Final message: {structured_response.message}")
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }
            if (
                structured_response.status == 'input_required'
            ):
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': '죄송합니다. 질문을 좀 더 명확히 입력해주세요.',
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': '죄송합니다. 답변을 생성하는 중 오류가 발생하였습니다. 다시 시도해주세요.',
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']