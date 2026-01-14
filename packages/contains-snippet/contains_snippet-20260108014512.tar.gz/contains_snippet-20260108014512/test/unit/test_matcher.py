"""Unit tests for the matcher module."""

from pathlib import Path

import pytest

from contains_snippet.cli import parse_prefix_map
from contains_snippet.matcher import check_file, commented_match, raw_match


@pytest.mark.unit
class TestRawMatch:
    """Tests for raw_match function."""

    def test_exact_match(self) -> None:
        """Exact string matches."""
        assert raw_match("hello", "hello")

    def test_substring_match(self) -> None:
        """Substring matches within content."""
        assert raw_match("world", "hello world!")

    def test_multiline_match(self) -> None:
        """Multiline snippet matches in content."""
        snippet = "line1\nline2"
        content = "prefix\nline1\nline2\nsuffix"
        assert raw_match(snippet, content)

    def test_no_match(self) -> None:
        """Non-matching snippet returns False."""
        assert not raw_match("xyz", "abc")

    def test_empty_snippet(self) -> None:
        """Empty snippet matches any content."""
        assert raw_match("", "any content")

    def test_empty_content(self) -> None:
        """Non-empty snippet doesn't match empty content."""
        assert not raw_match("something", "")


@pytest.mark.unit
class TestCommentedMatch:
    """Tests for commented_match function."""

    def test_single_line_with_space(self) -> None:
        """Single line with space after prefix."""
        assert commented_match("hello", "# hello")

    def test_single_line_without_space(self) -> None:
        """Single line without space after prefix."""
        assert commented_match("hello", "#hello")

    def test_multiline_with_space(self) -> None:
        """Multiline snippet with space after prefix."""
        snippet = "line1\nline2"
        content = "# line1\n# line2"
        assert commented_match(snippet, content)

    def test_multiline_without_space(self) -> None:
        """Multiline snippet without space after prefix."""
        snippet = "line1\nline2"
        content = "#line1\n#line2"
        assert commented_match(snippet, content)

    def test_multiline_mixed_space(self) -> None:
        """Multiline snippet with mixed spacing."""
        snippet = "line1\nline2"
        content = "# line1\n#line2"
        assert commented_match(snippet, content)

    def test_empty_line_matches_empty(self) -> None:
        """Empty snippet line matches empty file line."""
        snippet = "before\n\nafter"
        content = "# before\n\n# after"
        assert commented_match(snippet, content)

    def test_empty_line_matches_hash(self) -> None:
        """Empty snippet line matches lone hash."""
        snippet = "before\n\nafter"
        content = "# before\n#\n# after"
        assert commented_match(snippet, content)

    def test_empty_line_matches_hash_with_spaces(self) -> None:
        """Empty snippet line matches hash with trailing spaces."""
        snippet = "before\n\nafter"
        content = "# before\n#   \n# after"
        assert commented_match(snippet, content)

    def test_snippet_in_middle_of_file(self) -> None:
        """Snippet found in middle of file."""
        snippet = "target"
        content = "# other\n# target\n# more"
        assert commented_match(snippet, content)

    def test_no_match(self) -> None:
        """Non-matching snippet returns False."""
        assert not commented_match("hello", "# goodbye")

    def test_partial_match_not_contiguous(self) -> None:
        """Non-contiguous partial match returns False."""
        snippet = "line1\nline2"
        content = "# line1\n# other\n# line2"
        assert not commented_match(snippet, content)

    def test_empty_snippet(self) -> None:
        """Empty snippet matches any content."""
        assert commented_match("", "# anything")

    def test_empty_content(self) -> None:
        """Non-empty snippet doesn't match empty content."""
        assert not commented_match("hello", "")

    def test_first_line_matches_but_extends_past_eof(self) -> None:
        """First line matches but snippet extends past end of file."""
        snippet = "line1\nline2\nline3"
        content = "# other\n# line1"
        assert not commented_match(snippet, content)


@pytest.mark.unit
class TestCheckFile:
    """Tests for check_file function."""

    def test_md_file_raw_match(self, tmp_path: Path) -> None:
        """Markdown files use raw matching by default."""
        md_file = tmp_path / "test.md"
        md_file.write_text("some content here")
        assert check_file("content", md_file)

    def test_md_file_no_match(self, tmp_path: Path) -> None:
        """Markdown file without snippet returns False."""
        md_file = tmp_path / "test.md"
        md_file.write_text("some content here")
        assert not check_file("missing", md_file)

    def test_py_file_commented_match(self, tmp_path: Path) -> None:
        """Python files use commented matching by default."""
        py_file = tmp_path / "test.py"
        py_file.write_text("# snippet line")
        assert check_file("snippet line", py_file)

    def test_py_file_no_match(self, tmp_path: Path) -> None:
        """Python file with raw snippet returns False."""
        py_file = tmp_path / "test.py"
        py_file.write_text("snippet line")
        assert not check_file("snippet line", py_file)

    def test_yml_file_commented_match(self, tmp_path: Path) -> None:
        """YML files use commented matching by default."""
        yml_file = tmp_path / "test.yml"
        yml_file.write_text("# config line")
        assert check_file("config line", yml_file)

    def test_yaml_file_commented_match(self, tmp_path: Path) -> None:
        """YAML files use commented matching by default."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("#config line")
        assert check_file("config line", yaml_file)

    def test_unknown_extension_raw_match(self, tmp_path: Path) -> None:
        """Unknown extensions use raw matching by default."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("plain text content")
        assert check_file("text", txt_file)


@pytest.mark.unit
class TestCommentedMatchWithPrefix:
    """Tests for commented_match with custom prefix."""

    def test_custom_prefix_double_slash(self) -> None:
        """Double slash prefix works."""
        assert commented_match("hello", "// hello", prefix="//")

    def test_custom_prefix_semicolon(self) -> None:
        """Semicolon prefix works."""
        assert commented_match("hello", "; hello", prefix=";")

    def test_custom_prefix_no_space(self) -> None:
        """Custom prefix works without space."""
        assert commented_match("hello", "//hello", prefix="//")

    def test_custom_prefix_multiline(self) -> None:
        """Custom prefix works with multiline snippets."""
        snippet = "line1\nline2"
        content = "// line1\n// line2"
        assert commented_match(snippet, content, prefix="//")

    def test_custom_prefix_empty_line(self) -> None:
        """Custom prefix handles empty lines."""
        snippet = "before\n\nafter"
        content = "// before\n//\n// after"
        assert commented_match(snippet, content, prefix="//")


@pytest.mark.unit
class TestParsePrefixMap:
    """Tests for parse_prefix_map function."""

    def test_single_entry(self) -> None:
        """Single entry parsed correctly."""
        assert parse_prefix_map(".py=#") == {".py": "#"}

    def test_multiple_entries(self) -> None:
        """Multiple entries parsed correctly."""
        result = parse_prefix_map(".py=#,.js=//,.md=raw")
        assert result == {".py": "#", ".js": "//", ".md": None}

    def test_raw_value(self) -> None:
        """Raw value parsed as None."""
        assert parse_prefix_map(".txt=raw") == {".txt": None}

    def test_raw_case_insensitive(self) -> None:
        """RAW value is case insensitive."""
        assert parse_prefix_map(".txt=RAW") == {".txt": None}

    def test_extension_normalized_lowercase(self) -> None:
        """Extension is normalized to lowercase."""
        assert parse_prefix_map(".PY=#") == {".py": "#"}

    def test_whitespace_stripped(self) -> None:
        """Whitespace is stripped from entries."""
        assert parse_prefix_map(" .py = # ") == {".py": "#"}


@pytest.mark.unit
class TestCheckFileWithCommentPrefix:
    """Tests for check_file with comment_prefix parameter."""

    def test_forces_commented_on_md(self, tmp_path: Path) -> None:
        """comment_prefix forces commented matching on markdown."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# hello")
        assert check_file("hello", md_file, comment_prefix="#")

    def test_custom_prefix_on_any_file(self, tmp_path: Path) -> None:
        """comment_prefix works on any file type."""
        js_file = tmp_path / "test.js"
        js_file.write_text("// hello")
        assert check_file("hello", js_file, comment_prefix="//")


@pytest.mark.unit
class TestCheckFileWithPrefixMap:
    """Tests for check_file with prefix_map parameter."""

    def test_prefix_map_uses_mapped_prefix(self, tmp_path: Path) -> None:
        """prefix_map applies correct prefix for extension."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# hello")
        prefix_map: dict[str, str | None] = {".md": "#"}
        assert check_file("hello", md_file, prefix_map=prefix_map)

    def test_prefix_map_raw_value(self, tmp_path: Path) -> None:
        """prefix_map None value means raw matching."""
        py_file = tmp_path / "test.py"
        py_file.write_text("hello")
        prefix_map: dict[str, str | None] = {".py": None}
        assert check_file("hello", py_file, prefix_map=prefix_map)

    def test_prefix_map_unknown_ext_defaults_raw(self, tmp_path: Path) -> None:
        """Unknown extension defaults to raw matching."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")
        prefix_map: dict[str, str | None] = {".py": "#"}
        assert check_file("hello", txt_file, prefix_map=prefix_map)

    def test_prefix_map_unknown_ext_uses_raw(self, tmp_path: Path) -> None:
        """Unknown extension uses raw, not commented matching."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("# hello\n# world")
        prefix_map: dict[str, str | None] = {".py": "#"}
        assert not check_file("hello\nworld", txt_file, prefix_map=prefix_map)
