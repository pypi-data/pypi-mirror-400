from contextvars import Token
from typing import Any, Literal

from .context import reset_current_span, set_current_span


class SpanContext:
    """
    A context manager representing a logical period of work (a span) in an agent run.
    Spans can be nested to create parent-child relationships.
    """

    def __init__(self, span_id: str, session: Any) -> None:
        self.span_id = span_id
        self._session = session
        self._token: Token[str | None] | None = None

    def _emit_event(
        self,
        event: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self._session._emit_stream_event(
            span_id=self.span_id,
            event=event,
            attributes=attributes or {},
        )

    def event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Emit a structured event within this span."""
        self._emit_event(name, attributes)

    def __enter__(self) -> "SpanContext":
        self._token = set_current_span(self.span_id)
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> Literal[False]:
        try:
            self._session._emit_span_end(
                span_id=self.span_id,
                error=exc,
            )
        finally:
            if self._token is not None:
                reset_current_span(self._token)
        return False


class StreamSpan:
    """
    A persistent reference to a span context designed for high-frequency event streaming.
    Unlike SpanContext, it does not manage ambient context via ContextVars.
    """

    def __init__(self, span_id: str, session: Any) -> None:
        self.span_id = span_id
        self._session = session

    def _emit_event(
        self,
        event: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self._session._emit_stream_event(
            span_id=self.span_id,
            event=event,
            attributes=attributes or {},
        )

    def event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Emit a structured event within this stream."""
        self._emit_event(name, attributes)

    def __enter__(self) -> "StreamSpan":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> Literal[False]:
        self._session._emit_span_end(
            span_id=self.span_id,
            error=exc,
        )
        return False
