from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentContext:
    session_id: str
    agent_id: str
    user_id: str | None = None
    metadata: dict[str, Any] | None = None


_current_session: ContextVar[Any] = ContextVar(
    "current_session",
    default=None,
)
_current_span: ContextVar[str | None] = ContextVar(
    "current_span",
    default=None,
)


def get_current_session() -> Any:
    return _current_session.get()


def set_current_session(session: Any) -> Token[Any]:
    return _current_session.set(session)


def reset_current_session(token: Token[Any] | None) -> None:
    if token is not None:
        _current_session.reset(token)


def get_current_span() -> str | None:
    return _current_span.get()


def set_current_span(span_id: str) -> Token[str | None]:
    return _current_span.set(span_id)


def reset_current_span(token: Token[str | None]) -> None:
    _current_span.reset(token)
