import json
from pathlib import Path

from agent_observatory import AgentContext, ConsoleExporter, FileExporter, Observatory


def test_file_exporter_appends_jsonl(agent_ctx: AgentContext, tmp_path: Path) -> None:
    log_file = tmp_path / "test.jsonl"

    exporter = FileExporter(str(log_file))
    obs = Observatory(exporter=exporter, inline=True)

    with obs.start_session(agent_ctx) as session:
        with session.agent_step("step1"):
            pass

    # Read and verify
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8").strip()
    payload = json.loads(content)

    assert payload["session"]["session_id"] == agent_ctx.session_id
    assert len(payload["events"]) == 2  # span_start, span_end


def test_console_exporter_does_not_crash(agent_ctx: AgentContext) -> None:
    exporter = ConsoleExporter()
    obs = Observatory(exporter=exporter, inline=True)

    # We just ensure it doesn't raise anything when printing
    with obs.start_session(agent_ctx) as session:
        with session.agent_step("visual_test"):
            pass
