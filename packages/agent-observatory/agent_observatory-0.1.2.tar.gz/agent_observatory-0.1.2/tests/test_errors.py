from typing import Any

import pytest

from agent_observatory import AgentContext, Observatory


def test_span_error_is_recorded(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with pytest.raises(ValueError):
        with observatory.start_session(agent_ctx) as session:
            with session.span("boom", kind="agent_step"):
                raise ValueError("failure")

    events = exporter.payloads[0]["events"]
    span_end = events[-1]

    assert span_end["type"] == "span_end"
    assert span_end["payload"]["status"] == "error"
    assert span_end["payload"]["error"]["type"] == "ValueError"
