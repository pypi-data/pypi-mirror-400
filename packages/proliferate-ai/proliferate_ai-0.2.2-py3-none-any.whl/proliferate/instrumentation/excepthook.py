"""Exception hook instrumentation.

Patches sys.excepthook and threading.excepthook to automatically capture
uncaught exceptions.
"""

from __future__ import annotations

import sys
import threading
import traceback
from collections.abc import Callable
from types import TracebackType
from typing import Optional

# Type for sys.excepthook - using Optional for 3.9 compatibility
ExceptHookFn = Callable[
    [type[BaseException], BaseException, Optional[TracebackType]], None
]
_original_excepthook: Optional[ExceptHookFn] = None
_original_threading_excepthook: Optional[Callable[[threading.ExceptHookArgs], None]] = None
_capture_fn: Optional[Callable[[BaseException, str], None]] = None
_capturing = False  # Re-entrancy guard


def install_excepthook(capture_fn: Callable[[BaseException, str], None]) -> None:
    """Install exception hooks to capture uncaught exceptions.

    Args:
        capture_fn: Function to call with (exception, traceback_string).
    """
    global _original_excepthook, _original_threading_excepthook, _capture_fn

    _capture_fn = capture_fn
    _original_excepthook = sys.excepthook
    _original_threading_excepthook = threading.excepthook

    sys.excepthook = _excepthook
    threading.excepthook = _threading_excepthook


def _excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_tb: TracebackType | None,
) -> None:
    """Custom excepthook that captures exceptions before calling the original."""
    global _capturing

    if not _capturing and _capture_fn:
        _capturing = True
        try:
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            _capture_fn(exc_value, tb_str)
        finally:
            _capturing = False

    if _original_excepthook:
        _original_excepthook(exc_type, exc_value, exc_tb)


def _threading_excepthook(args: threading.ExceptHookArgs) -> None:
    """Custom threading excepthook that captures exceptions from threads."""
    global _capturing

    if not _capturing and _capture_fn and args.exc_value is not None:
        _capturing = True
        try:
            tb_str = "".join(
                traceback.format_exception(
                    args.exc_type, args.exc_value, args.exc_traceback
                )
            )
            _capture_fn(args.exc_value, tb_str)
        finally:
            _capturing = False

    if _original_threading_excepthook:
        _original_threading_excepthook(args)


def uninstall_excepthook() -> None:
    """Restore the original exception hooks."""
    global _original_excepthook, _original_threading_excepthook

    if _original_excepthook:
        sys.excepthook = _original_excepthook
    if _original_threading_excepthook:
        threading.excepthook = _original_threading_excepthook
