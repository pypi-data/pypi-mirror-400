# Streaming Agent Example

This example demonstrates **streaming-first observability**.

It shows how to:

- create a stream span
- emit high-frequency events
- preserve ordering
- associate events with spans

## Typical Use Cases

- token streaming
- audio chunks
- tool output streams
- real-time agent feedback

## Running

```bash
uv run stream_processing.py
```

## Key Takeaway

Streams are first-class citizens in Agent Observatory.
They are designed to be cheap, ordered and export cleanly.