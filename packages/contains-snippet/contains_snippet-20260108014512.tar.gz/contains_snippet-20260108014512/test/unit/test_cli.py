"""Unit tests for the CLI module."""

from pathlib import Path

import pytest

from contains_snippet.cli import BUILTIN_PREFIX_MAP, parse_prefix_map

from ..conftest import run_main_with_args


@pytest.mark.unit
class TestParsePrefixMap:
    """Tests for parse_prefix_map function."""

    def test_single_entry(self) -> None:
        """Parse single extension mapping."""
        assert parse_prefix_map(".js=//") == {".js": "//"}

    def test_multiple_entries(self) -> None:
        """Parse multiple extension mappings."""
        assert parse_prefix_map(".js=//,.ts=//,.go=//") == {".js": "//", ".ts": "//", ".go": "//"}

    def test_raw_value(self) -> None:
        """'raw' value becomes None."""
        assert parse_prefix_map(".md=raw") == {".md": None}

    def test_raw_case_insensitive(self) -> None:
        """'RAW' value also becomes None."""
        assert parse_prefix_map(".md=RAW") == {".md": None}

    def test_extension_normalized(self) -> None:
        """Extension is normalized to lowercase."""
        assert parse_prefix_map(".JS=//") == {".js": "//"}

    def test_whitespace_stripped(self) -> None:
        """Whitespace around parts is stripped."""
        assert parse_prefix_map(" .js = // ") == {".js": "//"}


@pytest.mark.unit
class TestBuiltinPrefixMap:
    """Tests for BUILTIN_PREFIX_MAP constant."""

    def test_md_is_raw(self) -> None:
        """Markdown files use raw matching."""
        assert BUILTIN_PREFIX_MAP[".md"] is None

    def test_py_uses_hash(self) -> None:
        """Python files use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".py"] == "#"

    def test_yml_uses_hash(self) -> None:
        """YAML files use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".yml"] == "#"

    def test_yaml_uses_hash(self) -> None:
        """YAML files (alt ext) use hash comment prefix."""
        assert BUILTIN_PREFIX_MAP[".yaml"] == "#"


@pytest.mark.unit
class TestMain:
    """Tests for main() function."""

    def test_snippet_found_exits_0(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found in all files."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("hello world")
        args = ["--snippet-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        assert run_main_with_args(args) == 0

    def test_snippet_not_found_exits_1(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found."""
        (tmp_path / "s.txt").write_text("missing")
        (tmp_path / "t.md").write_text("hello world")
        args = ["--snippet-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        assert run_main_with_args(args) == 1

    def test_missing_snippet_file_arg_exits_2(self) -> None:
        """Exit 2 when --snippet-file argument is missing."""
        assert run_main_with_args(["target.md"]) == 2

    def test_unreadable_snippet_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when snippet file cannot be read."""
        (tmp_path / "t.md").write_text("content")
        assert run_main_with_args(["--snippet-file", "/nonexistent", str(tmp_path / "t.md")]) == 2

    def test_unreadable_target_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        (tmp_path / "s.txt").write_text("hello")
        assert run_main_with_args(["--snippet-file", str(tmp_path / "s.txt"), "/nonexistent"]) == 2

    def test_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("# hello")
        snippet = str(tmp_path / "s.txt")
        args = ["--snippet-file", snippet, "--comment-prefix", "#", str(tmp_path / "t.md")]
        assert run_main_with_args(args) == 0

    def test_infer_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--infer-comment-prefix uses extension mapping."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.py").write_text("# hello")
        snippet = str(tmp_path / "s.txt")
        args = ["--snippet-file", snippet, "--infer-comment-prefix", str(tmp_path / "t.py")]
        assert run_main_with_args(args) == 0

    def test_comment_prefix_map_flag(self, tmp_path: Path) -> None:
        """--comment-prefix-map with --infer-comment-prefix."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.js").write_text("// hello")
        args = [
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix", "--comment-prefix-map", ".js=//", str(tmp_path / "t.js")
        ]
        assert run_main_with_args(args) == 0

    def test_help_exits_0(self) -> None:
        """--help exits with code 0."""
        assert run_main_with_args(["--help"]) == 0

    def test_multiple_files_all_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files match."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("hello world")
        snippet = str(tmp_path / "s.txt")
        args = ["--snippet-file", snippet, str(tmp_path / "f1.md"), str(tmp_path / "f2.md")]
        assert run_main_with_args(args) == 0

    def test_multiple_files_one_missing(self, tmp_path: Path) -> None:
        """Exit 1 when one file is missing the snippet."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("goodbye")
        snippet = str(tmp_path / "s.txt")
        args = ["--snippet-file", snippet, str(tmp_path / "f1.md"), str(tmp_path / "f2.md")]
        assert run_main_with_args(args) == 1
