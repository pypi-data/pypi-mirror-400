from agent_observatory import AgentContext, Observatory
from agent_observatory.exporters.base import Exporter


class FailingExporter(Exporter):
    def export(self, payload: dict) -> None:
        raise RuntimeError("boom")


def test_exporter_failure_does_not_crash(agent_ctx: AgentContext) -> None:
    obs = Observatory(exporter=FailingExporter())

    with obs.start_session(agent_ctx) as session:
        with session.span("safe", kind="agent_step"):
            pass
