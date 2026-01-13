from __future__ import annotations

import time
from typing import Any, Callable

from .trace import TraceEvent


def now_ms() -> int:
    return int(time.time() * 1000)


def truncate_text(text: str, max_chars: int | None) -> tuple[str, bool]:
    if max_chars is None or len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def with_trace(
    tool_name: str,
    request_id: str,
    tracer,
    args_summary: dict[str, Any],
    func: Callable[[], dict],
) -> dict:
    start_ms = now_ms()
    error_payload: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    try:
        result = func()
        error_payload = result.get("error") if isinstance(result, dict) else None
        return result
    finally:
        elapsed_ms = max(0, now_ms() - start_ms)
        result_summary: dict[str, Any] = {}
        if isinstance(result, dict):
            if "entries" in result:
                result_summary["entries"] = len(result.get("entries", []))
            if "matches" in result:
                result_summary["matches"] = len(result.get("matches", []))
            if "bytes" in result:
                result_summary["bytes"] = result.get("bytes")
        event = TraceEvent(
            tool_name=tool_name,
            request_id=request_id,
            args_summary=args_summary,
            elapsed_ms=elapsed_ms,
            result_summary=result_summary,
            error=error_payload,
        )
        tracer.record(event)
