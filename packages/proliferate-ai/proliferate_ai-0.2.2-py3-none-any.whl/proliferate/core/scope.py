"""Scope - context container for events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class User:
    """User context attached to events."""

    id: str | None = None
    email: str | None = None
    username: str | None = None
    ip_address: str | None = None


@dataclass
class PropagationContext:
    """Context for distributed tracing."""

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str | None = None


class Scope:
    """Holds contextual data for events.

    Scopes can be nested using Hub.push_scope() to create isolated contexts.
    Child scopes inherit from their parent but modifications don't affect the parent.
    """

    def __init__(self) -> None:
        self.user: User | None = None
        self.tags: dict[str, str] = {}
        self.extra: dict[str, Any] = {}
        self.propagation_context = PropagationContext()
        # Future: self.breadcrumbs, self.span

    def fork(self) -> Scope:
        """Create a child scope inheriting from this one."""
        child = Scope()
        child.user = self.user
        child.tags = self.tags.copy()
        child.extra = self.extra.copy()
        child.propagation_context = self.propagation_context
        return child

    def set_user(
        self,
        id: str | None = None,
        email: str | None = None,
        username: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Set user context on this scope."""
        self.user = User(id=id, email=email, username=username, ip_address=ip_address)

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag on this scope."""
        self.tags[key] = value

    def set_extra(self, key: str, value: Any) -> None:
        """Set extra data on this scope."""
        self.extra[key] = value
