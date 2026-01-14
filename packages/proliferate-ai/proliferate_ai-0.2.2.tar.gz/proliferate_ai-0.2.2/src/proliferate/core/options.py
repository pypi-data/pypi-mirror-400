"""SDK configuration options."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from proliferate.integrations.base import Integration


@dataclass
class Options:
    """SDK configuration options."""

    api_key: str
    endpoint: str = "https://api.proliferate.dev"
    release: str | None = None
    environment: str = "production"
    sample_rate: float = 1.0
    before_send: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None
    integrations: list[Integration] = field(default_factory=list)
    auto_excepthook: bool = True
