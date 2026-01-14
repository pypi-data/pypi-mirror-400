# OpenTelemetry Integration Example

This example demonstrates how to integrate Agent Observatory
with an existing OpenTelemetry setup.

## Important Design Rule

> Agent Observatory **does not configure OpenTelemetry**.

The application must configure:

- `TracerProvider`
- exporters
- processors

This avoids global side effects and ensures compatibility
with auto-instrumentation and frameworks.

## What This Example Shows

- explicit OTEL configuration
- using `OpenTelemetryExporter`
- coexistence of application spans and agent spans
- streaming and hierarchical traces

## Running

You must have an OpenTelemetry backend running
(e.g. Collector, Jaeger, Tempo).

```bash
uv run otel_integration.py
```

## Key Takeaway

Agent Observatory fits *into* your observability stack.
It does not try to own it.