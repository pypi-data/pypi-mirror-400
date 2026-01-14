"""Transport protocol definition."""

from __future__ import annotations

from typing import Any, Protocol


class Transport(Protocol):
    """Protocol for event transport implementations."""

    def send(self, payload: dict[str, Any]) -> None:
        """Send an event payload (non-blocking)."""
        ...

    def flush(self, timeout: float = 2.0) -> None:
        """Flush pending events, waiting up to timeout seconds."""
        ...

    def close(self) -> None:
        """Shutdown the transport."""
        ...
