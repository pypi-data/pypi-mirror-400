"""
LiveKit server entrypoint with Agent Observatory integration.

This example demonstrates:
- one LiveKit RTC session == one Agent Observatory session
- server-mode agent lifecycle
- structured metrics and tool observability
- clean separation between infrastructure and agent logic
"""

import logging
from typing import Any

from agent import MyAgent
from dotenv import load_dotenv
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    metrics,
    room_io,
)
from livekit.plugins import cartesia, deepgram, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from observability import configure_otel, create_observatory

from agent_observatory import AgentContext

logger = logging.getLogger("server")

# Load environment variables for LiveKit / providers
load_dotenv()

# -----------------------------------------------------------------------------
# LiveKit server setup
# -----------------------------------------------------------------------------

server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """
    Preload resources once per worker process.

    Used here to load the VAD model so it can be reused
    across multiple agent sessions.
    """
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit RTC session entrypoint.

    IMPORTANT:
    - One LiveKit RTC session maps to one Agent Observatory session.
    - Observability is scoped to the lifetime of this function.
    """
    # --- Observatory setup ---
    observatory = create_observatory()

    room_sid = str(ctx.room.sid)

    # --- Agent context ---
    agent_ctx = AgentContext(
        session_id=room_sid,
        agent_id="livekit-agent",
        metadata={
            "room": ctx.room.name,
            "job_id": ctx.job.id,
        },
    )

    # --- Agent Observatory session ---
    with observatory.start_session(agent_ctx) as obs_session:
        logger.info("Agent session started")

        # --- LiveKit agent session ---
        session: AgentSession = AgentSession(
            stt=deepgram.STT(),
            llm=openai.LLM(model="openai/gpt-4.1-mini"),
            tts=cartesia.TTS(),
            turn_detection=MultilingualModel(),
            vad=ctx.proc.userdata["vad"],
            preemptive_generation=True,
            resume_false_interruption=True,
            false_interruption_timeout=1.0,
        )

        usage_collector = metrics.UsageCollector()

        @session.on("metrics_collected")
        def _on_metrics_collected(ev: Any) -> None:
            """
            Capture LiveKit usage metrics and attach them
            as structured observability events.
            """
            usage_collector.collect(ev.metrics)

            with obs_session.agent_step("metrics.snapshot") as span:
                span.event(
                    "metrics.collected",
                    ev.metrics,
                )

        async def log_usage() -> None:
            """
            Log usage summary on session shutdown.
            """
            summary = usage_collector.get_summary()
            logger.info("Usage summary: %s", summary)

        # Register shutdown callback
        ctx.add_shutdown_callback(log_usage)

        # --- Start agent ---
        await session.start(
            agent=MyAgent(obs_session),
            room=ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions(),
            ),
        )

        logger.info("Agent session ended")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Configure OpenTelemetry once at process startup
    configure_otel()

    # Start LiveKit agent server
    cli.run_app(server)
