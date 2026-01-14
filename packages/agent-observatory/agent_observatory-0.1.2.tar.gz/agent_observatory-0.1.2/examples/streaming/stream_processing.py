"""
Streaming Agent Observatory example.

Demonstrates:
- stream spans
- high-frequency event emission
- ordered streaming events

Run with:
    uv run stream_processing.py
"""

from agent_observatory import AgentContext, JSONExporter, Observatory


def run_streaming_agent() -> None:
    # --- Observatory setup ---
    # Inline mode for demo purposes.
    # Use async worker mode for production systems.
    obs = Observatory(
        exporter=JSONExporter(),
        inline=True,
    )

    # --- Agent context ---
    ctx = AgentContext(
        session_id="streaming-session-1",
        agent_id="streaming-agent",
        user_id="stream-user",
        metadata={"env": "prod"},
    )

    # --- Agent session ---
    with obs.start_session(ctx) as session:
        # --- Stream span ---
        # Streams are first-class and support high-frequency events.
        with session.stream(
            "audio_stream",
            attributes={
                "codec": "opus",
                "sample_rate": 48_000,
            },
        ) as stream:
            for i in range(1_000):
                stream.event(
                    "audio.chunk",
                    {
                        "seq": i,
                        "bytes": 4_096,
                        "duration_ms": 20,
                    },
                )


if __name__ == "__main__":
    run_streaming_agent()
