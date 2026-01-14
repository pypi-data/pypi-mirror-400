"""Shared test utilities."""

import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the contains-snippet CLI with the given arguments."""
    return subprocess.run(
        [sys.executable, "-m", "contains_snippet", *args],
        capture_output=True,
        text=True,
        check=False,
    )
