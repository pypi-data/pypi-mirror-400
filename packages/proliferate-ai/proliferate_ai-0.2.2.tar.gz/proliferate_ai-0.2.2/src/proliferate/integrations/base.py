"""Base integration protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from proliferate.core.client import Client


class Integration(Protocol):
    """Protocol for framework integrations.

    Integrations are set up once during SDK initialization and can patch
    libraries, add middleware, or configure the client.
    """

    identifier: str

    def setup(self, client: Client) -> None:
        """Set up the integration.

        Called during SDK initialization. Can patch libraries,
        register hooks, or configure the client.
        """
        ...
