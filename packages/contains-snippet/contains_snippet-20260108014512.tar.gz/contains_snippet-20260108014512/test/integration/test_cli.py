"""Integration tests for the CLI module."""

from pathlib import Path

import pytest

from ..conftest import run_main_with_args


@pytest.mark.integration
class TestMainFunction:
    """Tests for the main() function."""

    def test_snippet_found_exits_0(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("hello world")
        code = run_main_with_args(
            ["--snippet-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        )
        assert code == 0

    def test_snippet_missing_exits_1(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found."""
        (tmp_path / "s.txt").write_text("missing")
        (tmp_path / "t.md").write_text("hello world")
        code = run_main_with_args(
            ["--snippet-file", str(tmp_path / "s.txt"), str(tmp_path / "t.md")]
        )
        assert code == 1

    def test_missing_content_file_arg_exits_2(self) -> None:
        """Exit 2 when --snippet-file is missing."""
        assert run_main_with_args(["somefile.md"]) == 2

    def test_missing_target_files_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when no target files provided."""
        (tmp_path / "s.txt").write_text("hello")
        assert run_main_with_args(["--snippet-file", str(tmp_path / "s.txt")]) == 2

    def test_unreadable_content_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when content file cannot be read."""
        (tmp_path / "t.md").write_text("content")
        code = run_main_with_args(
            ["--snippet-file", "/nonexistent/file.txt", str(tmp_path / "t.md")]
        )
        assert code == 2

    def test_unreadable_target_file_exits_2(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        (tmp_path / "s.txt").write_text("hello")
        code = run_main_with_args(
            ["--snippet-file", str(tmp_path / "s.txt"), "/nonexistent/file.md"]
        )
        assert code == 2

    def test_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.md").write_text("# hello")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--comment-prefix", "#",
            str(tmp_path / "t.md"),
        ])
        assert code == 0

    def test_infer_comment_prefix_flag(self, tmp_path: Path) -> None:
        """--infer-comment-prefix uses extension-based matching."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.py").write_text("# hello")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 0

    def test_comment_prefix_map_flag(self, tmp_path: Path) -> None:
        """--comment-prefix-map overrides extension mapping."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.js").write_text("// hello")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//",
            str(tmp_path / "t.js"),
        ])
        assert code == 0

    def test_multiple_files_all_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files match."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("hello world")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            str(tmp_path / "f1.md"),
            str(tmp_path / "f2.md"),
        ])
        assert code == 0

    def test_multiple_files_one_missing(self, tmp_path: Path) -> None:
        """Exit 1 when one file is missing the snippet."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "f1.md").write_text("hello")
        (tmp_path / "f2.md").write_text("goodbye")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            str(tmp_path / "f1.md"),
            str(tmp_path / "f2.md"),
        ])
        assert code == 1

    def test_help_exits_0(self) -> None:
        """--help exits with code 0."""
        assert run_main_with_args(["--help"]) == 0

    def test_empty_snippet_matches(self, tmp_path: Path) -> None:
        """Empty snippet matches any file."""
        (tmp_path / "s.txt").write_text("")
        (tmp_path / "t.py").write_text("# some content")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 0

    def test_empty_file_no_match(self, tmp_path: Path) -> None:
        """Non-empty snippet doesn't match empty file."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.py").write_text("")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 1

    def test_snippet_empty_line_matches_comment_only(self, tmp_path: Path) -> None:
        """Empty snippet line matches comment prefix only line."""
        (tmp_path / "s.txt").write_text("line1\n\nline2")
        (tmp_path / "t.py").write_text("# line1\n#\n# line2")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 0

    def test_snippet_extends_past_eof(self, tmp_path: Path) -> None:
        """Snippet that would extend past EOF doesn't match."""
        (tmp_path / "s.txt").write_text("line1\nline2\nline3")
        (tmp_path / "t.py").write_text("# line1\n# line2")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 1

    def test_partial_match_fails(self, tmp_path: Path) -> None:
        """First line matches but subsequent lines don't."""
        (tmp_path / "s.txt").write_text("line1\nline2")
        (tmp_path / "t.py").write_text("# line1\n# different")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 1

    def test_no_commented_match_returns_false(self, tmp_path: Path) -> None:
        """No match anywhere in file returns false."""
        (tmp_path / "s.txt").write_text("needle")
        (tmp_path / "t.py").write_text("# haystack\n# more hay")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            str(tmp_path / "t.py"),
        ])
        assert code == 1

    def test_prefix_map_unknown_ext_raw_match(self, tmp_path: Path) -> None:
        """Unknown extension with prefix_map falls back to raw match."""
        (tmp_path / "s.txt").write_text("hello")
        (tmp_path / "t.xyz").write_text("hello world")
        code = run_main_with_args([
            "--snippet-file", str(tmp_path / "s.txt"),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//",
            str(tmp_path / "t.xyz"),
        ])
        assert code == 0
