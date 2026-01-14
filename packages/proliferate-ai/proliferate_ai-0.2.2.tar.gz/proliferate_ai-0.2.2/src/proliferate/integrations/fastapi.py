"""FastAPI/Starlette integration."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class ProliferateMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware for automatic error capture.

    This middleware:
    - Creates a new scope for each request
    - Sets request context (method, path) as tags
    - Propagates trace IDs from headers or generates new ones
    - Captures unhandled exceptions

    Usage:
        from fastapi import FastAPI
        import proliferate
        from proliferate import ProliferateMiddleware

        proliferate.init(api_key="pk_...")
        app = FastAPI()
        app.add_middleware(ProliferateMiddleware)
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Handle a request, capturing any exceptions."""
        from proliferate.core.hub import Hub

        hub = Hub.current()

        with hub.push_scope() as scope:
            # Propagate or generate trace ID
            trace_id = request.headers.get("X-Trace-ID") or uuid.uuid4().hex
            scope.propagation_context.trace_id = trace_id

            # Set request context as tags
            scope.set_tag("http.method", request.method)
            scope.set_tag("http.url", str(request.url.path))

            try:
                response = await call_next(request)
                return response
            except Exception as exc:
                hub.capture_exception(exc)
                raise
