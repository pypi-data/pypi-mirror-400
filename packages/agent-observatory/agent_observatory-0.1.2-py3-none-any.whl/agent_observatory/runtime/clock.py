"""
Clock utilities with strict separation of concerns.

Design rules:
- Wall clock is used ONLY for exported timestamps (Jaeger-safe)
- Monotonic clock is used ONLY for duration and ordering
- Never mix clocks
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Wall clock (EXPORT ONLY)
# ---------------------------------------------------------------------------


def wall_time_ns() -> int:
    """
    Wall-clock time in nanoseconds since Unix epoch.

    Properties:
    - Globally comparable
    - Subject to NTP / clock jumps
    - REQUIRED for distributed tracing backends (Jaeger, OTel)
    """
    return time.time_ns()


def wall_time_iso() -> str:
    """
    Wall-clock timestamp formatted as ISO-8601 UTC with nanoseconds.
    """
    return format_ns(wall_time_ns())


# ---------------------------------------------------------------------------
# Monotonic clock (INTERNAL ONLY)
# ---------------------------------------------------------------------------


def mono_time_ns() -> int:
    """
    Monotonic time in nanoseconds.

    Properties:
    - Never goes backward
    - Process-local
    - SAFE for duration measurement
    - MUST NOT be exported
    """
    return time.monotonic_ns()


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_ns(ts_ns: int) -> str:
    """
    Format a wall-clock nanosecond timestamp as ISO-8601 UTC.

    Output:
        YYYY-MM-DD HH:MM:SS.nnnnnnnnnZ
    """
    seconds, nanoseconds = divmod(ts_ns, 1_000_000_000)
    microseconds = nanoseconds // 1_000

    dt = datetime.fromtimestamp(seconds, tz=timezone.utc).replace(microsecond=microseconds)

    return f"{dt.strftime('%Y-%m-%d %H:%M:%S')}.{nanoseconds:09d}Z"
