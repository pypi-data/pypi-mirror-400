"""Tests for documentation path validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.docs_check import (
    extract_paths_from_markdown,
    extract_paths_from_toml,
    validate_paths,
    validate_toml_paths,
)

pytestmark = pytest.mark.e2e_marker


class TestExtractPaths:
    """Tests for extract_paths_from_markdown."""

    def test_extracts_markdown_links(self):
        content = "See [the file](src/foo/bar.py) for details."
        paths = extract_paths_from_markdown(content)
        assert ("src/foo/bar.py", 1) in paths

    def test_ignores_urls(self):
        content = "See [docs](https://example.com) for more."
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_ignores_anchors(self):
        content = "See [section](#heading) below."
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_extracts_inline_code_paths(self):
        content = "The export file is `frontend/src/lib/index.ts`."
        paths = extract_paths_from_markdown(content)
        assert ("frontend/src/lib/index.ts", 1) in paths

    def test_ignores_inline_code_without_path(self):
        content = "Use `npm install` to install."
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_tracks_line_numbers(self):
        content = "line 1\n[file](src/a.py)\nline 3\n`src/b.ts`"
        paths = extract_paths_from_markdown(content)
        assert ("src/a.py", 2) in paths
        assert ("src/b.ts", 4) in paths

    def test_extracts_multiple_paths_from_same_line(self):
        content = "[a](src/a.py) and [b](src/b.py)"
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 2

    def test_ignores_command_paths(self):
        content = "Run `uv run pytest src/tests`"
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_ignores_glob_patterns_in_links(self):
        content = "See [files](secrets/*.yaml) for examples."
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_ignores_glob_patterns_in_code(self):
        content = "Edit files matching `src/**/*.py`"
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_ignores_placeholder_patterns(self):
        content = "Add tests in `src/djb/cli/tests/e2e/test_<command>.py`"
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0

    def test_ignores_hidden_files(self):
        content = "Config in `.djb/config.yaml` and `secrets/.sops.yaml`"
        paths = extract_paths_from_markdown(content)
        assert len(paths) == 0


class TestValidatePaths:
    """Tests for validate_paths."""

    def test_returns_empty_when_no_agents_md(self, tmp_path: Path):
        errors = validate_paths(tmp_path, tmp_path / "AGENTS.md")
        assert errors == []

    def test_returns_empty_when_all_paths_exist(self, tmp_path: Path):
        # Create file structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo.py").touch()

        # Create AGENTS.md with valid path
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("[file](src/foo.py)")

        errors = validate_paths(tmp_path, agents_md)
        assert errors == []

    def test_returns_error_for_missing_path(self, tmp_path: Path):
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("[file](src/missing.py)")

        errors = validate_paths(tmp_path, agents_md)
        assert len(errors) == 1
        assert errors[0].path == "src/missing.py"
        assert errors[0].line_number == 1

    def test_deduplicates_paths(self, tmp_path: Path):
        agents_md = tmp_path / "AGENTS.md"
        agents_md.write_text("[a](src/missing.py)\n[b](src/missing.py)")

        errors = validate_paths(tmp_path, agents_md)
        assert len(errors) == 1


class TestExtractPathsFromToml:
    """Tests for extract_paths_from_toml."""

    def test_extracts_file_with_line_number(self):
        content = 'files = ["beachresort25/cli/runner.py:222"]'
        paths = extract_paths_from_toml(content)
        assert ("beachresort25/cli/runner.py", 1) in paths

    def test_extracts_file_with_line_range(self):
        content = 'files = ["beachresort25/cli/runner.py:222-241"]'
        paths = extract_paths_from_toml(content)
        assert ("beachresort25/cli/runner.py", 1) in paths

    def test_extracts_multiple_files(self):
        content = 'files = ["src/a.py:1", "src/b.py:2-3"]'
        paths = extract_paths_from_toml(content)
        assert len(paths) == 2
        assert ("src/a.py", 1) in paths
        assert ("src/b.py", 1) in paths

    def test_tracks_line_numbers(self):
        content = """[task1]
title = "foo"
files = ["src/a.py:1"]

[task2]
files = ["src/b.py:2"]"""
        paths = extract_paths_from_toml(content)
        assert ("src/a.py", 3) in paths
        assert ("src/b.py", 6) in paths

    def test_empty_files_array_returns_no_paths(self):
        content = "files = []"
        paths = extract_paths_from_toml(content)
        assert paths == []


class TestValidateTomlPaths:
    """Tests for validate_toml_paths."""

    def test_returns_empty_when_no_toml(self, tmp_path: Path):
        errors = validate_toml_paths(tmp_path, tmp_path / "TODO.toml")
        assert errors == []

    def test_returns_empty_when_all_paths_exist(self, tmp_path: Path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "foo.py").touch()

        toml = tmp_path / "TODO.toml"
        toml.write_text('files = ["src/foo.py:1"]')

        errors = validate_toml_paths(tmp_path, toml)
        assert errors == []

    def test_returns_error_for_missing_path(self, tmp_path: Path):
        toml = tmp_path / "TODO.toml"
        toml.write_text('files = ["src/missing.py:1"]')

        errors = validate_toml_paths(tmp_path, toml)
        assert len(errors) == 1
        assert errors[0].path == "src/missing.py"


class TestRelativePathResolution:
    """Tests for relative path resolution in nested markdown files."""

    def test_resolves_relative_paths_from_nested_file(self, tmp_path: Path):
        # Create structure: docs/decisions/foo.md referencing ../plans/bar.md
        (tmp_path / "docs" / "decisions").mkdir(parents=True)
        (tmp_path / "docs" / "plans").mkdir(parents=True)
        (tmp_path / "docs" / "plans" / "bar.md").touch()

        md_file = tmp_path / "docs" / "decisions" / "foo.md"
        md_file.write_text("[plan](../plans/bar.md)")

        errors = validate_paths(tmp_path, md_file)
        assert errors == []

    def test_error_for_missing_relative_path(self, tmp_path: Path):
        (tmp_path / "docs" / "decisions").mkdir(parents=True)

        md_file = tmp_path / "docs" / "decisions" / "foo.md"
        md_file.write_text("[plan](../plans/missing.md)")

        errors = validate_paths(tmp_path, md_file)
        assert len(errors) == 1
        assert errors[0].path == "../plans/missing.md"

    def test_skips_external_relative_paths(self, tmp_path: Path):
        # Path resolving outside project root should be skipped
        md_file = tmp_path / "docs.md"
        md_file.write_text("[external](../other-project/file.py)")

        errors = validate_paths(tmp_path, md_file)
        assert errors == []  # Should skip, not error

    def test_resolves_bare_filename_from_same_directory(self, tmp_path: Path):
        # Bare filenames (no /) should resolve relative to markdown file's directory
        (tmp_path / "docs" / "decisions").mkdir(parents=True)
        (tmp_path / "docs" / "decisions" / "000-template.md").touch()

        md_file = tmp_path / "docs" / "decisions" / "README.md"
        md_file.write_text("[template](000-template.md)")

        errors = validate_paths(tmp_path, md_file)
        assert errors == []

    def test_error_for_missing_bare_filename(self, tmp_path: Path):
        (tmp_path / "docs" / "decisions").mkdir(parents=True)

        md_file = tmp_path / "docs" / "decisions" / "README.md"
        md_file.write_text("[template](missing.md)")

        errors = validate_paths(tmp_path, md_file)
        assert len(errors) == 1
        assert errors[0].path == "missing.md"
