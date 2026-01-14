"""E2E tests for djb health docs command."""

from __future__ import annotations

from pathlib import Path

import pytest

from djb.cli.djb import djb_cli


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def project_dir(health_project: Path) -> Path:
    """Use health_project for all tests in this module."""
    return health_project


class TestHealthDocs:
    """E2E tests for djb health docs."""

    def test_passes_when_all_paths_exist(self, cli_runner, project_dir: Path):
        """Docs check passes when all referenced paths exist."""
        # Create referenced file
        (project_dir / "src").mkdir()
        (project_dir / "src" / "main.py").touch()

        # Create AGENTS.md with valid reference
        (project_dir / "AGENTS.md").write_text("See [source](src/main.py)")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code == 0
        assert "Documentation paths validated" in result.output

    def test_fails_when_path_missing(self, cli_runner, project_dir: Path):
        """Docs check fails when referenced path doesn't exist."""
        # Create AGENTS.md with invalid reference
        (project_dir / "AGENTS.md").write_text("See [source](src/missing.py)")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code != 0
        assert "src/missing.py" in result.output

    def test_passes_when_no_agents_md(self, cli_runner, project_dir: Path):
        """Docs check passes when no AGENTS.md exists."""
        # Ensure no AGENTS.md exists
        agents_md = project_dir / "AGENTS.md"
        if agents_md.exists():
            agents_md.unlink()

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code == 0

    def test_reports_line_numbers(self, cli_runner, project_dir: Path):
        """Docs check reports line numbers for missing paths."""
        # Create AGENTS.md with invalid reference on line 3
        (project_dir / "AGENTS.md").write_text("# Title\n\nSee [source](src/missing.py)")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code != 0
        assert ":3:" in result.output

    def test_checks_multiple_markdown_files(self, cli_runner, project_dir: Path):
        """Docs check validates all markdown files in project root."""
        # Create referenced file
        (project_dir / "src").mkdir()
        (project_dir / "src" / "main.py").touch()

        # Create multiple markdown files
        (project_dir / "AGENTS.md").write_text("See [source](src/main.py)")
        (project_dir / "README.md").write_text("See [missing](src/missing.py)")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code != 0
        assert "README.md" in result.output
        assert "src/missing.py" in result.output

    def test_handles_symlinks_without_duplicates(self, cli_runner, project_dir: Path):
        """Symlinked markdown files are only validated once."""
        # Create referenced file
        (project_dir / "src").mkdir()
        (project_dir / "src" / "main.py").touch()

        # Create AGENTS.md and symlink CLAUDE.md to it
        (project_dir / "AGENTS.md").write_text("See [source](src/main.py)")
        (project_dir / "CLAUDE.md").symlink_to("AGENTS.md")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "docs"],
        )
        assert result.exit_code == 0
        assert "Documentation paths validated" in result.output
