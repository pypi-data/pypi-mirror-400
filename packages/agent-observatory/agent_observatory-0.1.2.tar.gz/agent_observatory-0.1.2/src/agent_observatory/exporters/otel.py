from typing import Any

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace import (
    Span,
    SpanKind,
    Status,
    StatusCode,
    Tracer,
)

from .base import Exporter


class OpenTelemetryExporter(Exporter):
    """
    OpenTelemetry exporter for Agent Observatory.

    CONTRACT:
    - Consumes an already-configured Tracer
    - Does NOT configure OpenTelemetry
    - Synchronous and fail-open
    """

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    # -----------------------------------------------------
    # Export entrypoint
    # -----------------------------------------------------
    def export(self, payload: dict[str, Any]) -> None:
        """
        Translate an Agent Observatory session envelope into
        OpenTelemetry spans and events.

        Fail-open by design: exporter errors must never affect
        agent execution.
        """
        try:
            events: list[dict[str, Any]] = payload.get("events", [])

            # span_id -> OTEL Span
            spans: dict[str, Span] = {}

            # span_id -> parent_span_id
            parents: dict[str, str | None] = {}

            # -------------------------------------------------
            # Pass 1: collect parent relationships
            # -------------------------------------------------
            for ev in events:
                if ev.get("type") == "span_start":
                    trace_info = ev["trace"]
                    parents[trace_info["span_id"]] = trace_info.get("parent_span_id")

            # -------------------------------------------------
            # Pass 2: start spans
            # -------------------------------------------------
            for ev in events:
                if ev.get("type") != "span_start":
                    continue

                trace_info = ev["trace"]
                payload_data = ev["payload"]

                span_id = trace_info["span_id"]
                parent_id = parents.get(span_id)

                parent_span = spans.get(parent_id) if parent_id else None

                # Explicit context handling to avoid ambient leakage
                if parent_span is not None:
                    parent_ctx: Context = trace.set_span_in_context(parent_span)
                else:
                    parent_ctx = Context()

                span = self._tracer.start_span(
                    name=payload_data.get("name", "agent_span"),
                    context=parent_ctx,
                    kind=self._map_kind(payload_data.get("kind")),
                )

                for k, v in payload_data.get("attributes", {}).items():
                    span.set_attribute(k, v)

                spans[span_id] = span

            # -------------------------------------------------
            # Pass 3: stream events → OTEL span events
            # -------------------------------------------------
            for ev in events:
                if ev.get("type") != "stream_event":
                    continue

                trace_info = ev["trace"]
                payload_data = ev["payload"]

                span_opt = spans.get(trace_info["span_id"])
                if span_opt is None:
                    continue

                span = span_opt

                span.add_event(
                    name=payload_data.get("event", "stream.event"),
                    attributes=payload_data.get("attributes", {}),
                )

            # -------------------------------------------------
            # Pass 4: end spans
            # -------------------------------------------------
            for ev in events:
                if ev.get("type") != "span_end":
                    continue

                span_opt = spans.get(ev["trace"]["span_id"])
                if span_opt is None:
                    continue

                span = span_opt

                payload_data = ev["payload"]

                if payload_data.get("status") == "error":
                    err = payload_data.get("error") or {}
                    message = err.get("message", "agent error")

                    span.record_exception(Exception(message))
                    span.set_status(Status(StatusCode.ERROR, message))

                span.end()

        except Exception:
            return

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    def _map_kind(self, kind: str | None) -> SpanKind:
        return {
            "agent_step": SpanKind.INTERNAL,
            "llm_call": SpanKind.CLIENT,
            "tool_call": SpanKind.CLIENT,
            "stream": SpanKind.INTERNAL,
        }.get(kind or "", SpanKind.INTERNAL)
