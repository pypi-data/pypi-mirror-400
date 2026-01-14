"""End-to-end tests for djb health barrels CLI command.

These tests exercise the barrel export validation command with real
file structures and actual file I/O.

Commands tested:
- djb health barrels
- djb health barrels --fix
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

from djb.cli.djb import djb_cli
from djb.cli.health_barrels import (
    BarrelListing,
    check_barrel,
    extract_exports,
    extract_python_exports,
    extract_typescript_exports,
    find_barrel_listings,
    fix_barrels_in_file,
    format_exports_line,
)

from . import create_pyproject_toml


# Mark all tests in this module as e2e (use --no-e2e to skip)
pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def barrels_project(
    project_dir: Path,
    make_project_with_git_repo: Callable[..., Path],
) -> Path:
    """Project with barrel files for barrel validation tests.

    Creates:
    - pyproject.toml with minimal config
    - Python barrel file with __all__
    - TypeScript barrel file with exports
    - AGENTS.md with barrel listings
    """
    create_pyproject_toml(project_dir, name="barrelsproject")

    # Create Python barrel
    lib_dir = project_dir / "src" / "lib"
    lib_dir.mkdir(parents=True)
    (lib_dir / "__init__.py").write_text(
        '''"""Library barrel export."""

__all__ = [
    "Alpha",
    "Beta",
    "Gamma",
]
'''
    )

    # Create TypeScript barrel
    frontend_dir = project_dir / "frontend" / "src" / "lib"
    frontend_dir.mkdir(parents=True)
    (frontend_dir / "index.ts").write_text(
        """// Frontend barrel export
export { Foo, Bar } from './components'
export type { BazType } from './types'
"""
    )

    # Create AGENTS.md with barrel listings
    agents_md = project_dir / "AGENTS.md"
    agents_md.write_text(
        """# AI Notes

## Barrel Exports

**Lib** [`src/lib/__init__.py`]: `Alpha`, `Beta`, `Gamma`

**Frontend** [`frontend/src/lib/index.ts`]: `Foo`, `Bar`, `BazType`
"""
    )

    # Initialize git
    make_project_with_git_repo(
        repo_path=project_dir,
        user_email="test@example.com",
        user_name="Test User",
        with_initial_commit=False,
    )

    return project_dir


class TestHealthBarrelsCheck:
    """E2E tests for djb health barrels command (check mode)."""

    def test_barrels_pass_when_in_sync(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrels check passes when all listings are in sync."""
        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        assert result.exit_code == 0
        assert "in sync" in result.output.lower() or "barrel listing" in result.output.lower()

    def test_barrels_fail_when_missing_exports(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrels check fails when source has exports not in docs."""
        # Add a new export to Python barrel
        lib_init = barrels_project / "src" / "lib" / "__init__.py"
        lib_init.write_text(
            '''"""Library barrel export."""

__all__ = [
    "Alpha",
    "Beta",
    "Gamma",
    "Delta",  # New export not in AGENTS.md
]
'''
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        assert result.exit_code != 0
        assert "missing" in result.output.lower()
        assert "Delta" in result.output

    def test_barrels_fail_when_extra_exports(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrels check fails when docs have exports not in source."""
        # Remove an export from Python barrel
        lib_init = barrels_project / "src" / "lib" / "__init__.py"
        lib_init.write_text(
            '''"""Library barrel export."""

__all__ = [
    "Alpha",
    "Beta",
    # Gamma removed
]
'''
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        assert result.exit_code != 0
        assert "extra" in result.output.lower()
        assert "Gamma" in result.output

    def test_barrels_shows_fix_tip(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrels check shows tip to run with --fix."""
        # Make listing out of sync
        lib_init = barrels_project / "src" / "lib" / "__init__.py"
        lib_init.write_text('__all__ = ["New"]')

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        assert result.exit_code != 0
        assert "--fix" in result.output


class TestHealthBarrelsFix:
    """E2E tests for djb health barrels --fix command."""

    def test_fix_updates_out_of_sync_barrel(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Fix updates markdown when barrel is out of sync."""
        # Change Python barrel exports
        lib_init = barrels_project / "src" / "lib" / "__init__.py"
        lib_init.write_text('__all__ = ["NewExport", "AnotherExport"]')

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels", "--fix"],
        )

        assert result.exit_code == 0

        # Verify AGENTS.md was updated
        agents_content = (barrels_project / "AGENTS.md").read_text()
        assert "`NewExport`" in agents_content
        assert "`AnotherExport`" in agents_content
        # Old exports should be gone
        assert "`Alpha`" not in agents_content
        assert "`Beta`" not in agents_content

    def test_fix_preserves_in_sync_barrels(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Fix does not modify barrels that are already in sync."""
        original_content = (barrels_project / "AGENTS.md").read_text()

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels", "--fix"],
        )

        assert result.exit_code == 0

        # Content should be unchanged
        assert (barrels_project / "AGENTS.md").read_text() == original_content

    def test_fix_updates_typescript_barrel(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Fix updates TypeScript barrel listings."""
        # Change TypeScript barrel exports
        ts_barrel = barrels_project / "frontend" / "src" / "lib" / "index.ts"
        ts_barrel.write_text(
            """export { Component, Widget } from './ui'
export type { Config } from './config'
"""
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels", "--fix"],
        )

        assert result.exit_code == 0

        # Verify AGENTS.md was updated
        agents_content = (barrels_project / "AGENTS.md").read_text()
        assert "`Component`" in agents_content
        assert "`Widget`" in agents_content
        assert "`Config`" in agents_content
        # Old exports should be gone
        assert "`Foo`" not in agents_content
        assert "`Bar`" not in agents_content

    def test_fix_reports_updated_files(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Fix reports which files were updated."""
        # Make listing out of sync
        lib_init = barrels_project / "src" / "lib" / "__init__.py"
        lib_init.write_text('__all__ = ["Changed"]')

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels", "--fix"],
        )

        assert result.exit_code == 0
        assert "AGENTS.md" in result.output
        assert "fixed" in result.output.lower() or "updated" in result.output.lower()


class TestHealthBarrelsMultipleFiles:
    """E2E tests for barrel validation across multiple markdown files."""

    def test_checks_multiple_markdown_files(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrel check scans multiple markdown files."""
        # Create docs directory with another markdown file
        docs_dir = barrels_project / "docs"
        docs_dir.mkdir()
        (docs_dir / "api.md").write_text(
            "**Lib** [`src/lib/__init__.py`]: `Alpha`, `Beta`, `Gamma`\n"
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        # Both files should be checked
        assert result.exit_code == 0
        assert "2 file(s)" in result.output or "barrel listing" in result.output.lower()

    def test_fix_updates_multiple_files(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Fix updates barrel listings in multiple files."""
        # Create docs with out-of-sync listing
        docs_dir = barrels_project / "docs"
        docs_dir.mkdir()
        (docs_dir / "api.md").write_text("**Lib** [`src/lib/__init__.py`]: `Old`, `Exports`\n")

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels", "--fix"],
        )

        assert result.exit_code == 0

        # Verify docs/api.md was updated
        api_content = (docs_dir / "api.md").read_text()
        assert "`Alpha`" in api_content
        assert "`Beta`" in api_content
        assert "`Old`" not in api_content


class TestHealthBarrelsNoListings:
    """E2E tests for projects without barrel listings."""

    def test_no_listings_shows_notice(
        self,
        cli_runner,
        project_dir: Path,
        make_project_with_git_repo: Callable[..., Path],
    ):
        """Projects without barrel listings show a notice."""
        create_pyproject_toml(project_dir, name="emptyproject")

        # Create AGENTS.md without barrel format
        (project_dir / "AGENTS.md").write_text("# Notes\n\nNo barrels here.\n")

        make_project_with_git_repo(
            repo_path=project_dir,
            user_email="test@example.com",
            user_name="Test User",
            with_initial_commit=False,
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(project_dir), "health", "barrels"],
        )

        assert result.exit_code == 0
        assert "no barrel" in result.output.lower()


class TestHealthBarrelsMissingFile:
    """E2E tests for barrel listings pointing to missing files."""

    def test_missing_source_file_reports_extra(
        self,
        cli_runner,
        barrels_project: Path,
    ):
        """Barrel listing with missing source file reports all exports as extra."""
        # Create AGENTS.md pointing to non-existent file
        (barrels_project / "AGENTS.md").write_text(
            "**Missing** [`src/missing/__init__.py`]: `Foo`, `Bar`\n"
        )

        result = cli_runner.invoke(
            djb_cli,
            ["--project-dir", str(barrels_project), "health", "barrels"],
        )

        assert result.exit_code != 0
        assert "extra" in result.output.lower()
        assert "Foo" in result.output
        assert "Bar" in result.output


# =============================================================================
# Tests for barrel parsing and extraction functions (merged from unit tests)
# =============================================================================


class TestFindBarrelListings:
    """Tests for finding barrel listings in markdown content."""

    def test_finds_single_barrel(self):
        content = "**Components** [`frontend/src/lib/index.ts`]: `foo`, `bar`"
        listings = find_barrel_listings(content)
        assert len(listings) == 1
        assert listings[0].label == "Components"
        assert listings[0].file_path == "frontend/src/lib/index.ts"
        assert listings[0].exports == ["foo", "bar"]

    def test_finds_multiple_barrels(self):
        content = """**Components** [`src/a.ts`]: `A`, `B`

**Utils** [`src/b.py`]: `C`, `D`"""
        listings = find_barrel_listings(content)
        assert len(listings) == 2
        assert listings[0].label == "Components"
        assert listings[1].label == "Utils"

    def test_tracks_line_numbers(self):
        content = """# Header

**Components** [`src/index.ts`]: `foo`

Some text."""
        listings = find_barrel_listings(content)
        assert len(listings) == 1
        assert listings[0].line_number == 3

    def test_handles_multiword_labels(self):
        content = "**DJB Core Module** [`djb/core/__init__.py`]: `error`"
        listings = find_barrel_listings(content)
        assert len(listings) == 1
        assert listings[0].label == "DJB Core Module"

    def test_handles_many_exports(self):
        content = "**Lib** [`src/lib.ts`]: `a`, `b`, `c`, `d`, `e`"
        listings = find_barrel_listings(content)
        assert len(listings) == 1
        assert listings[0].exports == ["a", "b", "c", "d", "e"]

    def test_ignores_non_barrel_bold_text(self):
        content = """**Note**: This is a note.

See the **important** file."""
        listings = find_barrel_listings(content)
        assert len(listings) == 0

    def test_handles_consecutive_barrels(self):
        content = """**A** [`a.ts`]: `x`
**B** [`b.ts`]: `y`"""
        listings = find_barrel_listings(content)
        assert len(listings) == 2

    def test_empty_content_returns_empty_list(self):
        listings = find_barrel_listings("")
        assert listings == []


class TestExtractPythonExports:
    """Tests for extracting __all__ from Python files."""

    def test_extracts_simple_all(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["foo", "bar"]')
        exports = extract_python_exports(py_file)
        assert exports == ["foo", "bar"]

    def test_extracts_multiline_all(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text(
            """__all__ = [
    "alpha",
    "beta",
    "gamma",
]"""
        )
        exports = extract_python_exports(py_file)
        assert exports == ["alpha", "beta", "gamma"]

    def test_returns_empty_when_no_all(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text("def foo(): pass")
        exports = extract_python_exports(py_file)
        assert exports == []

    def test_returns_empty_for_missing_file(self, tmp_path: Path):
        exports = extract_python_exports(tmp_path / "missing.py")
        assert exports == []

    def test_returns_empty_for_syntax_error(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text("def broken(")
        exports = extract_python_exports(py_file)
        assert exports == []

    def test_ignores_non_string_elements(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["foo", 123, "bar"]')
        exports = extract_python_exports(py_file)
        assert exports == ["foo", "bar"]

    def test_handles_all_with_imports(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text(
            """from .module import Foo, Bar

__all__ = ["Foo", "Bar"]
"""
        )
        exports = extract_python_exports(py_file)
        assert exports == ["Foo", "Bar"]


class TestExtractTypescriptExports:
    """Tests for extracting exports from TypeScript files."""

    def test_extracts_simple_export(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text("export { foo, bar } from './module'")
        exports = extract_typescript_exports(ts_file)
        assert "foo" in exports
        assert "bar" in exports

    def test_extracts_type_export(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text("export type { FooType, BarType } from './types'")
        exports = extract_typescript_exports(ts_file)
        assert "FooType" in exports
        assert "BarType" in exports

    def test_extracts_multiple_exports(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text(
            """export { a, b } from './a'
export { c } from './c'
export type { D } from './d'"""
        )
        exports = extract_typescript_exports(ts_file)
        assert set(exports) == {"a", "b", "c", "D"}

    def test_handles_renamed_export(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text("export { internal as External } from './module'")
        exports = extract_typescript_exports(ts_file)
        assert exports == ["External"]

    def test_returns_empty_for_missing_file(self, tmp_path: Path):
        exports = extract_typescript_exports(tmp_path / "missing.ts")
        assert exports == []

    def test_handles_multiline_export(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text(
            """export {
    alpha,
    beta,
    gamma,
} from './lib'"""
        )
        exports = extract_typescript_exports(ts_file)
        assert set(exports) == {"alpha", "beta", "gamma"}


class TestExtractExports:
    """Tests for the unified extract_exports function."""

    def test_routes_py_to_python_extractor(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["x"]')
        exports = extract_exports(py_file)
        assert exports == ["x"]

    def test_routes_ts_to_typescript_extractor(self, tmp_path: Path):
        ts_file = tmp_path / "index.ts"
        ts_file.write_text("export { y } from './y'")
        exports = extract_exports(ts_file)
        assert exports == ["y"]

    def test_routes_tsx_to_typescript_extractor(self, tmp_path: Path):
        tsx_file = tmp_path / "index.tsx"
        tsx_file.write_text("export { z } from './z'")
        exports = extract_exports(tsx_file)
        assert exports == ["z"]

    def test_returns_empty_for_unknown_extension(self, tmp_path: Path):
        txt_file = tmp_path / "file.txt"
        txt_file.write_text("some content")
        exports = extract_exports(txt_file)
        assert exports == []


class TestFormatExportsLine:
    """Tests for formatting barrel listing lines."""

    def test_formats_simple_line(self):
        line = format_exports_line("Components", "src/index.ts", ["foo", "bar"])
        assert line == "**Components** [`src/index.ts`]: `foo`, `bar`"

    def test_formats_single_export(self):
        line = format_exports_line("Main", "main.py", ["entry"])
        assert line == "**Main** [`main.py`]: `entry`"

    def test_formats_empty_exports(self):
        line = format_exports_line("Empty", "empty.ts", [])
        assert line == "**Empty** [`empty.ts`]: "


class TestCheckBarrel:
    """Tests for checking a single barrel listing."""

    def test_returns_none_when_in_sync(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["foo", "bar"]')

        listing = BarrelListing(
            label="Test",
            file_path="barrel.py",
            exports=["foo", "bar"],
            line_number=1,
            match_start=0,
            match_end=50,
        )
        discrepancy = check_barrel(tmp_path, listing)
        assert discrepancy is None

    def test_detects_missing_exports(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["foo", "bar", "baz"]')

        listing = BarrelListing(
            label="Test",
            file_path="barrel.py",
            exports=["foo"],
            line_number=1,
            match_start=0,
            match_end=50,
        )
        discrepancy = check_barrel(tmp_path, listing)
        assert discrepancy is not None
        assert set(discrepancy.missing) == {"bar", "baz"}
        assert discrepancy.extra == []

    def test_detects_extra_exports(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["foo"]')

        listing = BarrelListing(
            label="Test",
            file_path="barrel.py",
            exports=["foo", "bar", "baz"],
            line_number=1,
            match_start=0,
            match_end=50,
        )
        discrepancy = check_barrel(tmp_path, listing)
        assert discrepancy is not None
        assert discrepancy.missing == []
        assert set(discrepancy.extra) == {"bar", "baz"}

    def test_detects_both_missing_and_extra(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["actual"]')

        listing = BarrelListing(
            label="Test",
            file_path="barrel.py",
            exports=["documented"],
            line_number=1,
            match_start=0,
            match_end=50,
        )
        discrepancy = check_barrel(tmp_path, listing)
        assert discrepancy is not None
        assert discrepancy.missing == ["actual"]
        assert discrepancy.extra == ["documented"]

    def test_handles_missing_file(self, tmp_path: Path):
        listing = BarrelListing(
            label="Test",
            file_path="missing.py",
            exports=["foo"],
            line_number=1,
            match_start=0,
            match_end=50,
        )
        discrepancy = check_barrel(tmp_path, listing)
        assert discrepancy is not None
        assert discrepancy.extra == ["foo"]
        assert discrepancy.missing == []


class TestFixBarrelsInFile:
    """Tests for fixing barrel listings in markdown files."""

    def test_fixes_out_of_sync_barrel(self, tmp_path: Path):
        # Create barrel file
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["new_a", "new_b"]')

        # Create markdown with outdated listing
        md_file = tmp_path / "docs.md"
        md_file.write_text("**Test** [`barrel.py`]: `old_a`, `old_b`")

        fixed = fix_barrels_in_file(tmp_path, md_file)
        assert fixed == 1

        content = md_file.read_text()
        assert "`new_a`" in content
        assert "`new_b`" in content
        assert "`old_a`" not in content

    def test_does_not_modify_synced_barrel(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["a", "b"]')

        md_file = tmp_path / "docs.md"
        original = "**Test** [`barrel.py`]: `a`, `b`"
        md_file.write_text(original)

        fixed = fix_barrels_in_file(tmp_path, md_file)
        assert fixed == 0

        content = md_file.read_text()
        assert content == original

    def test_fixes_multiple_barrels(self, tmp_path: Path):
        # Create two barrel files
        (tmp_path / "a.py").write_text('__all__ = ["x"]')
        (tmp_path / "b.py").write_text('__all__ = ["y"]')

        md_file = tmp_path / "docs.md"
        md_file.write_text(
            """**A** [`a.py`]: `wrong`

**B** [`b.py`]: `also_wrong`"""
        )

        fixed = fix_barrels_in_file(tmp_path, md_file)
        assert fixed == 2

        content = md_file.read_text()
        assert "`x`" in content
        assert "`y`" in content

    def test_returns_zero_for_missing_file(self, tmp_path: Path):
        fixed = fix_barrels_in_file(tmp_path, tmp_path / "missing.md")
        assert fixed == 0

    def test_returns_zero_for_no_listings(self, tmp_path: Path):
        md_file = tmp_path / "docs.md"
        md_file.write_text("# Just a heading\n\nNo barrel listings here.")

        fixed = fix_barrels_in_file(tmp_path, md_file)
        assert fixed == 0

    def test_preserves_surrounding_content(self, tmp_path: Path):
        py_file = tmp_path / "barrel.py"
        py_file.write_text('__all__ = ["new"]')

        md_file = tmp_path / "docs.md"
        md_file.write_text(
            """# Header

Before text.

**Test** [`barrel.py`]: `old`

After text."""
        )

        fix_barrels_in_file(tmp_path, md_file)

        content = md_file.read_text()
        assert "# Header" in content
        assert "Before text." in content
        assert "After text." in content
        assert "`new`" in content
