"""
OpenTelemetry integration example.

Demonstrates:
- explicit OpenTelemetry configuration
- integration via OpenTelemetryExporter
- zero global state ownership by Agent Observatory
- streaming + hierarchical spans

Requirements:
- running OpenTelemetry backend (e.g. OTEL Collector)
- OTLP endpoint available at http://127.0.0.1:4317

Run with:
    uv run otel_integration.py
"""

import asyncio
import random
from importlib.metadata import version

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from agent_observatory import AgentContext, Observatory, OpenTelemetryExporter


# ---------------------------------------------------------
# 1. Configure OpenTelemetry (application-owned)
# ---------------------------------------------------------
def configure_otel() -> None:
    """
    Configure OpenTelemetry for the application.

    IMPORTANT:
    - Agent Observatory does NOT configure OpenTelemetry.
    - This must be done by the application.
    """
    SERVICE_VERSION = version("agent-observatory")

    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "agent-observatory-demo",
                "service.version": SERVICE_VERSION,
            }
        )
    )

    provider.add_span_processor(
        SimpleSpanProcessor(
            OTLPSpanExporter(
                endpoint="http://127.0.0.1:4317",
                insecure=True,
            )
        )
    )

    trace.set_tracer_provider(provider)


# ---------------------------------------------------------
# 2. Simulated agent workflow
# ---------------------------------------------------------
async def run_agent(obs: Observatory) -> None:
    # --- Agent context ---
    ctx = AgentContext(
        session_id="session_001",
        agent_id="demo-agent",
        user_id="demo-user",
        metadata={"env": "local"},
    )

    # Root span owned by the application
    tracer = trace.get_tracer("agent-demo")

    with tracer.start_as_current_span("agent.run") as root:
        root.set_attribute("agent.id", ctx.agent_id)
        root.set_attribute("session.id", ctx.session_id)

        # --- Agent Observatory session ---
        with obs.start_session(ctx) as session:
            # ---- Planning step
            with session.agent_step("plan") as span:
                span.event("planning.started")
                await asyncio.sleep(0.1)
                span.event("planning.completed")

            # ---- Streaming output (tokens / audio / chunks)
            with session.stream("response_stream") as stream:
                for i in range(5):
                    stream.event(
                        "chunk",
                        {
                            "index": i,
                            "text": f"token-{i}",
                        },
                    )
                    await asyncio.sleep(0.05)

            # ---- Final step with possible error
            try:
                with session.agent_step("finalize"):
                    if random.random() < 0.3:
                        raise RuntimeError("model timeout")
                    await asyncio.sleep(0.05)
            except Exception as e:
                # Application-level error handling
                root.record_exception(e)
                root.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))


# ---------------------------------------------------------
# 3. Entrypoint
# ---------------------------------------------------------
async def main() -> None:
    # --- OpenTelemetry setup ---
    configure_otel()

    tracer = trace.get_tracer("agent-demo")
    exporter = OpenTelemetryExporter(tracer)

    # Inline mode for simplicity and determinism in examples
    obs = Observatory(exporter=exporter, inline=True)

    await run_agent(obs)

    # Safe to call even in inline mode
    await obs.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
