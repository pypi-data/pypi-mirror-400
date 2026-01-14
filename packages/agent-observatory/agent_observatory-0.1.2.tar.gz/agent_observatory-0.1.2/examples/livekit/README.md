# LiveKit Agent Example

This is a **real-world, production-style agent example**
using LiveKit and Agent Observatory.

It demonstrates:

- long-running server execution
- agent lifecycle instrumentation
- structured metrics events
- separation of observability and business logic

## File Overview

- [`server.py`](server.py): LiveKit server entrypoint
- [`agent.py`](agent.py): agent logic with observability
- [`observability.py`](observability.py): OpenTelemetry + Observatory setup

## Execution Model

This example uses **server-style execution**:

- one LiveKit RTC session == one Agent Observatory session
- sessions flush automatically on exit
- OpenTelemetry is configured once per process

## Running

Before running, ensure:

- LiveKit is configured
- required plugins are installed
- an OTEL backend is running (optional but recommended)

```bash
uv run server.py console
```

## Key Takeaway

Use this pattern for:

* production agents
* real-time systems
* multi-session servers