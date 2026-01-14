"""
File logging example.

Demonstrates:
- using FileExporter to persist traces to disk
- JSONL format compatible with the obs-view CLI
- automatic session flushing to file

Run with:
    uv run file_logging.py

View with:
    uv run obs-view logs\traces.jsonl
"""

from agent_observatory import (
    AgentContext,
    FileExporter,
    Observatory,
    trace_agent_step,
)


def run_agent() -> None:
    # Use FileExporter for CLI verification
    exporter = FileExporter("logs/traces.jsonl")
    obs = Observatory(exporter=exporter, inline=True)

    ctx = AgentContext(session_id="cli-demo-1", agent_id="demo-agent", user_id="dev-user")

    @trace_agent_step("main_loop")
    def process() -> None:
        with obs.start_session(ctx) as session:
            with session.agent_step("planning"):
                pass

            with session.llm_call("gpt-4"):
                pass

            with session.tool_call("web_search", attributes={"query": "python cli"}):
                pass

            with session.agent_step("final_response"):
                pass

    process()
    print("Traces written to logs/traces.jsonl")


if __name__ == "__main__":
    run_agent()
