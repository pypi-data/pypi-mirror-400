from typing import Any

from agent_observatory import AgentContext, Observatory


def test_high_frequency_streaming(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.stream("audio") as stream:
            for i in range(1_000):
                stream.event(
                    "chunk",
                    {"seq": i, "bytes": 4096},
                )

    payload = exporter.payloads[0]
    events = payload["events"]

    stream_events = [e for e in events if e["type"] == "stream_event"]
    assert len(stream_events) == 1000
    assert stream_events[0]["payload"]["event"] == "chunk"
