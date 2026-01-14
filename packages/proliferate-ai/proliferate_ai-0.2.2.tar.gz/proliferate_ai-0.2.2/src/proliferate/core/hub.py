"""Hub - thread/async-local context management."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING, Callable

from proliferate.core.scope import Scope

if TYPE_CHECKING:
    from proliferate.core.client import Client

_current_hub: ContextVar[Hub | None] = ContextVar("proliferate_hub", default=None)

# Global reference to the main client, shared across all hubs
_main_client: Client | None = None


class Hub:
    """Thread/async-local hub managing scope stack and client.

    The Hub is the central point for capturing events. Each thread/async context
    gets its own Hub via contextvars, ensuring thread safety.

    The Hub maintains a stack of Scopes, allowing nested contexts via push_scope().

    The client is shared globally across all hubs (set during init).
    """

    def __init__(self, client: Client | None = None) -> None:
        self._client = client
        self._scope_stack: list[Scope] = [Scope()]  # Always has root scope

    @classmethod
    def current(cls) -> Hub:
        """Get the current Hub for this context, creating one if needed."""
        hub = _current_hub.get()
        if hub is None:
            # New hubs inherit the main client
            hub = cls(client=_main_client)
            _current_hub.set(hub)
        return hub

    @classmethod
    def main(cls) -> Hub:
        """Get the main Hub (used during init)."""
        return cls.current()

    def bind_client(self, client: Client) -> None:
        """Bind a client to this Hub and set as the global main client."""
        global _main_client
        self._client = client
        _main_client = client

    @property
    def client(self) -> Client | None:
        """Get the client bound to this Hub."""
        return self._client

    @property
    def scope(self) -> Scope:
        """Get the current scope (top of stack)."""
        return self._scope_stack[-1]

    @contextmanager
    def push_scope(self) -> Iterator[Scope]:
        """Push a new scope onto the stack, inheriting from the current scope.

        Usage:
            with hub.push_scope() as scope:
                scope.set_tag("operation", "batch_import")
                # Errors here include the tag
        """
        new_scope = self.scope.fork()
        self._scope_stack.append(new_scope)
        try:
            yield new_scope
        finally:
            self._scope_stack.pop()

    def configure_scope(self, callback: Callable[[Scope], None]) -> None:
        """Configure the current scope via a callback."""
        callback(self.scope)

    def capture_exception(self, exc: BaseException) -> str | None:
        """Capture an exception with the current scope context.

        Returns:
            Event ID if captured, None if not captured (no client or sampled out).
        """
        if self._client is None:
            return None
        return self._client.capture_exception(exc, self.scope)
