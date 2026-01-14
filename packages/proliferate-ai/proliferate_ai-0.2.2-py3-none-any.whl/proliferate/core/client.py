"""Client - captures events and sends them via transport."""

from __future__ import annotations

import random
import traceback
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from proliferate.core.options import Options
from proliferate.core.scope import Scope
from proliferate.transport.http import HttpTransport
from proliferate.utils.release import detect_release

if TYPE_CHECKING:
    pass


class Client:
    """Captures events and sends them via transport.

    The Client handles:
    - Building event payloads from exceptions
    - Sampling
    - before_send hook
    - Sending via transport
    """

    def __init__(self, options: Options) -> None:
        self.options = options
        self._transport = HttpTransport(
            endpoint=f"{options.endpoint}/v1/errors",
            api_key=options.api_key,
        )
        self._session_id = uuid.uuid4().hex
        self._release = detect_release(options.release)

        # Setup integrations
        for integration in options.integrations:
            integration.setup(self)

        # Auto-install excepthook
        if options.auto_excepthook:
            from proliferate.instrumentation.excepthook import install_excepthook

            install_excepthook(self._on_uncaught_exception)

    def _on_uncaught_exception(self, exc: BaseException, tb_str: str) -> None:
        """Called by excepthook for uncaught exceptions."""
        from proliferate.core.hub import Hub

        hub = Hub.current()
        self._capture_internal(exc, tb_str, hub.scope, handled=False)

    def capture_exception(self, exc: BaseException, scope: Scope) -> str | None:
        """Capture a handled exception."""
        tb_str = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        return self._capture_internal(exc, tb_str, scope, handled=True)

    def _capture_internal(
        self,
        exc: BaseException,
        tb_str: str,
        scope: Scope,
        handled: bool,
    ) -> str | None:
        """Internal method to capture an exception."""
        # Sampling
        if random.random() > self.options.sample_rate:
            return None

        event_id = uuid.uuid4().hex

        # Build payload matching backend's IngestErrorRequest
        payload: dict[str, Any] = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": "python",
            "release": self._release,
            "environment": self.options.environment,
            "session_id": self._session_id,
            "window_id": None,  # Python doesn't have windows
            "trace_id": scope.propagation_context.trace_id,
            "exception": {
                "type": type(exc).__name__,
                "value": str(exc),
                "stacktrace": tb_str,
                "mechanism": {"handled": handled},
            },
        }

        # Add context if we have user/tags
        if scope.user or scope.tags:
            context: dict[str, Any] = {}
            if scope.user:
                context["user"] = {
                    "id": scope.user.id,
                    "email": scope.user.email,
                    "username": scope.user.username,
                    "ip_address": scope.user.ip_address,
                }
            if scope.tags:
                context["tags"] = scope.tags
            payload["context"] = context

        # before_send hook
        if self.options.before_send:
            result = self.options.before_send(payload)
            if result is None:
                return None
            payload = result

        # Send
        self._transport.send(payload)
        return event_id

    def flush(self, timeout: float = 2.0) -> None:
        """Flush pending events."""
        self._transport.flush(timeout)

    def close(self) -> None:
        """Shutdown the SDK."""
        from proliferate.instrumentation.excepthook import uninstall_excepthook

        uninstall_excepthook()
        self._transport.close()
