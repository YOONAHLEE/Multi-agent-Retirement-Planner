from collections.abc import AsyncIterable
from typing import Any

from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from financial_report_pipeline import adaptive_rag, SUMMARY_CACHE_PATH
from datetime import date


memory = MemorySaver()

class FinancialReportAgent:
    def __init__(self):
        # Create the RAG graph
        self.rag_graph = adaptive_rag

    async def stream(self, query, sessionId) -> AsyncIterable[dict[str, Any]]:
        """
        Stream the response processing steps.
        
        Args:
            query: The user's question or input
            sessionId: Unique identifier for the conversation session
            
        Returns:
            An async iterable of response dictionaries
        """
        # Initialize state with required keys
        inputs = {
            "date": date.today().isoformat(),
            "query": query,
            "documents": [],  # Initialize empty documents list
            "doc_summary_chunks": [],
            "doc_summary": "",
            "web_summary": "",
            "final_output": "",
            "db_path": SUMMARY_CACHE_PATH
        }
        
        try:
            # Stream the graph execution
            for item in self.rag_graph.stream(inputs):
                # print(item)
                final_output = None
                # item은 {node_name: node_output} 형태
                for node_name, node_output in item.items():
                    print(f"Node: {node_name}")
                    if node_name == "load_docs":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '관련 문서를 읽어오는 중...',
                        }
                    elif node_name == "docs_summarize":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '정보를 취합하는 중...',
                        }
                    elif node_name == "search_general_web":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '웹에 정보를 검색하는 중...',
                        }
                    elif node_name == "search_certain_web":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '특정 웹에 정보를 검색하는 중...',
                        }
                    elif node_name == "merge":
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '모은 정보를 합치는 중...',
                        }
                    elif node_name == "save":
                        final_output = node_output.get("final_output", "")
                        print(f"Final output: {final_output}")
                        yield {
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': '금융 보고서를 정리하는 중...',
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

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']