import secrets
import uuid


def new_trace_id() -> str:
    """Standard OTel TraceID: 16 bytes (32 hex characters)."""
    return uuid.uuid4().hex


def new_span_id() -> str:
    """Standard OTel SpanID: 8 bytes (16 hex characters)."""
    return secrets.token_hex(8)


def new_event_id() -> str:
    """Generic unique ID for events."""
    return uuid.uuid4().hex
