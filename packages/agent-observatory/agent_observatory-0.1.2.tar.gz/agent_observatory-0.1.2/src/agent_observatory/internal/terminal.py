import json
from typing import Any

from ..runtime.clock import format_ns

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.theme import Theme
except ImportError:
    # Minimal fallback
    class Console:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...
        def print(self, *args: Any, **kwargs: Any) -> None:
            print(*args)

    class Panel:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    class Table:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    class Theme:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    class Text:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: ...
        @property
        def plain(self) -> str:
            return ""

        def append(self, *args: Any, **kwargs: Any) -> None: ...


CUSTOM_THEME = Theme(
    {
        "session": "bold blue",
        "agent_step": "green",
        "tool_call": "yellow",
        "llm_call": "magenta",
        "stream": "cyan",
        "error": "bold red",
        "timestamp": "dim white",
    }
)

console = Console(theme=CUSTOM_THEME)


def render_timestamp(ts: int | str | None) -> str:
    """
    Render a timestamp safely.

    Rules:
    - int   -> wall-clock nanoseconds → format_ns()
    - str   -> already formatted → return as-is
    - other -> placeholder
    """
    if isinstance(ts, int):
        return format_ns(ts)
    if isinstance(ts, str):
        return ts
    return "-"


def render_session_envelope(payload: dict[str, Any]) -> None:
    session = payload.get("session", {})
    events = payload.get("events", [])

    header_text = Text()
    header_text.append("Session: ", style="session")
    header_text.append(str(session.get("session_id", "unknown")), style="bold")
    header_text.append(f" | Agent: {session.get('agent_id', 'unknown')}", style="dim")
    header_text.append(f" | User: {session.get('user_id', 'none')}", style="dim")

    if Panel is not None:
        console.print(Panel(header_text, border_style="blue"))
    else:
        console.print(f"=== {header_text.plain} ===")

    if Table is None:
        for ev in events:
            console.print(f"  {ev.get('type')}: {ev.get('payload')}")
        return

    table = Table(box=None, show_header=True, padding=(0, 1))
    table.add_column("Time", style="timestamp")
    table.add_column("Type", width=12)
    table.add_column("Details")

    for ev in events:
        ev_type = str(ev.get("type", "unknown"))
        data = ev.get("payload", {})
        ts = render_timestamp(ev.get("timestamp", ""))

        type_style = "white"
        details = Text()

        if ev_type == "span_start":
            kind = str(data.get("kind", "internal"))
            type_style = kind
            details.append(f"-> START {kind}: ", style=type_style)
            details.append(str(data.get("name", "")), style="bold")
            if data.get("attributes"):
                details.append(f" {json.dumps(data['attributes'])}", style="dim")

        elif ev_type == "span_end":
            kind = str(data.get("kind", "internal"))
            type_style = kind
            status = str(data.get("status", "ok"))
            status_style = "green" if status == "ok" else "error"
            details.append(f"<- END {kind}: ", style=type_style)
            details.append(str(data.get("name", "")), style="bold")
            details.append(f" [{status}]", style=status_style)
            if data.get("error"):
                details.append(f"\n  Error: {data['error']}", style="error")

        elif ev_type == "stream_event":
            details.append(f"  ~ {data.get('event', 'event')}", style="stream")
            if data.get("attributes"):
                details.append(f" {json.dumps(data['attributes'])}", style="dim")

        table.add_row(ts, Text(ev_type, style=type_style), details)

    console.print(table)
    console.print()
