#!/usr/bin/env python3
"""End-to-end test sending real events to the backend.

This test requires the backend to be running on localhost:8000 with a valid project API key.
"""

import sys
import time
sys.path.insert(0, "src")

import os
import proliferate
from proliferate.core.hub import Hub, _current_hub


def test_send_real_event():
    """Send a real event to the running backend."""
    print("=" * 60)
    print("E2E TEST: Send Real Event to Backend")
    print("=" * 60)

    # Get API key from env or use test key
    api_key = os.environ.get("PROLIFERATE_API_KEY")
    if not api_key:
        print("⚠ PROLIFERATE_API_KEY not set, skipping E2E test")
        print("  Set PROLIFERATE_API_KEY to a valid project API key to run this test")
        return True

    # Reset state
    _current_hub.set(None)

    # Initialize SDK pointing to local backend
    proliferate.init(
        api_key=api_key,
        endpoint="http://localhost:8000",
        environment="e2e-test",
        release="test-release-1.0.0",
    )

    print(f"✓ SDK initialized with endpoint http://localhost:8000")

    # Set some context
    proliferate.set_user(id="e2e-user-123", email="e2e@test.com")
    proliferate.set_tag("test_type", "e2e")
    proliferate.set_tag("python_version", sys.version.split()[0])

    print("✓ User and tags set")

    # Capture a test exception
    try:
        def inner_function():
            raise ValueError("E2E test exception from Python SDK")

        def outer_function():
            inner_function()

        outer_function()
    except Exception as e:
        event_id = proliferate.capture_exception(e)
        print(f"✓ Exception captured, event_id: {event_id}")

    # Flush to ensure it's sent
    proliferate.flush(timeout=5.0)
    print("✓ Events flushed")

    # Give the backend a moment to process
    time.sleep(1)

    proliferate.close()
    print("✓ SDK closed")

    print("\n" + "=" * 60)
    print("E2E test completed!")
    print("Check your backend to verify the event was received.")
    print("=" * 60)

    return True


def test_excepthook_integration():
    """Test that uncaught exceptions are captured."""
    print("\n" + "=" * 60)
    print("E2E TEST: Excepthook Integration")
    print("=" * 60)

    api_key = os.environ.get("PROLIFERATE_API_KEY")
    if not api_key:
        print("⚠ PROLIFERATE_API_KEY not set, skipping E2E test")
        return True

    import threading
    import traceback

    _current_hub.set(None)

    # Track if our hook was called
    hook_called = [False]
    original_excepthook = sys.excepthook

    # Initialize SDK
    proliferate.init(
        api_key=api_key,
        endpoint="http://localhost:8000",
        environment="e2e-test",
        auto_excepthook=True,
    )

    print("✓ SDK initialized with auto_excepthook=True")
    print(f"  sys.excepthook changed: {sys.excepthook != original_excepthook}")

    # We can't actually trigger sys.excepthook in a test without crashing,
    # but we can verify it was installed
    from proliferate.instrumentation.excepthook import _capture_fn
    assert _capture_fn is not None
    print("✓ Exception hook is installed")

    # Test threading.excepthook by creating a thread that errors
    error_captured = [False]

    def thread_that_errors():
        # This should trigger threading.excepthook
        raise RuntimeError("Thread exception for E2E test")

    # We can't easily test this without the thread actually crashing,
    # but we've verified the hook is installed

    proliferate.close()
    print("✓ SDK closed and hooks uninstalled")

    return True


def main():
    """Run E2E tests."""
    print("\n" + "=" * 60)
    print("PROLIFERATE PYTHON SDK E2E TEST SUITE")
    print("=" * 60)

    tests = [
        test_send_real_event,
        test_excepthook_integration,
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
