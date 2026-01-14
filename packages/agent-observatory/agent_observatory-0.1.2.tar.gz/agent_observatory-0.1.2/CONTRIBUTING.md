# Contributing to Agent Observatory

Thank you for your interest in contributing to **Agent Observatory**.

This project is an **infrastructure-level observability library**.
Contributions are welcome, but must respect the core design principles outlined below.

Please read this document carefully before opening issues or pull requests.

---

## Project Philosophy (Read First)

Agent Observatory is intentionally:

- **Fail-open**  
  Observability must never break agent execution.

- **Minimal**  
  No UI, no storage, no SaaS, no vendor lock-in.

- **Composable**  
  Must coexist cleanly with OpenTelemetry, logging frameworks and existing infrastructure.

- **Runtime-focused**  
  Designed for agent systems, streaming workflows and long-lived processes.

If a change violates these principles, it is unlikely to be accepted.

---

## Design Guarantees (Non-Negotiable)

The following constraints are **hard guarantees** of the project.

### 1. No Global Side Effects

Agent Observatory **must not**:

- configure OpenTelemetry
- mutate global tracer providers
- modify logging configuration
- install signal handlers
- manage process lifecycle

All global configuration belongs to the **application**, not the library.

---

### 2. Exporters Are Synchronous

Exporter implementations **must**:

- expose a synchronous `export(payload)` method
- never raise exceptions
- fail open under all circumstances

```python
class Exporter:
    def export(self, payload: dict) -> None:
        ...
````

Async exporters are explicitly **out of scope for v0.x**.

---

### 3. Fail-Open Semantics

The following rules apply everywhere:

* exporter failures must not crash sessions
* queue overflows must drop traces, not block agents
* internal errors are logged only
* user code must never be forced to handle observability failures

If observability breaks agent execution, it is a bug.

---

### 4. Inline vs Async Execution Modes

Agent Observatory supports two execution modes:

* **Inline mode** (`inline=True`)
  Deterministic and synchronous.
  Used for scripts, tests and examples.

* **Async mode** (`inline=False`)
  Background worker with buffering.
  Used for long-running services.

Contributions must respect this split and not blur the semantics.

---

## What to Contribute

We welcome contributions in the following areas.

### ✅ Good Contribution Areas

* new exporters (e.g. OTEL variants, file-based exporters)
* performance improvements
* memory usage optimizations
* streaming improvements
* test coverage
* documentation and examples
* bug fixes with clear reproduction

---

### ❌ Out of Scope (v0.x)

The following will not be accepted in v0.x:

* dashboards or UI
* persistence layers
* metrics backends
* async exporter interfaces
* automatic OpenTelemetry configuration
* background threads in inline mode
* opinionated defaults that remove user control

These may be discussed for future versions, but should not be merged casually.

---

## Development Setup

### Requirements

* Python 3.10+
* `uv` or `pip`
* `pytest`
* `mypy`

> **Note:**
> The project uses **Hatch** for development workflows (linting, testing, builds).
> Hatch is a **developer tool only** and is not a runtime dependency.

Install Hatch if you want to use the provided scripts:

```bash
uv pip install hatch
```

---

### Sync dependencies

```bash
uv sync --all-extras
```

---

### Common development commands (recommended)

Using Hatch (preferred):

```bash
uv run hatch run lint
uv run hatch run test
uv run hatch run build-all
```

These commands run:

* formatting (`black`)
* linting (`ruff`)
* type checking (`mypy`)
* tests (`pytest`)
* build verification (`hatch build`)

You may also run the tools directly if you prefer.

---

Without Hatch:

```bash
uv run pytest
uv run mypy .
uv run black .
uv run ruff check --fix .
```

---

## Testing Guidelines

All contributions **must include tests** where applicable.

Key expectations:

* tests must not depend on global state
* OpenTelemetry tests must not configure global providers
* exporters should be testable in isolation
* inline mode must be deterministic

If a change cannot be tested, explain why in the PR.

---

## Documentation Expectations

If you change:

* public APIs
* execution semantics
* exporter behavior
* failure semantics

You **must** update:

* `README.md`
* examples (if applicable)

Documentation is part of the API contract.

---

## Pull Request Guidelines

When opening a PR, please include:

1. **What problem does this solve?**
2. **Why does it belong in Agent Observatory?**
3. **How does it preserve fail-open behavior?**
4. **Which execution mode does it affect (inline / async)?**
5. **Tests added or updated**

Low-context PRs are likely to be closed.

---

## Issues & Discussions

Please use:

* **Issues** for concrete bugs and actionable proposals
* **Discussions** for design questions or architectural ideas

When reporting bugs, include:

* minimal reproduction
* execution mode (`inline` or `async`)
* exporter used
* Python version

---

## Code Style

* Favor clarity over cleverness
* Avoid unnecessary abstractions
* Prefer explicit over implicit behavior
* No magic globals
* No silent background work

This is infrastructure code - predictability matters more than elegance.

---

## Final Note

Agent Observatory aims to be a **trustworthy observability primitive**.

We value:

* correctness over features
* explicit contracts over convenience
* long-term maintainability over short-term wins

If you’re unsure whether a change fits, open a discussion first.

Thank you for contributing.