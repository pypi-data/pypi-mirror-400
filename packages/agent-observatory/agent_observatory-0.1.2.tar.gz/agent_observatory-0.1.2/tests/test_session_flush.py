from typing import Any

from agent_observatory import AgentContext, Observatory


def test_flush_happens_on_session_exit(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.span("work", kind="agent_step"):
            pass

    assert len(exporter.payloads) == 1

    payload = exporter.payloads[0]
    assert payload["session"]["session_id"] == "test_session"
    assert "events" in payload
