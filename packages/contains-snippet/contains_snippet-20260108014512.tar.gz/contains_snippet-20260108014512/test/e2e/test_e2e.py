"""End-to-end tests for the CLI."""

from pathlib import Path
from test.helpers import run_cli

import pytest


@pytest.mark.e2e
class TestCliExitCodes:
    """Tests for CLI exit code behavior."""

    def test_exit_0_when_snippet_found(self, tmp_path: Path) -> None:
        """Exit 0 when snippet is found in file."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")
        target_file = tmp_path / "target.md"
        target_file.write_text("say hello world")

        result = run_cli("--snippet-file", str(content_file), str(target_file))
        assert result.returncode == 0

    def test_exit_1_when_snippet_missing(self, tmp_path: Path) -> None:
        """Exit 1 when snippet is not found in file."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("missing")
        target_file = tmp_path / "target.md"
        target_file.write_text("no match here")

        result = run_cli("--snippet-file", str(content_file), str(target_file))
        assert result.returncode == 1

    def test_exit_2_missing_content_file_arg(self) -> None:
        """Exit 2 when --snippet-file argument is missing."""
        result = run_cli("somefile.md")
        assert result.returncode == 2

    def test_exit_2_missing_target_files(self, tmp_path: Path) -> None:
        """Exit 2 when no target files are provided."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        result = run_cli("--snippet-file", str(content_file))
        assert result.returncode == 2

    def test_exit_2_unreadable_content_file(self, tmp_path: Path) -> None:
        """Exit 2 when content file cannot be read."""
        target_file = tmp_path / "target.md"
        target_file.write_text("content")

        result = run_cli(
            "--snippet-file", "/nonexistent/path/file.txt", str(target_file)
        )
        assert result.returncode == 2

    def test_exit_2_unreadable_target_file(self, tmp_path: Path) -> None:
        """Exit 2 when target file cannot be read."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("hello")

        result = run_cli(
            "--snippet-file", str(content_file), "/nonexistent/path/file.md"
        )
        assert result.returncode == 2


@pytest.mark.e2e
class TestCliMultipleFiles:
    """Tests for handling multiple target files."""

    def test_all_files_match(self, tmp_path: Path) -> None:
        """Exit 0 when all files contain the snippet."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("target")
        file1 = tmp_path / "file1.md"
        file1.write_text("has target text")
        file2 = tmp_path / "file2.md"
        file2.write_text("also has target")

        result = run_cli("--snippet-file", str(content_file), str(file1), str(file2))
        assert result.returncode == 0

    def test_one_file_missing(self, tmp_path: Path) -> None:
        """Exit 1 when any file is missing the snippet."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("target")
        file1 = tmp_path / "file1.md"
        file1.write_text("has target text")
        file2 = tmp_path / "file2.md"
        file2.write_text("no match")

        result = run_cli("--snippet-file", str(content_file), str(file1), str(file2))
        assert result.returncode == 1


@pytest.mark.e2e
class TestCliCommentedMatch:
    """Tests for extension-based commented matching."""

    def test_py_file_commented(self, tmp_path: Path) -> None:
        """Python files use commented matching by default."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("snippet content")
        py_file = tmp_path / "code.py"
        py_file.write_text("# snippet content\ncode = 1")

        result = run_cli("--snippet-file", str(content_file), str(py_file))
        assert result.returncode == 0

    def test_yml_file_commented(self, tmp_path: Path) -> None:
        """YAML files use commented matching by default."""
        content_file = tmp_path / "snippet.txt"
        content_file.write_text("config line")
        yml_file = tmp_path / "config.yml"
        yml_file.write_text("#config line\nkey: value")

        result = run_cli("--snippet-file", str(content_file), str(yml_file))
        assert result.returncode == 0


@pytest.mark.e2e
class TestCommentPrefixFlag:
    """Tests for --comment-prefix flag."""

    def test_forces_commented_match_on_md(self, tmp_path: Path) -> None:
        """--comment-prefix forces commented matching on markdown files."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        md_file = tmp_path / "test.md"
        md_file.write_text("# hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--comment-prefix", "#", str(md_file)
        )
        assert result.returncode == 0

    def test_md_raw_fails_with_comment_prefix(self, tmp_path: Path) -> None:
        """Raw content in markdown fails when --comment-prefix is set."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        md_file = tmp_path / "test.md"
        md_file.write_text("hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--comment-prefix", "#", str(md_file)
        )
        assert result.returncode == 1

    def test_custom_prefix_double_slash(self, tmp_path: Path) -> None:
        """--comment-prefix works with // prefix."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        js_file = tmp_path / "test.js"
        js_file.write_text("// hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--comment-prefix", "//", str(js_file)
        )
        assert result.returncode == 0


@pytest.mark.e2e
class TestInferCommentPrefixFlag:
    """Tests for --infer-comment-prefix flag."""

    def test_uses_builtin_mapping_py(self, tmp_path: Path) -> None:
        """Python files use # prefix with --infer-comment-prefix."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        py_file = tmp_path / "test.py"
        py_file.write_text("# hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--infer-comment-prefix", str(py_file)
        )
        assert result.returncode == 0

    def test_uses_builtin_mapping_md_raw(self, tmp_path: Path) -> None:
        """Markdown files use raw matching with --infer-comment-prefix."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        md_file = tmp_path / "test.md"
        md_file.write_text("hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--infer-comment-prefix", str(md_file)
        )
        assert result.returncode == 0

    def test_unknown_ext_defaults_to_raw(self, tmp_path: Path) -> None:
        """Unknown extensions default to raw matching."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")

        result = run_cli(
            "--snippet-file", str(snippet), "--infer-comment-prefix", str(txt_file)
        )
        assert result.returncode == 0

    def test_unknown_ext_uses_raw_not_commented(self, tmp_path: Path) -> None:
        """Unknown extensions don't match as comments."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello\nworld")
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("# hello\n# world")

        result = run_cli(
            "--snippet-file", str(snippet), "--infer-comment-prefix", str(txt_file)
        )
        assert result.returncode == 1


@pytest.mark.e2e
class TestCommentPrefixMapFlag:
    """Tests for --comment-prefix-map flag."""

    def test_overrides_builtin_to_raw(self, tmp_path: Path) -> None:
        """--comment-prefix-map can override Python to raw matching."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        py_file = tmp_path / "test.py"
        py_file.write_text("hello")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".py=raw",
            str(py_file)
        )
        assert result.returncode == 0

    def test_adds_new_extension(self, tmp_path: Path) -> None:
        """--comment-prefix-map can add new extension mappings."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        js_file = tmp_path / "test.js"
        js_file.write_text("// hello")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//",
            str(js_file)
        )
        assert result.returncode == 0


@pytest.mark.e2e
class TestPrecedence:
    """Tests for flag precedence."""

    def test_comment_prefix_overrides_infer(self, tmp_path: Path) -> None:
        """--comment-prefix takes precedence over --infer-comment-prefix."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        py_file = tmp_path / "test.py"
        py_file.write_text("// hello")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--comment-prefix", "//",
            "--infer-comment-prefix",
            str(py_file)
        )
        assert result.returncode == 0

    def test_comment_prefix_overrides_map(self, tmp_path: Path) -> None:
        """--comment-prefix takes precedence over --comment-prefix-map."""
        snippet = tmp_path / "s.txt"
        snippet.write_text("hello")
        py_file = tmp_path / "test.py"
        py_file.write_text("; hello")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--comment-prefix", ";",
            "--infer-comment-prefix",
            "--comment-prefix-map", ".py=#",
            str(py_file)
        )
        assert result.returncode == 0


@pytest.mark.e2e
class TestRealisticMarkdownScenarios:
    """E2E tests for markdown file scenarios."""

    def test_license_snippet_in_readme(self, tmp_path: Path) -> None:
        """License text found in README file."""
        snippet = tmp_path / "license_notice.txt"
        snippet.write_text("Licensed under the Apache License, Version 2.0")

        readme = tmp_path / "README.md"
        readme.write_text(
            "# My Project\n\n"
            "Some description here.\n\n"
            "## License\n\n"
            "Licensed under the Apache License, Version 2.0\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(readme))
        assert result.returncode == 0

    def test_code_block_in_docs(self, tmp_path: Path) -> None:
        """Installation command found in documentation."""
        snippet = tmp_path / "example.txt"
        snippet.write_text("pip install my-package")

        docs = tmp_path / "INSTALL.md"
        docs.write_text(
            "# Installation\n\n"
            "Run the following:\n\n"
            "```bash\n"
            "pip install my-package\n"
            "```\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(docs))
        assert result.returncode == 0


@pytest.mark.e2e
class TestRealisticPythonScenarios:
    """E2E tests for Python file scenarios."""

    def test_multiline_header_comment(self, tmp_path: Path) -> None:
        """Multiline copyright header found in Python file."""
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright 2025\nAll rights reserved")

        py_file = tmp_path / "module.py"
        py_file.write_text(
            "#!/usr/bin/env python\n"
            "# Copyright 2025\n"
            "# All rights reserved\n"
            "\n"
            "def main():\n"
            "    pass\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(py_file))
        assert result.returncode == 0

    def test_snippet_with_empty_lines(self, tmp_path: Path) -> None:
        """Snippet with empty lines matches commented block."""
        snippet = tmp_path / "docblock.txt"
        snippet.write_text("Section 1\n\nSection 2")

        py_file = tmp_path / "code.py"
        py_file.write_text(
            "# Section 1\n"
            "#\n"
            "# Section 2\n"
            "x = 1\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(py_file))
        assert result.returncode == 0


@pytest.mark.e2e
class TestRealisticYamlScenarios:
    """E2E tests for YAML file scenarios."""

    def test_workflow_comment_block(self, tmp_path: Path) -> None:
        """Comment block found in YAML workflow file."""
        snippet = tmp_path / "notice.txt"
        snippet.write_text("Auto-generated file\nDo not edit manually")

        workflow = tmp_path / "ci.yml"
        workflow.write_text(
            "# Auto-generated file\n"
            "# Do not edit manually\n"
            "\n"
            "name: CI\n"
            "on: push\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(workflow))
        assert result.returncode == 0

    def test_yaml_extension(self, tmp_path: Path) -> None:
        """YAML files with .yaml extension use commented matching."""
        snippet = tmp_path / "config_header.txt"
        snippet.write_text("Configuration file")

        config = tmp_path / "settings.yaml"
        config.write_text(
            "#Configuration file\n"
            "database:\n"
            "  host: localhost\n"
        )

        result = run_cli("--snippet-file", str(snippet), str(config))
        assert result.returncode == 0


@pytest.mark.e2e
class TestMixedFileTypes:
    """E2E tests for mixed file type scenarios."""

    def test_multiple_file_types_all_pass(self, tmp_path: Path) -> None:
        """Different file types all contain their snippets."""
        md_snippet = tmp_path / "md_snippet.txt"
        md_snippet.write_text("Important Notice")

        readme = tmp_path / "README.md"
        readme.write_text("# Title\n\nImportant Notice\n")

        result = run_cli("--snippet-file", str(md_snippet), str(readme))
        assert result.returncode == 0

    def test_mixed_pass_fail(self, tmp_path: Path) -> None:
        """Exit 1 when one file passes and another fails."""
        snippet = tmp_path / "required.txt"
        snippet.write_text("REQUIRED TEXT")

        file1 = tmp_path / "has_it.md"
        file1.write_text("This has REQUIRED TEXT in it")

        file2 = tmp_path / "missing.md"
        file2.write_text("This does not have the text")

        result = run_cli(
            "--snippet-file", str(snippet), str(file1), str(file2)
        )
        assert result.returncode == 1


@pytest.mark.e2e
class TestFlagScenarios:
    """E2E tests for CLI flag combinations."""

    def test_mixed_extensions_with_infer(self, tmp_path: Path) -> None:
        """--infer-comment-prefix handles mixed file types."""
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright 2025")

        py_file = tmp_path / "code.py"
        py_file.write_text("# Copyright 2025\ndef main(): pass")

        md_file = tmp_path / "README.md"
        md_file.write_text("# Title\n\nCopyright 2025\n")

        yml_file = tmp_path / "config.yml"
        yml_file.write_text("#Copyright 2025\nkey: value")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--infer-comment-prefix",
            str(py_file), str(md_file), str(yml_file)
        )
        assert result.returncode == 0

    def test_js_files_with_custom_prefix(self, tmp_path: Path) -> None:
        """JavaScript files work with // comment prefix."""
        snippet = tmp_path / "license.txt"
        snippet.write_text("MIT License")

        js_file = tmp_path / "app.js"
        js_file.write_text("// MIT License\nconst x = 1;")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--comment-prefix", "//",
            str(js_file)
        )
        assert result.returncode == 0

    def test_multiple_js_ts_files_with_map(self, tmp_path: Path) -> None:
        """Multiple JS/TS files work with custom prefix map."""
        snippet = tmp_path / "header.txt"
        snippet.write_text("Copyright Notice")

        js_file = tmp_path / "app.js"
        js_file.write_text("// Copyright Notice\nconst x = 1;")

        ts_file = tmp_path / "types.ts"
        ts_file.write_text("//Copyright Notice\ntype X = string;")

        result = run_cli(
            "--snippet-file", str(snippet),
            "--infer-comment-prefix",
            "--comment-prefix-map", ".js=//,.ts=//",
            str(js_file), str(ts_file)
        )
        assert result.returncode == 0

    def test_realistic_multifile_project(self, tmp_path: Path) -> None:
        """Realistic project with multiple file types all pass."""
        header = tmp_path / "license_header.txt"
        header.write_text("Copyright 2025 Acme Inc.\nLicensed under Apache 2.0")

        py_file = tmp_path / "main.py"
        py_file.write_text(
            "#!/usr/bin/env python3\n"
            "# Copyright 2025 Acme Inc.\n"
            "# Licensed under Apache 2.0\n"
            "\n"
            "def main():\n"
            "    print('Hello')\n"
        )

        readme = tmp_path / "README.md"
        readme.write_text(
            "# Project\n\n"
            "Copyright 2025 Acme Inc.\n"
            "Licensed under Apache 2.0\n"
        )

        config = tmp_path / "config.yaml"
        config.write_text(
            "#Copyright 2025 Acme Inc.\n"
            "#Licensed under Apache 2.0\n"
            "setting: value\n"
        )

        result = run_cli(
            "--snippet-file", str(header),
            "--infer-comment-prefix",
            str(py_file), str(readme), str(config)
        )
        assert result.returncode == 0
