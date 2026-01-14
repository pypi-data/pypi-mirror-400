# Basic Agent Example

This is the **simplest possible usage** of Agent Observatory.

It demonstrates:

- inline execution mode
- a single agent session
- basic span usage
- `ConsoleExporter` for live terminal feedback
- `FileExporter` for logging to JSONL files (compatible with CLI)

## Files

- [`basic_tracing.py`](basic_tracing.py): Minimal usage with `JSONExporter`.
- [`realtime_debug.py`](realtime_debug.py): Real-time pretty-printing with `ConsoleExporter`.
- [`file_logging.py`](file_logging.py): Logging to `traces.jsonl` for use with `obs-view`.

## Running

```bash
# Basic usage
uv run basic_tracing.py

# Live console feedback
uv run realtime_debug.py

# CLI demo (logging to file)
uv run file_logging.py

# View logs with CLI tool
uv run obs-view logs\traces.jsonl
```

## Key Takeaway

Use **inline mode** when:

* running scripts
* writing tests
* experimenting locally