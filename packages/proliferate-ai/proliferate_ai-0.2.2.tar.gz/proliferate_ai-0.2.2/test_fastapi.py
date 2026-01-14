#!/usr/bin/env python3
"""Test FastAPI integration for the Proliferate Python SDK."""

import sys
sys.path.insert(0, "src")

import asyncio
from unittest.mock import MagicMock, patch


def test_fastapi_middleware():
    """Test that FastAPI middleware works correctly."""
    print("=" * 60)
    print("TEST: FastAPI Middleware")
    print("=" * 60)

    # Import after path setup
    from starlette.testclient import TestClient
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    import proliferate
    from proliferate import ProliferateMiddleware
    from proliferate.core.hub import Hub, _current_hub

    # Reset state
    _current_hub.set(None)

    # Track what gets captured
    captured_payloads = []

    class MockTransport:
        def send(self, payload):
            captured_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    # Initialize SDK
    proliferate.init(
        api_key="test_key",
        endpoint="http://localhost:8000",
        environment="test",
        auto_excepthook=False,
    )

    # Replace transport with mock
    Hub.current().client._transport = MockTransport()

    # Create test app
    async def homepage(request):
        return JSONResponse({"status": "ok"})

    async def error_endpoint(request):
        raise ValueError("Test error from endpoint")

    async def user_endpoint(request):
        # Set user context
        proliferate.set_user(id="user123", email="test@example.com")
        proliferate.set_tag("endpoint", "user")
        raise RuntimeError("User endpoint error")

    app = Starlette(
        routes=[
            Route("/", homepage),
            Route("/error", error_endpoint),
            Route("/user", user_endpoint),
        ],
    )
    app.add_middleware(ProliferateMiddleware)

    client = TestClient(app, raise_server_exceptions=False)

    # Test 1: Normal request (no error)
    print("\nTest 1: Normal request")
    response = client.get("/")
    assert response.status_code == 200
    assert len(captured_payloads) == 0
    print("✓ Normal requests don't capture errors")

    # Test 2: Error endpoint
    print("\nTest 2: Error endpoint")
    response = client.get("/error")
    assert response.status_code == 500
    assert len(captured_payloads) == 1

    payload = captured_payloads[0]
    assert payload["exception"]["type"] == "ValueError"
    assert payload["exception"]["value"] == "Test error from endpoint"
    assert payload["platform"] == "python"
    assert "trace_id" in payload
    print("✓ Errors are captured with correct exception info")

    # Check tags were set by middleware
    context = payload.get("context", {})
    tags = context.get("tags", {})
    assert tags.get("http.method") == "GET"
    assert tags.get("http.url") == "/error"
    print("✓ HTTP context tags are set")

    # Test 3: User context
    print("\nTest 3: User context in error")
    captured_payloads.clear()
    response = client.get("/user")
    assert response.status_code == 500
    assert len(captured_payloads) == 1

    payload = captured_payloads[0]
    context = payload.get("context", {})
    user = context.get("user", {})
    assert user.get("id") == "user123"
    assert user.get("email") == "test@example.com"
    tags = context.get("tags", {})
    assert tags.get("endpoint") == "user"
    print("✓ User context is included in errors")

    # Cleanup
    proliferate.close()

    print("\n" + "=" * 60)
    print("All FastAPI tests passed!")
    print("=" * 60)
    return True


def test_scope_isolation():
    """Test that scopes are properly isolated between requests."""
    print("\n" + "=" * 60)
    print("TEST: Scope Isolation")
    print("=" * 60)

    from starlette.testclient import TestClient
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    import proliferate
    from proliferate import ProliferateMiddleware
    from proliferate.core.hub import Hub, _current_hub

    # Reset state
    _current_hub.set(None)

    captured_payloads = []

    class MockTransport:
        def send(self, payload):
            captured_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    proliferate.init(
        api_key="test_key",
        endpoint="http://localhost:8000",
        auto_excepthook=False,
    )
    Hub.current().client._transport = MockTransport()

    # Set a tag at the global level
    proliferate.set_tag("global", "yes")

    async def request_a(request):
        proliferate.set_tag("request", "A")
        raise ValueError("Error A")

    async def request_b(request):
        proliferate.set_tag("request", "B")
        raise ValueError("Error B")

    app = Starlette(
        routes=[
            Route("/a", request_a),
            Route("/b", request_b),
        ],
    )
    app.add_middleware(ProliferateMiddleware)

    client = TestClient(app, raise_server_exceptions=False)

    # Make request A
    client.get("/a")
    # Make request B
    client.get("/b")

    assert len(captured_payloads) == 2

    # Each request should have its own tags (not polluted by the other)
    tags_a = captured_payloads[0].get("context", {}).get("tags", {})
    tags_b = captured_payloads[1].get("context", {}).get("tags", {})

    # Both should have http context
    assert tags_a.get("http.url") == "/a"
    assert tags_b.get("http.url") == "/b"

    # Each should have their own request tag
    assert tags_a.get("request") == "A"
    assert tags_b.get("request") == "B"

    print("✓ Request scopes are isolated")

    proliferate.close()
    return True


def test_trace_id_propagation():
    """Test that trace IDs are propagated from headers."""
    print("\n" + "=" * 60)
    print("TEST: Trace ID Propagation")
    print("=" * 60)

    from starlette.testclient import TestClient
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    import proliferate
    from proliferate import ProliferateMiddleware
    from proliferate.core.hub import Hub, _current_hub

    _current_hub.set(None)

    captured_payloads = []

    class MockTransport:
        def send(self, payload):
            captured_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    proliferate.init(
        api_key="test_key",
        endpoint="http://localhost:8000",
        auto_excepthook=False,
    )
    Hub.current().client._transport = MockTransport()

    async def error_endpoint(request):
        raise ValueError("Test error")

    app = Starlette(routes=[Route("/error", error_endpoint)])
    app.add_middleware(ProliferateMiddleware)

    client = TestClient(app, raise_server_exceptions=False)

    # Test with custom trace ID header
    custom_trace_id = "my-custom-trace-id-12345"
    client.get("/error", headers={"X-Trace-ID": custom_trace_id})

    assert len(captured_payloads) == 1
    assert captured_payloads[0]["trace_id"] == custom_trace_id
    print("✓ Trace ID is propagated from X-Trace-ID header")

    # Test without header (should generate one)
    captured_payloads.clear()
    client.get("/error")

    assert len(captured_payloads) == 1
    generated_trace_id = captured_payloads[0]["trace_id"]
    assert generated_trace_id is not None
    assert len(generated_trace_id) == 32  # UUID hex
    print("✓ Trace ID is generated when not provided")

    proliferate.close()
    return True


def main():
    """Run all FastAPI tests."""
    tests = [
        test_fastapi_middleware,
        test_scope_isolation,
        test_trace_id_propagation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED with exception:")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
