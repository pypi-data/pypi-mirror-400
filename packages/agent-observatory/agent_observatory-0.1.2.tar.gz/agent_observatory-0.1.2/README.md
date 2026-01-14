# Agent Observatory

[![PyPI version](https://img.shields.io/pypi/v/agent-observatory.svg)](https://pypi.org/project/agent-observatory/)
[![Python versions](https://img.shields.io/pypi/pyversions/agent-observatory.svg)](https://pypi.org/project/agent-observatory/)
[![License](https://img.shields.io/pypi/l/agent-observatory.svg)](LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/darshankparmar/agent-observatory)

**Agent Observatory** is a lightweight, fail-open observability layer for **AI agents and agent-based systems**.

It provides structured tracing for:
- agent steps
- tool calls
- LLM interactions
- streaming workflows (tokens, audio, events)
- hierarchical agent execution

Agent Observatory is designed as **infrastructure**, not a platform:
- no UI
- no storage
- no vendor lock-in
- no global side effects

It emits **portable trace envelopes** that can be exported to JSON, OpenTelemetry, or custom backends.


## Why Agent Observatory?

Modern AI agents are:
- long-running
- stateful
- streaming
- hierarchical
- partially autonomous

Traditional request/response tracing breaks down.

Agent Observatory focuses on:
- **agent runtime introspection**
- **streaming-first tracing**
- **minimal overhead**
- **composability with existing observability stacks**


## Core Concepts

### Sessions
A **session** represents a single agent run.

```python
with observatory.start_session(ctx) as session:
    ...
```

A session:

* owns a trace ID
* buffers events
* flushes automatically on exit
* never throws on failure (fail-open)


### Spans

Spans represent logical units of agent work.

```python
with session.agent_step("plan"):
    ...
```

Supported span helpers include:

* `agent_step()`
* `tool_call()`
* `llm_call()`
* `stream()`

Spans can be nested and are tracked via context propagation.


### Streaming Events

Streams are first-class.

```python
with session.stream("audio_stream") as stream:
    stream.event("chunk", {"seq": 1})
```

Streaming events:

* are associated with a span
* are high-frequency safe
* preserve ordering
* export cleanly to OTEL span events


## Architecture Overview

```
┌──────────────┐
│ Agent Code   │
└─────┬────────┘
      │
      ▼
┌──────────────┐
│ AgentSession │
│  (buffering) │
└─────┬────────┘
      │ envelope
      ▼
┌───────────────────────┐
│ Exporter Worker       │
│                       │
│  inline  |  async     │
└─────┬─────────────────┘
      │
      ▼
┌────────────────────────┐
│ Exporter               │
│  JSON | OTEL | Console │
│  File | Custom         │
└────────────────────────┘
```


## Execution Modes (Important)

Agent Observatory supports **two execution modes**.

### Inline Mode

**Use for:** Scripts, notebooks, tests, examples

```python
obs = Observatory(exporter=exporter, inline=True)

with obs.start_session(ctx) as session:
    ...
# automatic flush on exit
```

**Characteristics**

* synchronous
* deterministic
* exporter called immediately
* ideal for short-lived processes


### Server Mode (Long-Running Processes)
**Use for:** Production agents, servers, multi-session apps

```python
obs = Observatory(exporter)  # inline=False
await obs.start()            # start background worker

# ... handle many sessions ...

await obs.shutdown()         # graceful shutdown
```

**Characteristics**

* background worker
* buffered exporting
* backpressure handling
* designed for long-running agents

⚠️ **Important:** Server mode requires explicit shutdown. Use inline mode for short scripts.


## Exporters

### Exporter Contract

All exporters must:

* be **synchronous**
* never raise
* fail open
* accept a full session envelope

```python
class Exporter:
    def export(self, payload: dict) -> None:
        ...
```

### Built-in Exporters

#### JSON Exporter

Useful for debugging and local inspection.

```python
from agent_observatory import JSONExporter

exporter = JSONExporter()
obs = Observatory(exporter=exporter, inline=True)
```

#### Console Exporter

Provides immediate, pretty-printed terminal feedback for development.

```python
from agent_observatory import ConsoleExporter

exporter = ConsoleExporter()
obs = Observatory(exporter=exporter, inline=True)
```

#### File Exporter

Writes traces to disk in JSONL format, compatible with the `obs-view` CLI tool.

```python
from agent_observatory import FileExporter

exporter = FileExporter("logs/traces.jsonl")
obs = Observatory(exporter=exporter, inline=True)
```

#### OpenTelemetry Exporter

Agent Observatory integrates with OpenTelemetry **without owning global state**.

##### Design Contract (Critical)

> Agent Observatory **does not configure OpenTelemetry**.
> Applications must configure the `TracerProvider`.

This is intentional and required for:
- auto-instrumentation
- framework compatibility
- production safety

##### OpenTelemetry Example (Recommended)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from agent_observatory import Observatory, AgentContext
from agent_observatory.exporters.otel import OpenTelemetryExporter


provider = TracerProvider(
    resource=Resource.create({"service.name": "agent-demo"})
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

tracer = trace.get_tracer("agent-demo")
exporter = OpenTelemetryExporter(tracer)

obs = Observatory(exporter=exporter, inline=True)

ctx = AgentContext(
    session_id="demo-session",
    agent_id="demo-agent",
)

with obs.start_session(ctx) as session:
    with session.span("plan", kind="agent_step"):
        pass
```

## CLI Tool

Agent Observatory includes a CLI tool for viewing JSONL trace files:

```bash
# View a trace file
obs-view logs/traces.jsonl

# Tail a trace file in real-time
obs-view -t logs/traces.jsonl
```

The CLI provides:
- Formatted trace visualization
- Real-time tailing support
- Graceful error handling
- Optional Rich-based rendering

## Decorators

Agent Observatory provides decorators for automatic tracing:

```python
from agent_observatory import trace_agent_step, trace_tool_call, trace_llm_call

@trace_agent_step("planning")
def plan_response():
    # Automatically traced as agent_step
    pass

@trace_tool_call("search")
def web_search(query: str):
    # Automatically traced as tool_call
    pass

@trace_llm_call("gpt-4")
async def call_llm(prompt: str):
    # Automatically traced as llm_call
    pass
```

Decorators work with both sync and async functions and automatically detect the active session.

## Timestamp Semantics

- Internal event timestamps use **wall-clock nanoseconds** for global correlation
- Duration measurements use **monotonic clock** for accuracy
- All timestamps are ISO-8601 formatted in exports


## Failure Semantics

Agent Observatory is **fail-open by design**.

* exporter failures do not crash agents
* queue overflows drop traces
* internal errors are logged only
* agent execution is never blocked

This is intentional.


## What Agent Observatory Is NOT

* ❌ Not a tracing backend
* ❌ Not a UI
* ❌ Not a metrics system
* ❌ Not a logging framework
* ❌ Not opinionated about storage

It is a **runtime observability primitive**.


## When to Use Agent Observatory

Use it if you are building:

* AI agents
* multi-step reasoning systems
* streaming LLM pipelines
* LiveKit / real-time agents
* tool-heavy autonomous workflows

## Installation

```bash
# Core only (zero dependencies)
pip install agent-observatory

# With OpenTelemetry
pip install agent-observatory[otel]

# With CLI tool
pip install agent-observatory[cli]

# All extras
pip install agent-observatory[all]
```

## Versioning & Stability

* `v0.x` - APIs may evolve
* Core design principles are stable
* Exporter contract is stable
* Inline vs async semantics are stable


## Contributing

Contributions are welcome.

Please respect:

* synchronous exporter contract
* fail-open guarantees
* zero global side effects
* minimal dependencies

See `CONTRIBUTING.md`.


## Feedback Welcome

Agent Observatory is early-stage infrastructure.

Design feedback, critique and edge-case discussion are very welcome.
Please open a Discussion or Issue.
