import json
from typing import Any

from .base import Exporter


class FileExporter(Exporter):
    """
    Exporter that writes session envelopes to a file in JSONL format.
    One JSON object per line. Ideal for tailing with CLI tools.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def export(self, payload: dict[str, Any]) -> None:
        import os

        # Ensure directory exists
        if os.path.dirname(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "a", encoding="utf-8") as f:
            # We use separators=(",", ":") to keep it compact on one line
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
