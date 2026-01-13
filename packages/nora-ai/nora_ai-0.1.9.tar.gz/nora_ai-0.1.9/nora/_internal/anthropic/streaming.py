"""
Anthropic 스트리밍 응답 처리
"""

from typing import Any, Dict
from .utils import format_prompt
from .types import RequestParams


class StreamWrapper:
    """Generator를 context manager로 감싸는 wrapper 클래스"""
    
    def __init__(self, generator, original_response=None):
        self._generator = generator
        self._original_response = original_response
    
    def __iter__(self):
        return self._generator
    
    def __aiter__(self):
        return self._generator
    
    def __enter__(self):
        # 원본 response가 context manager를 지원하면 사용
        if self._original_response and hasattr(self._original_response, '__enter__'):
            self._original_response.__enter__()
        return self
    
    def __exit__(self, *args):
        # 원본 response가 context manager를 지원하면 사용
        if self._original_response and hasattr(self._original_response, '__exit__'):
            return self._original_response.__exit__(*args)
        return False
    
    async def __aenter__(self):
        # 원본 response가 async context manager를 지원하면 사용
        if self._original_response and hasattr(self._original_response, '__aenter__'):
            await self._original_response.__aenter__()
        return self
    
    async def __aexit__(self, *args):
        # 원본 response가 async context manager를 지원하면 사용
        if self._original_response and hasattr(self._original_response, '__aexit__'):
            return await self._original_response.__aexit__(*args)
        return False


def wrap_streaming_response(
    response: Any,
    client: Any,
    request_params: RequestParams,
    start_time: float,
    is_async: bool,
    parent_execution_id: str = None,
) -> Any:
    """
    스트리밍 응답을 래핑하여 완료 시 trace를 기록합니다.

    Args:
        response: Anthropic 스트리밍 응답
        client: Nora client 인스턴스
        request_params: 요청 파라미터
        start_time: 시작 시간
        is_async: 비동기 여부
        parent_execution_id: 부모 execution span ID (optional)

    Returns:
        래핑된 스트리밍 응답
    """
    # 스트리밍 데이터 수집용
    collected_data: Dict[str, Any] = {
        "text": "",
        "stop_reason": None,
        "usage": None,
    }

    def process_event(event: Any) -> Any:
        """이벤트를 처리하고 데이터를 수집합니다."""
        try:
            # 이벤트 타입에 따른 처리
            event_type = getattr(event, "type", None)

            if event_type == "content_block_delta":
                # 텍스트 델타
                delta = getattr(event, "delta", None)
                if delta:
                    delta_type = getattr(delta, "type", None)
                    if delta_type == "text_delta":
                        text = getattr(delta, "text", "")
                        if text:
                            collected_data["text"] += text

            elif event_type == "message_delta":
                # Stop reason 추출
                delta = getattr(event, "delta", None)
                if delta:
                    stop_reason = getattr(delta, "stop_reason", None)
                    if stop_reason:
                        collected_data["stop_reason"] = stop_reason

                # Usage 정보 추출
                usage = getattr(event, "usage", None)
                if usage:
                    collected_data["usage"] = {
                        "input_tokens": getattr(usage, "input_tokens", 0),
                        "output_tokens": getattr(usage, "output_tokens", 0),
                    }

        except Exception:
            pass

        return event

    def finalize_trace() -> None:
        """스트리밍 완료 후 trace를 기록합니다."""
        import time
        
        end_time = time.time()

        # Usage 정보 처리
        tokens_used = None
        if collected_data["usage"]:
            usage_data = collected_data["usage"]
            tokens_used = usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)

        trace_data = {
            "provider": "anthropic",
            "model": request_params.model,
            "prompt": format_prompt(request_params),
            "response": collected_data["text"],
            "start_time": start_time,
            "end_time": end_time,
            "stop_reason": collected_data["stop_reason"],
            "tokens_used": tokens_used,
            "metadata": {
                "temperature": request_params.temperature,
                "max_tokens": request_params.max_tokens,
                "top_p": request_params.top_p,
                "top_k": request_params.top_k,
                "system": request_params.system,
                "messages_count": len(request_params.messages),
                "is_streaming": True,
                "usage": collected_data["usage"],
            },
        }
        
        # Add parent execution ID if exists
        if parent_execution_id:
            trace_data["execution_parent_id"] = parent_execution_id

        client.trace(**trace_data)

    # 동기 스트리밍 래퍼
    if not is_async:

        def sync_wrapper():
            try:
                for event in response:
                    yield process_event(event)
            finally:
                finalize_trace()

        return StreamWrapper(sync_wrapper(), response)

    # 비동기 스트리밍 래퍼
    else:

        async def async_wrapper():
            try:
                async for event in response:
                    yield process_event(event)
            finally:
                finalize_trace()

        return StreamWrapper(async_wrapper(), response)
