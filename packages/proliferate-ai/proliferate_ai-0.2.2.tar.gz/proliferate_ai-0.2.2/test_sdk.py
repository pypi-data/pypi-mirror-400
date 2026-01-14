#!/usr/bin/env python3
"""Test script for the Proliferate Python SDK.

Run this to verify the SDK works correctly.
"""

import sys
import traceback

# Add src to path for local testing
sys.path.insert(0, "src")


def test_imports():
    """Test that all imports work."""
    print("=" * 60)
    print("TEST: Imports")
    print("=" * 60)

    try:
        import proliferate
        from proliferate import (
            init,
            capture_exception,
            set_user,
            set_tag,
            set_extra,
            push_scope,
            configure_scope,
            flush,
            close,
            ProliferateMiddleware,
        )
        from proliferate.core.hub import Hub
        from proliferate.core.scope import Scope
        from proliferate.core.client import Client
        from proliferate.core.options import Options
        from proliferate.transport.http import HttpTransport
        from proliferate.utils.release import detect_release

        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_release_detection():
    """Test release detection."""
    print("\n" + "=" * 60)
    print("TEST: Release Detection")
    print("=" * 60)

    from proliferate.utils.release import detect_release

    # Test explicit
    result = detect_release("v1.2.3")
    assert result == "v1.2.3", f"Expected 'v1.2.3', got '{result}'"
    print("✓ Explicit release works")

    # Test truncation
    long_sha = "abcdef1234567890abcdef1234567890"
    result = detect_release(long_sha)
    assert result == long_sha, f"Explicit should not truncate, got '{result}'"
    print("✓ Explicit release not truncated")

    # Test None fallback to git
    result = detect_release(None)
    print(f"  Git detection result: {result}")
    print("✓ Git fallback works (or returns None if not in git repo)")

    return True


def test_scope():
    """Test Scope functionality."""
    print("\n" + "=" * 60)
    print("TEST: Scope")
    print("=" * 60)

    from proliferate.core.scope import Scope, User

    scope = Scope()

    # Test initial state
    assert scope.user is None
    assert scope.tags == {}
    assert scope.extra == {}
    assert scope.propagation_context.trace_id is not None
    print("✓ Initial state correct")

    # Test set_user
    scope.set_user(id="123", email="test@example.com")
    assert scope.user.id == "123"
    assert scope.user.email == "test@example.com"
    print("✓ set_user works")

    # Test set_tag
    scope.set_tag("env", "test")
    assert scope.tags["env"] == "test"
    print("✓ set_tag works")

    # Test set_extra
    scope.set_extra("order_id", "abc123")
    assert scope.extra["order_id"] == "abc123"
    print("✓ set_extra works")

    # Test fork
    child = scope.fork()
    assert child.user.id == "123"
    assert child.tags["env"] == "test"
    child.set_tag("child_only", "yes")
    assert "child_only" not in scope.tags
    print("✓ fork creates independent copy")

    return True


def test_hub():
    """Test Hub functionality."""
    print("\n" + "=" * 60)
    print("TEST: Hub")
    print("=" * 60)

    from proliferate.core.hub import Hub

    hub = Hub.current()
    assert hub is not None
    print("✓ Hub.current() works")

    # Test scope access
    scope = hub.scope
    assert scope is not None
    print("✓ hub.scope works")

    # Test push_scope
    hub.scope.set_tag("outer", "yes")
    with hub.push_scope() as inner_scope:
        inner_scope.set_tag("inner", "yes")
        assert "outer" in hub.scope.tags
        assert "inner" in hub.scope.tags

    # After exiting, inner tag should be gone
    assert "outer" in hub.scope.tags
    assert "inner" not in hub.scope.tags
    print("✓ push_scope isolates changes")

    return True


def test_transport():
    """Test HttpTransport."""
    print("\n" + "=" * 60)
    print("TEST: HttpTransport")
    print("=" * 60)

    from proliferate.transport.http import HttpTransport

    # Create transport (won't actually send since endpoint doesn't exist)
    transport = HttpTransport(
        endpoint="http://localhost:9999/test",
        api_key="test_key",
    )

    # Test that send doesn't block
    import time
    start = time.time()
    transport.send({"test": "payload"})
    elapsed = time.time() - start
    assert elapsed < 0.1, f"send() blocked for {elapsed}s"
    print("✓ send() is non-blocking")

    # Test flush
    transport.flush(timeout=0.5)
    print("✓ flush() works")

    # Test close
    transport.close()
    print("✓ close() works")

    return True


def test_excepthook():
    """Test exception hook installation."""
    print("\n" + "=" * 60)
    print("TEST: Exception Hook")
    print("=" * 60)

    import sys
    from proliferate.instrumentation.excepthook import (
        install_excepthook,
        uninstall_excepthook,
    )

    original_hook = sys.excepthook

    captured = []

    def capture_fn(exc, tb_str):
        captured.append((exc, tb_str))

    install_excepthook(capture_fn)
    assert sys.excepthook != original_hook
    print("✓ install_excepthook replaces sys.excepthook")

    uninstall_excepthook()
    assert sys.excepthook == original_hook
    print("✓ uninstall_excepthook restores original")

    return True


def test_client_payload_format():
    """Test that Client builds correct payload format."""
    print("\n" + "=" * 60)
    print("TEST: Client Payload Format")
    print("=" * 60)

    from proliferate.core.options import Options
    from proliferate.core.scope import Scope

    # We'll need to capture what gets sent
    sent_payloads = []

    # Mock the transport
    class MockTransport:
        def send(self, payload):
            sent_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    # Create client with mock transport
    from proliferate.core.client import Client

    options = Options(
        api_key="test_key",
        endpoint="http://localhost:8000",
        environment="test",
        auto_excepthook=False,  # Don't install hooks
    )

    client = Client(options)
    client._transport = MockTransport()

    # Create a scope with context
    scope = Scope()
    scope.set_user(id="user123", email="test@example.com")
    scope.set_tag("feature", "checkout")

    # Capture an exception
    try:
        raise ValueError("Test error message")
    except Exception as e:
        client.capture_exception(e, scope)

    assert len(sent_payloads) == 1
    payload = sent_payloads[0]

    # Verify required fields
    assert "event_id" in payload
    assert "timestamp" in payload
    assert payload["platform"] == "python"
    assert payload["environment"] == "test"
    assert "session_id" in payload
    assert payload["window_id"] is None
    assert "trace_id" in payload
    print("✓ Basic fields present")

    # Verify exception
    exc = payload["exception"]
    assert exc["type"] == "ValueError"
    assert exc["value"] == "Test error message"
    assert "Traceback" in exc["stacktrace"]
    assert exc["mechanism"]["handled"] is True
    print("✓ Exception formatted correctly")

    # Verify context
    ctx = payload["context"]
    assert ctx["user"]["id"] == "user123"
    assert ctx["user"]["email"] == "test@example.com"
    assert ctx["tags"]["feature"] == "checkout"
    print("✓ Context included correctly")

    print(f"\n  Sample payload keys: {list(payload.keys())}")
    print(f"  Exception type: {exc['type']}")
    print(f"  Stacktrace preview: {exc['stacktrace'][:100]}...")

    return True


def test_full_init_flow():
    """Test the full init and capture flow."""
    print("\n" + "=" * 60)
    print("TEST: Full Init Flow")
    print("=" * 60)

    import proliferate
    from proliferate.core.hub import Hub

    # Reset hub state
    from proliferate.core.hub import _current_hub
    _current_hub.set(None)

    # Init with auto_excepthook=False to avoid side effects
    proliferate.init(
        api_key="test_key",
        endpoint="http://localhost:8000",
        environment="test",
        auto_excepthook=False,
    )

    hub = Hub.current()
    assert hub.client is not None
    print("✓ init() binds client to hub")

    # Test set_user
    proliferate.set_user(id="123")
    assert hub.scope.user.id == "123"
    print("✓ set_user() works via public API")

    # Test set_tag
    proliferate.set_tag("test", "value")
    assert hub.scope.tags["test"] == "value"
    print("✓ set_tag() works via public API")

    # Test push_scope
    with proliferate.push_scope() as scope:
        scope.set_tag("inner", "yes")
        assert hub.scope.tags.get("inner") == "yes"
    assert "inner" not in hub.scope.tags
    print("✓ push_scope() works via public API")

    # Cleanup
    proliferate.close()
    print("✓ close() works")

    return True


def test_sampling():
    """Test that sampling works."""
    print("\n" + "=" * 60)
    print("TEST: Sampling")
    print("=" * 60)

    from proliferate.core.options import Options
    from proliferate.core.client import Client
    from proliferate.core.scope import Scope

    sent_payloads = []

    class MockTransport:
        def send(self, payload):
            sent_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    # Create client with 0% sample rate
    options = Options(
        api_key="test_key",
        sample_rate=0.0,
        auto_excepthook=False,
    )

    client = Client(options)
    client._transport = MockTransport()

    scope = Scope()

    # Try to capture many exceptions
    for _ in range(10):
        try:
            raise ValueError("Test")
        except Exception as e:
            client.capture_exception(e, scope)

    assert len(sent_payloads) == 0
    print("✓ 0% sample rate drops all events")

    # Create client with 100% sample rate
    sent_payloads.clear()
    options = Options(
        api_key="test_key",
        sample_rate=1.0,
        auto_excepthook=False,
    )

    client = Client(options)
    client._transport = MockTransport()

    for _ in range(5):
        try:
            raise ValueError("Test")
        except Exception as e:
            client.capture_exception(e, scope)

    assert len(sent_payloads) == 5
    print("✓ 100% sample rate captures all events")

    return True


def test_before_send_hook():
    """Test before_send hook."""
    print("\n" + "=" * 60)
    print("TEST: before_send Hook")
    print("=" * 60)

    from proliferate.core.options import Options
    from proliferate.core.client import Client
    from proliferate.core.scope import Scope

    sent_payloads = []

    class MockTransport:
        def send(self, payload):
            sent_payloads.append(payload)
        def flush(self, timeout=2.0):
            pass
        def close(self):
            pass

    # Test modification
    def modify_event(event):
        event["custom_field"] = "added"
        return event

    options = Options(
        api_key="test_key",
        before_send=modify_event,
        auto_excepthook=False,
    )

    client = Client(options)
    client._transport = MockTransport()

    scope = Scope()
    try:
        raise ValueError("Test")
    except Exception as e:
        client.capture_exception(e, scope)

    assert sent_payloads[0].get("custom_field") == "added"
    print("✓ before_send can modify events")

    # Test dropping
    sent_payloads.clear()

    def drop_event(event):
        return None  # Drop

    options = Options(
        api_key="test_key",
        before_send=drop_event,
        auto_excepthook=False,
    )

    client = Client(options)
    client._transport = MockTransport()

    try:
        raise ValueError("Test")
    except Exception as e:
        result = client.capture_exception(e, scope)

    assert len(sent_payloads) == 0
    assert result is None
    print("✓ before_send can drop events")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PROLIFERATE PYTHON SDK TEST SUITE")
    print("=" * 60)

    tests = [
        test_imports,
        test_release_detection,
        test_scope,
        test_hub,
        test_transport,
        test_excepthook,
        test_client_payload_format,
        test_full_init_flow,
        test_sampling,
        test_before_send_hook,
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
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
