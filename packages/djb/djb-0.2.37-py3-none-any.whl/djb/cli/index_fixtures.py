"""
djb index fixtures - Generate fixture package indexes.

Discovers pytest fixtures using AST parsing and generates a TOML-formatted
index in the [fixtures] section of pytest_index.toml files.

The index helps document fixture availability and can find duplicate fixtures.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.indexer import (
    SimilarTestPair,
    compute_text_similarity,
    find_test_packages,
    get_projects_to_index,
    parse_index_from_toml,
    write_toml_index,
)
from djb.core.logging import get_logger


logger = get_logger(__name__)


class FixtureItem(NamedTuple):
    """Represents a collected fixture with its metadata."""

    file_path: Path  # Path to the file containing the fixture
    module_name: str  # Module name (e.g., "conftest", "test_health")
    class_name: str | None  # Class name if nested, else None
    fixture_name: str  # Fixture function name
    docstring: str | None  # First line of docstring


@dataclass
class FixturePackageIndex:
    """Index of fixtures in a package."""

    index_path: Path  # Path to pytest_index.toml
    package_path: Path
    fixtures: list[FixtureItem] = field(default_factory=list)


def _get_first_line(docstring: str | None) -> str | None:
    """Get the first line of a docstring, or None if empty."""
    if not docstring:
        return None
    first_line = docstring.strip().split("\n")[0].strip()
    return first_line if first_line else None


def _has_pytest_fixture_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if a function has @pytest.fixture decorator."""
    for decorator in node.decorator_list:
        # Handle @pytest.fixture
        if isinstance(decorator, ast.Attribute):
            if (
                isinstance(decorator.value, ast.Name)
                and decorator.value.id == "pytest"
                and decorator.attr == "fixture"
            ):
                return True
        # Handle @pytest.fixture()
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if (
                    isinstance(decorator.func.value, ast.Name)
                    and decorator.func.value.id == "pytest"
                    and decorator.func.attr == "fixture"
                ):
                    return True
    return False


def parse_fixtures(file_path: Path) -> list[FixtureItem]:
    """Parse fixtures from a Python file using AST.

    Returns list of FixtureItem for each @pytest.fixture decorated function.
    Handles both module-level and class-nested fixtures.
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return []

    fixtures: list[FixtureItem] = []
    module_name = file_path.stem  # e.g., "conftest" or "test_health"

    # Find module-level fixtures
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _has_pytest_fixture_decorator(node):
                docstring = _get_first_line(ast.get_docstring(node))
                fixtures.append(
                    FixtureItem(
                        file_path=file_path,
                        module_name=module_name,
                        class_name=None,
                        fixture_name=node.name,
                        docstring=docstring,
                    )
                )

    # Find class-nested fixtures
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _has_pytest_fixture_decorator(item):
                        docstring = _get_first_line(ast.get_docstring(item))
                        fixtures.append(
                            FixtureItem(
                                file_path=file_path,
                                module_name=module_name,
                                class_name=node.name,
                                fixture_name=item.name,
                                docstring=docstring,
                            )
                        )

    return fixtures


def find_fixture_files(package_path: Path) -> list[Path]:
    """Find all Python files that may contain fixtures in a package.

    Looks for:
    - conftest.py files
    - test_*.py files
    - *_test.py files
    - tests.py files
    """
    files: list[Path] = []

    # Find all Python files in the package
    for py_file in package_path.rglob("*.py"):
        # Skip virtual environments and common exclusions
        parts = py_file.parts
        if ".venv" in parts or "node_modules" in parts:
            continue
        if "site-packages" in parts:
            continue

        name = py_file.name
        # Include conftest.py, test files, and files named tests.py
        if name == "conftest.py":
            files.append(py_file)
        elif name.startswith("test_") and name.endswith(".py"):
            files.append(py_file)
        elif name.endswith("_test.py"):
            files.append(py_file)
        elif name == "tests.py":
            files.append(py_file)

    return sorted(files)


def collect_fixtures(project_root: Path) -> list[FixtureItem]:
    """Collect all fixtures from a project.

    Scans all fixture-containing files and parses them for @pytest.fixture.
    """
    all_fixtures: list[FixtureItem] = []

    fixture_files = find_fixture_files(project_root)
    for file_path in fixture_files:
        fixtures = parse_fixtures(file_path)
        all_fixtures.extend(fixtures)

    return all_fixtures


def group_fixtures_by_package(
    index_paths: list[Path],
    fixtures: list[FixtureItem],
) -> list[FixturePackageIndex]:
    """Group fixtures by their containing test package."""
    package_indexes: list[FixturePackageIndex] = []

    for index_path in index_paths:
        package_path = index_path.parent
        # Find fixtures that belong to this package
        package_fixtures = [
            f
            for f in fixtures
            if package_path in f.file_path.parents or f.file_path.parent == package_path
        ]
        if package_fixtures:
            package_indexes.append(
                FixturePackageIndex(
                    index_path=index_path,
                    package_path=package_path,
                    fixtures=package_fixtures,
                )
            )

    return package_indexes


def build_fixture_key(fixture: FixtureItem) -> str:
    """Build the dotted key for a fixture.

    Format: module.ClassName.fixture_name (ClassName optional)
    """
    if fixture.class_name:
        return f"{fixture.module_name}.{fixture.class_name}.{fixture.fixture_name}"
    return f"{fixture.module_name}.{fixture.fixture_name}"


def build_fixture_index_data(package_index: FixturePackageIndex) -> dict[str, str]:
    """Build fixture index data structure for TOML output.

    Returns a dict with dotted keys:
    {
        "conftest.runner": "Click CLI test runner.",
        "conftest.TestClass.fixture": "Fixture docstring.",
    }
    """
    fixtures_data: dict[str, str] = {}

    for fixture in package_index.fixtures:
        key = build_fixture_key(fixture)
        fixtures_data[key] = fixture.docstring or ""

    # Sort by key for consistent output
    return dict(sorted(fixtures_data.items()))


def merge_fixture_index(index_path: Path, fixtures_data: dict[str, str]) -> dict:
    """Merge fixtures into existing index, preserving [tests] section."""
    existing = parse_index_from_toml(index_path)
    if existing is None:
        existing = {}

    # Preserve existing sections, update fixtures
    existing["fixtures"] = fixtures_data
    return existing


def find_similar_fixtures(
    fixtures_data: dict[str, str],
    min_similarity: float = 0.8,
) -> list[SimilarTestPair]:
    """Find fixtures with similar docstrings.

    Reuses SimilarTestPair since the structure is identical.
    """
    # Collect all fixture docstrings with their keys
    all_fixtures: list[tuple[str, str]] = [
        (key, value) for key, value in fixtures_data.items() if value
    ]

    # Compare all pairs
    similar_pairs = []
    for i, (name1, doc1) in enumerate(all_fixtures):
        for name2, doc2 in all_fixtures[i + 1 :]:
            similarity = compute_text_similarity(doc1, doc2)
            if similarity >= min_similarity:
                similar_pairs.append(
                    SimilarTestPair(
                        test1=name1,
                        test2=name2,
                        doc1=doc1,
                        doc2=doc2,
                        similarity=similarity,
                    )
                )

    return sorted(similar_pairs, key=lambda x: -x.similarity)


@click.command("fixtures")
@click.option(
    "--check-unique",
    is_flag=True,
    help="Find fixtures with similar descriptions (potential duplicates).",
)
@click.option(
    "--min-similarity",
    type=float,
    default=0.8,
    show_default=True,
    help="Minimum similarity threshold for --check-unique (0.0-1.0).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be changed without modifying files.",
)
@djb_pass_context
def fixtures_cmd(
    cli_ctx: CliContext,
    check_unique: bool,
    min_similarity: float,
    dry_run: bool,
):
    """Generate fixture package indexes.

    Discovers pytest fixtures using AST parsing and generates a TOML-formatted
    index in the [fixtures] section of pytest_index.toml files.

    The index helps document fixture availability and find duplicates.

    \b
    Examples:
        djb index fixtures              # Generate indexes
        djb index fixtures --dry-run    # Preview changes
        djb index fixtures --check-unique    # Find similar fixtures
    """
    config = cli_ctx.config
    projects = get_projects_to_index(config)

    # For check mode, read existing indexes
    if check_unique:
        all_fixture_data: dict[str, str] = {}
        seen_paths: set[Path] = set()

        for proj_root in projects:
            index_paths = find_test_packages(proj_root)
            for index_path in index_paths:
                abs_path = index_path.resolve()
                if abs_path in seen_paths:
                    continue
                seen_paths.add(abs_path)

                parsed = parse_index_from_toml(index_path)
                if parsed and "fixtures" in parsed:
                    rel_path = index_path.relative_to(proj_root)
                    for key, value in parsed["fixtures"].items():
                        prefixed_key = f"{rel_path.parent}::{key}"
                        all_fixture_data[prefixed_key] = value

        if not all_fixture_data:
            logger.warning(
                "No fixture indexes found. Run 'djb index fixtures' first to generate indexes."
            )
            return

        similar = find_similar_fixtures(all_fixture_data, min_similarity)
        if similar:
            logger.warning(f"Found {len(similar)} pairs with similar descriptions:")
            for pair in similar:
                logger.info(f"  {pair.similarity:.0%} similar:")
                logger.info(f"    {pair.test1}")
                logger.info(f'      "{pair.doc1}"')
                logger.info(f"    {pair.test2}")
                logger.info(f'      "{pair.doc2}"')
        else:
            logger.done("No fixtures with similar descriptions found")

        return

    # Generate indexes
    processed_dirs: list[Path] = []

    for proj_root in projects:
        logger.info(f"Collecting fixtures from {proj_root.name}...")

        # Collect fixtures
        fixtures = collect_fixtures(proj_root)
        if not fixtures:
            logger.info(f"  No fixtures found in {proj_root.name}")
            processed_dirs.append(proj_root)
            continue

        # Find test packages
        index_paths = find_test_packages(proj_root, exclude_dirs=processed_dirs)

        # Group fixtures by package
        package_indexes = group_fixtures_by_package(index_paths, fixtures)

        # Mark this project as processed
        processed_dirs.append(proj_root)

        # Update files
        updated_count = 0
        for pkg_idx in package_indexes:
            fixtures_data = build_fixture_index_data(pkg_idx)
            merged_data = merge_fixture_index(pkg_idx.index_path, fixtures_data)

            if dry_run:
                rel_path = pkg_idx.index_path.relative_to(proj_root)
                logger.info(f"  Would update: {rel_path}")
                logger.info(f"    {len(fixtures_data)} fixtures")
            else:
                if write_toml_index(pkg_idx.index_path, merged_data):
                    rel_path = pkg_idx.index_path.relative_to(proj_root)
                    logger.done(f"  Updated: {rel_path}")
                    updated_count += 1

        if not dry_run:
            logger.info(f"  Updated {updated_count} fixture package indexes")
