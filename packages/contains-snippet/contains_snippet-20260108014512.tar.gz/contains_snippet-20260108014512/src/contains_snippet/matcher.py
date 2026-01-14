"""Snippet matching functions for raw and commented content."""

from pathlib import Path


def raw_match(snippet: str, file_content: str) -> bool:
    """Check if snippet exists as a substring in file content."""
    return snippet in file_content


def commented_match(snippet: str, file_content: str, prefix: str = "#") -> bool:
    """Check if snippet exists as commented lines in file content."""
    snippet_lines = snippet.splitlines()
    if not snippet_lines:
        return True

    file_lines = file_content.splitlines()
    if not file_lines:
        return False

    def line_matches(snippet_line: str, file_line: str) -> bool:
        if snippet_line == "":
            return file_line == "" or file_line.rstrip() == prefix
        return file_line in (f"{prefix} {snippet_line}", f"{prefix}{snippet_line}")

    for start_idx, file_line in enumerate(file_lines):
        if line_matches(snippet_lines[0], file_line):
            if start_idx + len(snippet_lines) > len(file_lines):
                continue
            all_match = True
            for offset, snippet_line in enumerate(snippet_lines):
                if not line_matches(snippet_line, file_lines[start_idx + offset]):
                    all_match = False
                    break
            if all_match:
                return True
    return False


def _get_match_result(
    snippet: str,
    file_content: str,
    mapped_prefix: str | None,
) -> bool:
    """Return match result based on mapped prefix value."""
    if mapped_prefix is None:
        return raw_match(snippet, file_content)
    return commented_match(snippet, file_content, prefix=mapped_prefix)


def check_file(
    snippet: str,
    file_path: Path,
    comment_prefix: str | None = None,
    prefix_map: dict[str, str | None] | None = None,
) -> bool:
    """Check if snippet exists in file using appropriate matching strategy."""
    file_content = file_path.read_text()
    suffix = file_path.suffix.lower()

    if comment_prefix is not None:
        return commented_match(snippet, file_content, prefix=comment_prefix)

    if prefix_map is not None:
        mapped = prefix_map.get(suffix)
        if suffix in prefix_map:
            return _get_match_result(snippet, file_content, mapped)
        return raw_match(snippet, file_content)

    default_map: dict[str, str | None] = {
        ".md": None,
        ".py": "#",
        ".yml": "#",
        ".yaml": "#",
    }
    return _get_match_result(snippet, file_content, default_map.get(suffix))
