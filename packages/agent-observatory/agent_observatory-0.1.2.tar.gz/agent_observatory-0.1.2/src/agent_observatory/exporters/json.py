import json
from typing import Any

from .base import Exporter


class JSONExporter(Exporter):
    def export(self, payload: dict[str, Any]) -> None:
        print(json.dumps(payload, indent=2))
