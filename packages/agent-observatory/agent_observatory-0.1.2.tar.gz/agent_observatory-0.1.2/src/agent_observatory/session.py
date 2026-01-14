from contextvars import Token
from typing import Any

from .buffering.ring_buffer import RingBuffer
from .context import get_current_span, reset_current_session
from .events import SCHEMA_VERSION, TraceEvent
from .exporters.worker import ExporterWorkerProtocol
from .internal.logging import log_internal_error
from .runtime.clock import (
    format_ns,
    mono_time_ns,
    wall_time_iso,
    wall_time_ns,
)
from .runtime.errors import serialize_error
from .runtime.ids import new_event_id, new_span_id, new_trace_id
from .spans import SpanContext, StreamSpan

DEFAULT_EVENT_BUFFER_SIZE = 10_000


class SessionState:
    """
    Internal state holding session metadata and buffered events.
    """

    def __init__(
        self,
        session_id: str,
        agent_id: str,
        user_id: str | None,
        metadata: dict[str, Any],
    ) -> None:
        self.session_id = session_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.metadata = metadata

        self.trace_id: str = new_trace_id()

        # EXPORT timestamp (wall clock)
        self.start_wall_ns: int = wall_time_ns()

        self.event_buffer = RingBuffer(capacity=DEFAULT_EVENT_BUFFER_SIZE)

        # span_id -> monotonic start time
        self._span_mono_start: dict[str, int] = {}

        # span metadata
        self._span_meta: dict[str, dict[str, str]] = {}


class AgentSession:
    """
    Main session object for tracing agent execution.
    """

    def __init__(
        self,
        state: SessionState,
        token: Token[Any] | None,
        exporter_worker: ExporterWorkerProtocol,
    ) -> None:
        self._state = state
        self._token = token
        self._exporter_worker = exporter_worker

    def __enter__(self) -> "AgentSession":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        reset_current_session(self._token)
        try:
            envelope = self._build_envelope()
            self._exporter_worker.enqueue(envelope)
        except Exception as e:
            log_internal_error(f"session flush failed: {e}")

    # ---------------- Public API ----------------

    def span(
        self,
        name: str,
        kind: str,
        attributes: dict[str, Any] | None = None,
    ) -> SpanContext:
        span_id = new_span_id()
        parent_span_id = get_current_span()

        self._emit_span_start(
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=name,
            kind=kind,
            attributes=attributes or {},
        )

        return SpanContext(span_id=span_id, session=self)

    def agent_step(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> SpanContext:
        """Helper to create an agent_step span."""
        return self.span(name, kind="agent_step", attributes=attributes)

    def tool_call(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> SpanContext:
        """Helper to create a tool_call span."""
        return self.span(name, kind="tool_call", attributes=attributes)

    def llm_call(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> SpanContext:
        """Helper to create an llm_call span."""
        return self.span(name, kind="llm_call", attributes=attributes)

    def stream(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> StreamSpan:
        span_id = new_span_id()
        parent_span_id = get_current_span()

        self._emit_span_start(
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=name,
            kind="stream",
            attributes=attributes or {},
        )

        return StreamSpan(span_id=span_id, session=self)

    # ---------------- Internal ----------------

    def _build_envelope(self) -> dict[str, Any]:
        events = self._state.event_buffer.drain()

        return {
            "schema_version": SCHEMA_VERSION,
            "session": {
                "session_id": self._state.session_id,
                "agent_id": self._state.agent_id,
                "user_id": self._state.user_id,
                "metadata": self._state.metadata,
                "trace_id": self._state.trace_id,
                "start_time": format_ns(self._state.start_wall_ns),
                "end_time": wall_time_iso(),
            },
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": format_ns(e.timestamp),
                    "type": e.type,
                    "trace": {
                        "trace_id": e.trace_id,
                        "span_id": e.span_id,
                        "parent_span_id": e.parent_span_id,
                    },
                    "payload": e.payload,
                }
                for e in events
            ],
        }

    def _emit_span_start(
        self,
        span_id: str,
        parent_span_id: str | None,
        name: str,
        kind: str,
        attributes: dict[str, Any],
    ) -> None:
        try:
            self._state._span_mono_start[span_id] = mono_time_ns()
            self._state._span_meta[span_id] = {"name": name, "kind": kind}

            self._state.event_buffer.append(
                TraceEvent(
                    event_id=new_event_id(),
                    timestamp=wall_time_ns(),
                    type="span_start",
                    trace_id=self._state.trace_id,
                    span_id=span_id,
                    parent_span_id=parent_span_id,
                    payload={
                        "kind": kind,
                        "name": name,
                        "attributes": attributes,
                    },
                )
            )
        except Exception as e:
            log_internal_error(f"span_start failed: {e}")

    def _emit_span_end(
        self,
        span_id: str,
        error: Exception | None,
    ) -> None:
        try:
            mono_start = self._state._span_mono_start.pop(span_id)
            duration_ns = mono_time_ns() - mono_start
            meta = self._state._span_meta.pop(span_id, {})

            self._state.event_buffer.append(
                TraceEvent(
                    event_id=new_event_id(),
                    timestamp=wall_time_ns(),
                    type="span_end",
                    trace_id=self._state.trace_id,
                    span_id=span_id,
                    parent_span_id=None,
                    payload={
                        "name": meta.get("name"),
                        "kind": meta.get("kind"),
                        "status": "error" if error else "ok",
                        "error": serialize_error(error),
                        "duration_ns": duration_ns,
                    },
                )
            )
        except Exception as e:
            log_internal_error(f"span_end failed: {e}")

    def _emit_stream_event(
        self,
        span_id: str,
        event: str,
        attributes: dict[str, Any],
    ) -> None:
        try:
            self._state.event_buffer.append(
                TraceEvent(
                    event_id=new_event_id(),
                    timestamp=wall_time_ns(),
                    type="stream_event",
                    trace_id=self._state.trace_id,
                    span_id=span_id,
                    parent_span_id=None,
                    payload={
                        "event": event,
                        "attributes": attributes,
                    },
                )
            )
        except Exception as e:
            log_internal_error(f"stream_event failed: {e}")
