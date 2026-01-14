"""HTTP transport using a background thread."""

from __future__ import annotations

import contextlib
import queue
import threading
from typing import Any

import httpx


class HttpTransport:
    """Background thread HTTP transport.

    Events are queued and sent asynchronously by a daemon thread.
    This ensures that sending events never blocks the main application.
    """

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=100)
        self._shutdown = threading.Event()
        self._worker = threading.Thread(
            target=self._run,
            daemon=True,
            name="proliferate-transport",
        )
        self._worker.start()

    def send(self, payload: dict[str, Any]) -> None:
        """Queue an event for sending (non-blocking).

        If the queue is full, the event is dropped silently.
        """
        with contextlib.suppress(queue.Full):
            self._queue.put_nowait(payload)

    def _run(self) -> None:
        """Worker thread that sends queued events."""
        with httpx.Client(timeout=5.0) as client:
            while not self._shutdown.is_set():
                try:
                    payload = self._queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                with contextlib.suppress(Exception):
                    client.post(
                        self._endpoint,
                        json=payload,
                        headers={"X-API-Key": self._api_key},
                    )

    def flush(self, timeout: float = 2.0) -> None:
        """Wait for the queue to drain, up to timeout seconds."""
        deadline = threading.Event()

        def wait_empty() -> None:
            while not self._queue.empty():
                threading.Event().wait(0.05)
            deadline.set()

        t = threading.Thread(target=wait_empty, daemon=True)
        t.start()
        deadline.wait(timeout)

    def close(self) -> None:
        """Shutdown the transport."""
        self.flush()
        self._shutdown.set()
        self._worker.join(timeout=2.0)
