from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import RunnableConfig
from typing import Any, Dict, List, Callable, Optional

def stream_graph(
    graph: CompiledStateGraph,
    inputs: dict,
    config: RunnableConfig,
    node_names: List[str] = [],
    callback: Callable = None,
):
    """
    LangGraph의 실행 결과를 스트리밍하여 출력하는 함수입니다.

    Args:
        graph (CompiledStateGraph): 실행할 컴파일된 LangGraph 객체
        inputs (dict): 그래프에 전달할 입력값 딕셔너리
        config (RunnableConfig): 실행 설정
        node_names (List[str], optional): 출력할 노드 이름 목록. 기본값은 빈 리스트
        callback (Callable, optional): 각 청크 처리를 위한 콜백 함수. 기본값은 None
            콜백 함수는 {"node": str, "content": str} 형태의 딕셔너리를 인자로 받습니다.
    Returns:
        None: 함수는 스트리밍 결과를 출력만 하고 반환값은 없습니다.
    """
    prev_node = ""
    for chunk_msg, metadata in graph.stream(inputs, config, stream_mode="messages"):
        curr_node = metadata["langgraph_node"]

        # node_names가 비어있거나 현재 노드가 node_names에 있는 경우에만 처리
        if not node_names or curr_node in node_names:
            # 콜백 함수가 있는 경우 실행
            if callback:
                callback({"node": curr_node, "content": chunk_msg.content})
            # 콜백이 없는 경우 기본 출력
            else:
                # 노드가 변경된 경우에만 구분선 출력
                if curr_node != prev_node:
                    print("\n" + "=" * 50)
                    print(f"🔄 Node: \033[1;36m{curr_node}\033[0m 🔄")
                    print("- " * 25)
                print(chunk_msg.content, end="", flush=True)

            prev_node = curr_node

def display_final_result(
    graph: CompiledStateGraph,
    inputs: dict,
    config: Optional[RunnableConfig] = None,
    callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    LangGraph 실행 후 최종 결과만 출력하는 함수입니다.

    Args:
        graph (CompiledStateGraph): 실행할 컴파일된 LangGraph 객체
        inputs (dict): 그래프에 전달할 입력값 딕셔너리
        config (RunnableConfig, optional): 실행 설정
        callback (Callable, optional): 최종 결과 처리를 위한 콜백 함수
            콜백 함수는 {"result": Any} 형태의 딕셔너리를 인자로 받음
    
    Returns:
        Dict[str, Any]: 그래프 실행의 최종 상태
    """
    # 기본 config 설정
    if config is None:
        config = {}
    
    # 그래프 실행
    final_state = graph.invoke(inputs, config)
    
    # # 최종 메시지 확인 및 출력
    # if 'messages' in final_state and final_state['messages']:
    #     last_message = final_state['messages'][-1]  # 마지막 메시지
        
    #     print("\n" + "=" * 50)
    #     print("🔄 Final Result 🔄")
    #     print("- " * 25)
        
    #     if hasattr(last_message, 'content'):
    #         print(last_message.content)
    #     else:
    #         print(str(last_message))
    # else:
    #     print("\n" + "=" * 50)
    #     print("🔄 Final Result 🔄")
    #     print("- " * 25)
    #     print(str(final_state))
    
    # 콜백 함수가 있는 경우 실행
    if callback:
        callback({"result": final_state})
    
    return final_state