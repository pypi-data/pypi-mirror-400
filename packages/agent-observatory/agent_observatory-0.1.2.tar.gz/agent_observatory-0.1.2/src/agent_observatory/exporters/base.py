from typing import Any


class Exporter:
    """
    Exporter contract.

    DESIGN:
    - Exporters are synchronous.
    - Must fail open (never raise).
    - Must be safe to call from any thread / event loop.
    """

    def export(self, payload: dict[str, Any]) -> None:
        raise NotImplementedError
