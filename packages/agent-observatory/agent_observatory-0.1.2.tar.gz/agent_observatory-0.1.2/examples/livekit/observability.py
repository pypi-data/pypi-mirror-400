"""
Agent Observatory + OpenTelemetry setup for LiveKit agents.

This module is responsible for:
- configuring OpenTelemetry (once per process)
- creating an Agent Observatory instance
- keeping observability concerns isolated from agent logic

This file is imported by the LiveKit server and agent code.
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from agent_observatory import Observatory, OpenTelemetryExporter


def configure_otel() -> None:
    """
    Configure OpenTelemetry ONCE per process.

    IMPORTANT:
    - Agent Observatory does NOT configure OpenTelemetry.
    - This function must be called by the application.
    - Safe to call at process startup.
    """
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "livekit-agent",
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


def create_observatory() -> Observatory:
    """
    Create and return an Agent Observatory instance.

    DESIGN NOTES:
    - Uses OpenTelemetryExporter
    - Inline mode is appropriate for agent lifecycles
    - No global state is owned by Agent Observatory
    """
    tracer = trace.get_tracer("livekit-agent")
    exporter = OpenTelemetryExporter(tracer)

    # Inline mode ensures deterministic export per agent run
    return Observatory(exporter=exporter, inline=True)
