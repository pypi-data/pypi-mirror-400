"""
Real-time debugging example.

Demonstrates:
- using ConsoleExporter for immediate, pretty-printed terminal feedback
- inspecting agent thought processes and tool calls live

Run with:
    uv run realtime_debug.py
"""

from agent_observatory import (
    AgentContext,
    ConsoleExporter,
    Observatory,
    trace_agent_step,
)


def run_agent() -> None:
    # Immediate feedback in terminal
    exporter = ConsoleExporter()
    obs = Observatory(exporter=exporter, inline=True)

    ctx = AgentContext(session_id="live-demo-1", agent_id="demo-agent", user_id="dev-user")

    @trace_agent_step("main_loop")
    def process() -> None:
        with obs.start_session(ctx) as session:
            with session.agent_step("thinking"):
                pass

            with session.llm_call("claude-3"):
                pass

            with session.agent_step("done"):
                pass

    process()


if __name__ == "__main__":
    run_agent()
