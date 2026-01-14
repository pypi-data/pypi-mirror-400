import asyncio
from typing import Any

from agent_observatory import (
    AgentContext,
    Observatory,
    trace_agent_step,
    trace_llm_call,
)


def test_basic_span_emission(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.span("step1", kind="agent_step"):
            pass

    payload = exporter.payloads[0]
    events = payload["events"]

    assert len(events) == 2
    assert events[0]["type"] == "span_start"
    assert events[0]["payload"]["name"] == "step1"

    assert events[1]["type"] == "span_end"
    assert events[1]["payload"]["status"] == "ok"


def test_nested_spans_parent_child(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.span("parent", kind="agent_step"):
            with session.span("child", kind="agent_step"):
                pass

    events = exporter.payloads[0]["events"]

    parent_start = events[0]
    child_start = events[1]

    assert child_start["trace"]["parent_span_id"] == parent_start["trace"]["span_id"]


def test_session_helpers(observatory: Observatory, agent_ctx: AgentContext, exporter: Any) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.agent_step("my_step"):
            pass
        with session.tool_call("my_tool"):
            pass
        with session.llm_call("my_llm"):
            pass

    events = exporter.payloads[0]["events"]
    assert any(e["type"] == "span_start" and e["payload"]["kind"] == "agent_step" for e in events)
    assert any(e["type"] == "span_start" and e["payload"]["kind"] == "tool_call" for e in events)
    assert any(e["type"] == "span_start" and e["payload"]["kind"] == "llm_call" for e in events)


def test_span_event_alias(observatory: Observatory, agent_ctx: AgentContext, exporter: Any) -> None:
    with observatory.start_session(agent_ctx) as session:
        with session.agent_step("step") as span:
            span.event("foo", {"a": 1})

    events = exporter.payloads[0]["events"]
    stream_event = next(e for e in events if e["type"] == "stream_event")
    assert stream_event["payload"]["event"] == "foo"


class MyAgent:
    def __init__(self, session: Any) -> None:
        self.session = session

    @trace_agent_step("decorated_step")
    def run_step(self) -> str:
        return "done"


def test_decorator_agent_step(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx) as session:
        agent = MyAgent(session)
        agent.run_step()

    events = exporter.payloads[0]["events"]
    span_start = next(
        (
            e
            for e in events
            if e["type"] == "span_start" and e["payload"]["name"] == "decorated_step"
        ),
        None,
    )
    assert span_start is not None
    assert span_start["payload"]["kind"] == "agent_step"


@trace_llm_call("decorated_llm")
async def call_llm_async() -> str:
    return "chunk"


def test_decorator_llm_call(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx):
        asyncio.run(call_llm_async())

    events = exporter.payloads[0]["events"]
    span_start = next(
        e for e in events if e["type"] == "span_start" and e["payload"]["name"] == "decorated_llm"
    )
    assert span_start["payload"]["kind"] == "llm_call"


@trace_agent_step("ambient_step")
def run_ambient_step() -> str:
    return "ok"


def test_decorator_ambient_session(
    observatory: Observatory, agent_ctx: AgentContext, exporter: Any
) -> None:
    with observatory.start_session(agent_ctx):
        run_ambient_step()

    events = exporter.payloads[0]["events"]
    span_start = next(
        e for e in events if e["type"] == "span_start" and e["payload"]["name"] == "ambient_step"
    )
    assert span_start is not None
