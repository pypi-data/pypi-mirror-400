import asyncio

from .context import AgentContext, set_current_session
from .exporters.base import Exporter
from .exporters.worker import (
    ExporterWorker,
    ExporterWorkerProtocol,
    InlineExporterWorker,
)
from .session import AgentSession, SessionState


class Observatory:
    """
    The main entry point for the Agent Observatory library.
    Manages the lifecycle of agent sessions and ensures events are correctly exported.
    """

    def __init__(self, exporter: Exporter, *, inline: bool = False) -> None:
        """
        Initialize the observatory.

        Args:
            exporter: The exporter to use for session envelopes.
            inline: If True, exports happen synchronously on the same thread (ideal for CLI/scripts).
                   If False, exports happen on a background thread.
        """
        self._exporter = exporter
        self._inline = inline

        self._worker: ExporterWorkerProtocol
        self._worker_task: asyncio.Task[None] | None = None

        if inline:
            self._worker = InlineExporterWorker(exporter)
        else:
            self._worker = ExporterWorker(exporter)

    async def start(self) -> None:
        if self._inline:
            return

        worker = self._worker
        assert isinstance(worker, ExporterWorker)

        if self._worker_task is None:
            self._worker_task = asyncio.create_task(worker.start())

    def start_session(self, ctx: AgentContext) -> AgentSession:
        """
        Start a new agent session.
        Returns an AgentSession context manager.
        """
        state = SessionState(
            session_id=ctx.session_id,
            agent_id=ctx.agent_id,
            user_id=ctx.user_id,
            metadata=ctx.metadata or {},
        )
        # We create the session first, then set it in context so decorators
        # find the actual session object (which has .span, .agent_step, etc.)
        session = AgentSession(state, None, self._worker)
        token = set_current_session(session)
        session._token = token
        return session

    async def shutdown(self) -> None:
        if self._inline:
            return

        worker = self._worker
        assert isinstance(worker, ExporterWorker)

        await worker.stop()
        self._worker_task = None
