"""Release detection utilities.

Automatically detects the release/version from environment variables or git.
"""

from __future__ import annotations

import os
import subprocess

# Environment variables to check for release, in priority order
CI_ENV_VARS = [
    "PROLIFERATE_RELEASE",
    "GITHUB_SHA",
    "VERCEL_GIT_COMMIT_SHA",
    "RAILWAY_GIT_COMMIT_SHA",
    "RENDER_GIT_COMMIT",
    "HEROKU_SLUG_COMMIT",
    "CI_COMMIT_SHA",
    "BITBUCKET_COMMIT",
    "CIRCLE_SHA1",
]


def detect_release(explicit: str | None = None) -> str | None:
    """
    Detect the release/version identifier.

    Priority order:
    1. Explicit value passed to init()
    2. PROLIFERATE_RELEASE env var
    3. CI provider env vars (GITHUB_SHA, etc.)
    4. Git SHA at runtime

    Args:
        explicit: Explicitly provided release string.

    Returns:
        Release identifier (max 12 chars for git SHAs) or None.
    """
    # 1. Explicit takes priority
    if explicit:
        return explicit

    # 2. Check CI env vars in order
    for var in CI_ENV_VARS:
        if value := os.environ.get(var):
            # Truncate long SHAs to 12 chars
            return value[:12] if len(value) > 12 else value

    # 3. Try git at runtime
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=os.getcwd(),
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except Exception:
        pass

    return None
