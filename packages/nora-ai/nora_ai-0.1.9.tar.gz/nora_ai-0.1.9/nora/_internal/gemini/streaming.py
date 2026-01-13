"""Gemini API 스트리밍 응답 처리"""

from typing import Any
from ...client import NoraClient
from .types import RequestParams
from .metadata_builder import build_trace_data


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
    stream: Any,
    client: NoraClient,
    request_params: RequestParams,
    start_time: float,
    is_async: bool = False,
    parent_execution_id: str = None,
):
    """
    스트리밍 응답을 래핑하여 완료 시 trace를 기록합니다.

    Args:
        stream: 원본 스트리밍 응답
        client: Nora 클라이언트
        request_params: 요청 파라미터
        start_time: 요청 시작 시간
        is_async: 비동기 스트림 여부
        parent_execution_id: 부모 execution span ID (optional)

    Returns:
        래핑된 스트리밍 응답
    """
    # 스트리밍 데이터 수집용
    collected_data = {
        "text": "",
        "total_tokens": 0,
        "finish_reason": None,
    }

    def process_chunk(chunk):
        """청크를 처리하고 데이터를 수집합니다."""
        try:
            # 청크에서 텍스트 추출
            if hasattr(chunk, "text"):
                collected_data["text"] += chunk.text

            # 토큰 사용량 누적
            if hasattr(chunk, "usage_metadata"):
                metadata = chunk.usage_metadata
                if hasattr(metadata, "total_token_count"):
                    collected_data["total_tokens"] = metadata.total_token_count

            # finish_reason 추출
            if hasattr(chunk, "candidates") and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, "finish_reason"):
                    finish_reason = candidate.finish_reason
                    if hasattr(finish_reason, "name"):
                        collected_data["finish_reason"] = finish_reason.name

        except Exception:
            pass

        return chunk

    def finalize_trace():
        """스트리밍 완료 후 trace를 기록합니다."""
        import time

        end_time = time.time()

        # Mock response 객체 생성
        mock_response = type(
            "MockResponse",
            (),
            {
                "text": collected_data["text"],
                "usage_metadata": type(
                    "UsageMetadata", (), {"total_token_count": collected_data["total_tokens"]}
                )(),
                "candidates": [
                    type(
                        "Candidate",
                        (),
                        {
                            "finish_reason": type(
                                "FinishReason", (), {"name": collected_data["finish_reason"] or "STOP"}
                            )()
                        },
                    )()
                ],
            },
        )()

        trace_data = build_trace_data(
            request_params,
            mock_response,
            start_time,
            end_time,
            error=None,
        )
        
        # Add parent execution ID if exists
        if parent_execution_id:
            trace_data["execution_parent_id"] = parent_execution_id
        
        client.trace(**trace_data)

    # 동기 스트리밍 래퍼
    if not is_async:

        def sync_wrapper():
            try:
                for chunk in stream:
                    yield process_chunk(chunk)
            finally:
                finalize_trace()

        return StreamWrapper(sync_wrapper(), stream)

    # 비동기 스트리밍 래퍼
    else:

        async def async_wrapper():
            try:
                async for chunk in stream:
                    yield process_chunk(chunk)
            finally:
                finalize_trace()

        return StreamWrapper(async_wrapper(), stream)
