"""Integration tests for the __main__ module."""

import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


def run_as_main(args: list[str]) -> int:
    """Run as __main__ module with patched sys.argv and return exit code."""
    with patch("sys.argv", ["prog"] + args):
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("contains_snippet", run_name="__main__")
        return int(exc_info.value.code or 0)


@pytest.mark.integration
def test_main_module_invokes_cli(tmp_path: Path) -> None:
    """Running python -m contains_snippet calls the main function."""
    (tmp_path / "content.txt").write_text("hello")
    (tmp_path / "check.md").write_text("hello")
    snippet = str(tmp_path / "content.txt")
    assert run_as_main(["--snippet-file", snippet, str(tmp_path / "check.md")]) == 0
