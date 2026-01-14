"""Public API functions for the Proliferate SDK."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Callable

from proliferate.core.client import Client
from proliferate.core.hub import Hub
from proliferate.core.options import Options
from proliferate.core.scope import Scope
from proliferate.integrations.base import Integration


def init(
    api_key: str,
    endpoint: str = "https://api.proliferate.dev",
    release: str | None = None,
    environment: str = "production",
    sample_rate: float = 1.0,
    before_send: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
    integrations: list[Integration] | None = None,
    auto_excepthook: bool = True,
) -> None:
    """Initialize the Proliferate SDK.

    This must be called before any other SDK functions.

    Args:
        api_key: Your Proliferate API key.
        endpoint: API endpoint URL (default: https://api.proliferate.dev).
        release: Release/version identifier. Auto-detected if not provided.
        environment: Environment name (default: "production").
        sample_rate: Fraction of events to send (0.0 to 1.0, default: 1.0).
        before_send: Hook to modify or drop events before sending.
        integrations: List of integrations to enable.
        auto_excepthook: Whether to automatically capture uncaught exceptions.

    Example:
        import proliferate

        proliferate.init(
            api_key="pk_...",
            environment="production",
        )
    """
    options = Options(
        api_key=api_key,
        endpoint=endpoint,
        release=release,
        environment=environment,
        sample_rate=sample_rate,
        before_send=before_send,
        integrations=integrations or [],
        auto_excepthook=auto_excepthook,
    )
    client = Client(options)
    Hub.main().bind_client(client)


def capture_exception(exc: BaseException) -> str | None:
    """Manually capture an exception.

    Args:
        exc: The exception to capture.

    Returns:
        Event ID if captured, None if not captured.

    Example:
        try:
            risky_operation()
        except Exception as e:
            proliferate.capture_exception(e)
    """
    return Hub.current().capture_exception(exc)


def set_user(
    id: str | None = None,
    email: str | None = None,
    username: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Set user context on the current scope.

    Args:
        id: User ID.
        email: User email.
        username: Username.
        ip_address: User's IP address.

    Example:
        proliferate.set_user(id="123", email="user@example.com")
    """
    Hub.current().scope.set_user(
        id=id,
        email=email,
        username=username,
        ip_address=ip_address,
    )


def set_tag(key: str, value: str) -> None:
    """Set a tag on the current scope.

    Tags are indexed and searchable.

    Args:
        key: Tag name.
        value: Tag value.

    Example:
        proliferate.set_tag("feature", "checkout")
    """
    Hub.current().scope.set_tag(key, value)


def set_extra(key: str, value: Any) -> None:
    """Set extra data on the current scope.

    Extra data is not indexed but included in events.

    Args:
        key: Data key.
        value: Data value (must be JSON-serializable).

    Example:
        proliferate.set_extra("order_id", "abc123")
    """
    Hub.current().scope.set_extra(key, value)


@contextmanager
def push_scope() -> Iterator[Scope]:
    """Create an isolated scope context.

    Changes made to the scope inside the context manager do not
    affect the parent scope.

    Yields:
        The new scope.

    Example:
        with proliferate.push_scope() as scope:
            scope.set_tag("batch_id", "abc123")
            for item in items:
                process(item)  # Errors include batch_id
    """
    with Hub.current().push_scope() as scope:
        yield scope


def configure_scope(callback: Callable[[Scope], None]) -> None:
    """Configure the current scope via a callback.

    Args:
        callback: Function that receives the scope.

    Example:
        proliferate.configure_scope(lambda scope: scope.set_tag("key", "value"))
    """
    Hub.current().configure_scope(callback)


def flush(timeout: float = 2.0) -> None:
    """Flush pending events.

    Blocks until all queued events are sent or timeout is reached.

    Args:
        timeout: Maximum time to wait in seconds.
    """
    client = Hub.current().client
    if client:
        client.flush(timeout)


def close() -> None:
    """Shutdown the SDK.

    Flushes pending events and uninstalls hooks.
    Call this before your application exits.
    """
    client = Hub.current().client
    if client:
        client.close()
