import traceback
from typing import Any


def serialize_error(exc: Exception | None) -> dict[str, Any] | None:
    if exc is None:
        return None

    return {
        "type": exc.__class__.__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }
