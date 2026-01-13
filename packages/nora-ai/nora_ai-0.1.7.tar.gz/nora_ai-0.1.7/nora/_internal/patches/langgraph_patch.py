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
    
    # 노드 이름 -> 마지막 execution span ID 매핑 (conditional edge 부모 추적용)
    _node_execution_spans: Dict[str, str] = {}

    def traced_add_node(self, name: str, action: Callable, **kwargs):
        """노드 추가 시 자동으로 trace 데코레이터를 적용합니다."""
        import inspect
        client = _get_active_client()
        
        # 이미 traced된 함수인지 확인
        if client and callable(action) and not hasattr(action, '_nora_traced'):
            original_action = action
            
            # async 함수인지 확인
            if inspect.iscoroutinefunction(original_action):
                # async wrapper
                @wraps(original_action)
                async def async_wrapper(*args, **kwargs):
                    from ...client import _current_execution_span
                    
                    # 함수 실행 (이 시점에 execution span이 설정되어 있음)
                    result = await original_action(*args, **kwargs)
                    
                    # 실행 후 현재 execution span ID 저장 (conditional edge에서 사용)
                    current_span = _current_execution_span.get()
                    if current_span and current_span.get("id"):
                        _node_execution_spans[name] = current_span["id"]
                    
                    return result
                
                # trace 데코레이터 적용 (wrapper를 감쌈)
                traced_action = client.trace(async_wrapper, span_kind="langgraph_node", name=name)
                traced_action._nora_traced = True
                return original_add_node(self, name, traced_action, **kwargs)
            else:
                # sync wrapper
                @wraps(original_action)
                def sync_wrapper(*args, **kwargs):
                    from ...client import _current_execution_span
                    
                    # 함수 실행 (이 시점에 execution span이 설정되어 있음)
                    result = original_action(*args, **kwargs)
                    
                    # 실행 후 현재 execution span ID 저장 (conditional edge에서 사용)
                    current_span = _current_execution_span.get()
                    if current_span and current_span.get("id"):
                        _node_execution_spans[name] = current_span["id"]
                    
                    return result
                
                # trace 데코레이터 적용 (wrapper를 감쌈)
                traced_action = client.trace(sync_wrapper, span_kind="langgraph_node", name=name)
                traced_action._nora_traced = True
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
                    
                    # source 노드의 execution span ID를 부모로 사용
                    parent_execution_id = _node_execution_spans.get(source)
                    
                    # span_data 생성
                    import time
                    import uuid
                    span_data = {
                        "id": str(uuid.uuid4()),
                        "name": original_path.__name__,  # 함수 이름 사용
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
                    
                    # 부모 execution_id 추가
                    if parent_execution_id:
                        span_data["execution_parent_id"] = parent_execution_id
                    
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
