"""Unit tests for the __main__ module."""

import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


def run_module_main(args: list[str]) -> int:
    """Run module as __main__ with patched sys.argv and return exit code."""
    with patch("sys.argv", ["prog"] + args):
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("contains_snippet", run_name="__main__")
        return int(exc_info.value.code or 0)


@pytest.mark.unit
def test_main_module_calls_main(tmp_path: Path) -> None:
    """Running as __main__ calls the main function."""
    (tmp_path / "snippet.txt").write_text("content")
    (tmp_path / "target.md").write_text("content")
    snippet = str(tmp_path / "snippet.txt")
    assert run_module_main(["--snippet-file", snippet, str(tmp_path / "target.md")]) == 0
