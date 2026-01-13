"""
LangGraph 자동 패치
LangGraph의 노드 실행과 conditional edges를 자동으로 trace합니다.
"""

from typing import Any, Callable, Optional, Union, Dict, Sequence
from functools import wraps
import sys


def patch_langgraph():
    """LangGraph를 패치하여 자동으로 노드 실행과 routing을 trace합니다."""
    try:
        import langgraph
        from langgraph.graph import StateGraph
    except ImportError:
        # LangGraph가 설치되지 않은 경우 패치하지 않음
        return

    from ...client import _get_active_client

    # 이미 패치되었는지 확인
    if hasattr(StateGraph.add_node, '_nora_patched'):
        return

    # 원본 메서드 저장
    original_add_node = StateGraph.add_node
    original_add_conditional_edges = StateGraph.add_conditional_edges

    def traced_add_node(self, name: str, action: Callable, **kwargs):
        """노드 추가 시 자동으로 trace 데코레이터를 적용합니다."""
        client = _get_active_client()
        
        # 이미 traced된 함수인지 확인
        if client and callable(action) and not hasattr(action, '_nora_traced'):
            # 노드 함수를 trace로 감싸기
            traced_action = client.trace(action, span_kind="langgraph_node")
            traced_action._nora_traced = True  # 마커 추가
            return original_add_node(self, name, traced_action, **kwargs)
        else:
            return original_add_node(self, name, action, **kwargs)

    def traced_add_conditional_edges(
        self,
        source: str,
        path: Union[Callable, Dict[str, str]],
        path_map: Optional[Dict[str, str]] = None,
        then: Optional[str] = None,
    ):
        """Conditional edges 추가 시 routing 함수를 trace하고 decision을 기록합니다."""
        client = _get_active_client()
        
        if client and callable(path):
            # routing 함수를 trace로 감싸되 decision 정보 추가
            original_path = path
            
            @wraps(original_path)
            def traced_routing(state):
                from ...client import _current_trace_group
                
                # routing 함수 실행
                selected = original_path(state)
                
                # trace_group이 활성화된 경우에만 decision 기록
                current_group = _current_trace_group.get()
                if current_group and current_group.trace_id:
                    # path_map에서 가능한 옵션들 추출
                    if path_map:
                        options = [{"content": key, "score": None} for key in path_map.keys()]
                    else:
                        # path_map이 없으면 선택된 값으로부터 추정
                        options = [{"content": str(selected), "score": None}]
                    
                    # span_data 생성
                    import time
                    import uuid
                    span_data = {
                        "id": str(uuid.uuid4()),
                        "name": f"route_{source}",
                        "start_time": time.time(),
                        "end_time": time.time(),
                        "span_kind": "select",
                        "status": "completed",
                        "input": state if isinstance(state, dict) else {"state": str(state)},
                        "result": {
                            "options": options,
                            "selected_option": {"content": str(selected), "score": None}
                        },
                        "metadata": {
                            "function": original_path.__name__,
                            "source_node": source,
                        },
                    }
                    
                    # execution span 전송
                    client._send_execution_span(current_group.trace_id, span_data)
                
                return selected
            
            # 키워드 인자로 전달
            kwargs = {}
            if path_map is not None:
                kwargs['path_map'] = path_map
            if then is not None:
                kwargs['then'] = then
            
            return original_add_conditional_edges(self, source, traced_routing, **kwargs)
        else:
            # 키워드 인자로 전달
            kwargs = {}
            if path_map is not None:
                kwargs['path_map'] = path_map
            if then is not None:
                kwargs['then'] = then
            
            return original_add_conditional_edges(self, source, path, **kwargs)

    # 메서드 패치
    StateGraph.add_node = traced_add_node
    StateGraph.add_conditional_edges = traced_add_conditional_edges
    
    # 패치 완료 마커
    StateGraph.add_node._nora_patched = True
    StateGraph.add_conditional_edges._nora_patched = True

    print("[Nora] ✓ LangGraph patched successfully (nodes + conditional edges)")
