"""Proliferate Python SDK for error tracking.

Basic usage:
    import proliferate

    proliferate.init(api_key="pk_...")

    # Exceptions are automatically captured via sys.excepthook

    # Or capture manually:
    try:
        risky_operation()
    except Exception as e:
        proliferate.capture_exception(e)

With context:
    proliferate.set_user(id="123", email="user@example.com")
    proliferate.set_tag("feature", "checkout")

FastAPI integration:
    from fastapi import FastAPI
    import proliferate

    proliferate.init(api_key="pk_...")

    app = FastAPI()
    app.add_middleware(proliferate.ProliferateMiddleware)
"""

from typing import TYPE_CHECKING

from proliferate.api import (
    capture_exception,
    close,
    configure_scope,
    flush,
    init,
    push_scope,
    set_extra,
    set_tag,
    set_user,
)

if TYPE_CHECKING:
    from proliferate.integrations.fastapi import ProliferateMiddleware

__all__ = [
    "init",
    "capture_exception",
    "set_user",
    "set_tag",
    "set_extra",
    "push_scope",
    "configure_scope",
    "flush",
    "close",
    "ProliferateMiddleware",
]

__version__ = "0.2.2"


def __getattr__(name: str):
    """Lazy import for optional dependencies."""
    if name == "ProliferateMiddleware":
        try:
            from proliferate.integrations.fastapi import ProliferateMiddleware

            return ProliferateMiddleware
        except ImportError as e:
            raise ImportError(
                "ProliferateMiddleware requires starlette. "
                "Install with: pip install proliferate-ai[fastapi]"
            ) from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
