from typing import Any

from ..internal.terminal import render_session_envelope
from .base import Exporter


class ConsoleExporter(Exporter):
    """
    Exporter that pretty-prints session envelopes directly to the terminal.
    Ideal for development and immediate feedback.
    """

    def export(self, payload: dict[str, Any]) -> None:
        render_session_envelope(payload)
