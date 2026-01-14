from dataclasses import dataclass
from typing import Any, Literal

SCHEMA_VERSION = "0.1"


@dataclass(slots=True)
class TraceEvent:
    event_id: str
    timestamp: int
    type: Literal["span_start", "span_end", "stream_event"]
    trace_id: str
    span_id: str
    parent_span_id: str | None
    payload: dict[str, Any]
