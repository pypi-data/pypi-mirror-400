"""Command-line interface for contains-snippet."""

import argparse
import sys
from pathlib import Path

from .matcher import check_file

BUILTIN_PREFIX_MAP: dict[str, str | None] = {
    ".md": None,
    ".py": "#",
    ".yml": "#",
    ".yaml": "#",
}


def parse_prefix_map(map_str: str) -> dict[str, str | None]:
    """Parse extension-to-prefix mapping string like '.py=#,.js=//'."""
    result: dict[str, str | None] = {}
    for entry in map_str.split(","):
        ext, value = entry.split("=", 1)
        ext = ext.strip().lower()
        value = value.strip()
        result[ext] = None if value.lower() == "raw" else value
    return result


def main() -> None:
    """Run the contains-snippet CLI."""
    parser = argparse.ArgumentParser(
        description="Check if a snippet exists in files"
    )
    parser.add_argument(
        "--snippet-file",
        required=True,
        type=Path,
        help="Path to the file containing the snippet to search for",
    )
    parser.add_argument(
        "--comment-prefix",
        type=str,
        default=None,
        help="Force commented matching for all files with this prefix",
    )
    parser.add_argument(
        "--infer-comment-prefix",
        action="store_true",
        help="Infer comment prefix from file extension",
    )
    parser.add_argument(
        "--comment-prefix-map",
        type=str,
        default=None,
        help="Override extension mapping: '.py=#,.js=//,.md=raw'",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Files to check for the snippet",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        sys.exit(2 if e.code != 0 else 0)

    try:
        snippet = args.snippet_file.read_text()
    except (OSError, IOError) as e:
        print(f"Error reading snippet file: {e}", file=sys.stderr)
        sys.exit(2)

    results = []
    for file_path in args.files:
        try:
            if args.comment_prefix:
                result = check_file(snippet, file_path, comment_prefix=args.comment_prefix)
            elif args.infer_comment_prefix:
                prefix_map = BUILTIN_PREFIX_MAP.copy()
                if args.comment_prefix_map:
                    prefix_map.update(parse_prefix_map(args.comment_prefix_map))
                result = check_file(snippet, file_path, prefix_map=prefix_map)
            else:
                result = check_file(snippet, file_path)
            results.append(result)
        except (OSError, IOError) as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0 if all(results) else 1)
