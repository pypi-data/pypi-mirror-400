from collections import deque
from threading import Lock
from typing import Any


class RingBuffer:
    """Fixed-capacity, thread-safe FIFO ring buffer."""

    __slots__ = ("_buffer", "_lock")

    def __init__(self, capacity: int) -> None:
        self._buffer: deque[Any] = deque(maxlen=capacity)
        self._lock = Lock()

    def append(self, item: Any) -> None:
        with self._lock:
            self._buffer.append(item)

    def drain(self) -> list[Any]:
        with self._lock:
            if not self._buffer:
                return []

            items = list(self._buffer)
            self._buffer.clear()
            return items
