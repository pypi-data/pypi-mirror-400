from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TraceEvent:
    tool_name: str
    request_id: str
    args_summary: dict[str, Any]
    elapsed_ms: int
    result_summary: dict[str, Any]
    error: dict[str, Any] | None


class TraceWriter:
    def record(self, event: TraceEvent) -> None:
        raise NotImplementedError


class NullTraceWriter(TraceWriter):
    def record(self, event: TraceEvent) -> None:
        return


class InMemoryTraceWriter(TraceWriter):
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def record(self, event: TraceEvent) -> None:
        self.events.append(event)
