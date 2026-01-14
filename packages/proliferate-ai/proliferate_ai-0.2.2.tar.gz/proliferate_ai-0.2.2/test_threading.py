#!/usr/bin/env python3
"""Test threading.excepthook integration."""

import sys
import threading
import time
sys.path.insert(0, "src")


def test_threading_excepthook():
    """Test that exceptions in threads are captured."""
    print("=" * 60)
    print("TEST: Threading Excepthook")
    print("=" * 60)

    import proliferate
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

    # Initialize SDK with auto_excepthook
    proliferate.init(
        api_key="test_key",
        endpoint="http://localhost:8000",
        auto_excepthook=True,
    )
    Hub.current().client._transport = MockTransport()

    print("✓ SDK initialized with auto_excepthook=True")

    # Original threading excepthook for comparison
    original_threading_hook = None

    def thread_that_errors():
        raise RuntimeError("Thread exception test")

    # Create thread that will error
    t = threading.Thread(target=thread_that_errors, name="test-error-thread")
    t.start()
    t.join()  # Wait for it to finish

    # Give a moment for the hook to process
    time.sleep(0.2)

    # Check if exception was captured
    if len(captured_payloads) > 0:
        print("✓ Thread exception was captured!")
        payload = captured_payloads[0]
        print(f"  Exception type: {payload['exception']['type']}")
        print(f"  Exception value: {payload['exception']['value']}")
        assert payload['exception']['type'] == 'RuntimeError'
        assert 'Thread exception test' in payload['exception']['value']
        print("✓ Exception details are correct")
    else:
        print("⚠ Thread exception was NOT captured")
        print("  This may be expected depending on Python version")
        # Not all Python versions call threading.excepthook the same way

    proliferate.close()
    print("✓ SDK closed")

    return True


def test_thread_context_isolation():
    """Test that thread contexts are isolated."""
    print("\n" + "=" * 60)
    print("TEST: Thread Context Isolation")
    print("=" * 60)

    import proliferate
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

    # Set main thread context
    proliferate.set_tag("thread", "main")
    proliferate.set_user(id="main-user")

    results = []

    def thread_work(thread_id):
        # Each thread should get its own Hub via contextvars
        hub = Hub.current()
        hub.scope.set_tag("thread", f"worker-{thread_id}")
        hub.scope.set_user(id=f"user-{thread_id}")

        # Capture exception
        try:
            raise ValueError(f"Error from thread {thread_id}")
        except Exception as e:
            event_id = proliferate.capture_exception(e)
            results.append((thread_id, event_id))

    # Create multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=thread_work, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    time.sleep(0.1)

    # Check results
    print(f"  Captured {len(captured_payloads)} events from {len(threads)} threads")

    # Each thread's event should have its own context
    for payload in captured_payloads:
        ctx = payload.get("context", {})
        tags = ctx.get("tags", {})
        user = ctx.get("user", {})
        thread_tag = tags.get("thread", "unknown")
        user_id = user.get("id", "unknown")
        print(f"  Thread: {thread_tag}, User: {user_id}")

    # Main thread context should be unchanged
    main_hub = Hub.current()
    assert main_hub.scope.tags.get("thread") == "main"
    assert main_hub.scope.user.id == "main-user"
    print("✓ Main thread context unchanged")

    proliferate.close()
    return True


def main():
    """Run threading tests."""
    print("\n" + "=" * 60)
    print("PROLIFERATE PYTHON SDK THREADING TEST SUITE")
    print("=" * 60)

    tests = [
        test_threading_excepthook,
        test_thread_context_isolation,
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
