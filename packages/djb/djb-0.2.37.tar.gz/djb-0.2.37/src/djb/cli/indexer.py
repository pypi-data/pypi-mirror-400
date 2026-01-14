"""
djb index tests - Generate test package indexes.

Discovers tests using pytest, parses their docstrings, and generates
a TOML-formatted index file (pytest_index.toml) in each test package.

The index helps document test coverage and can be regenerated at any time.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Final, NamedTuple

import click

from djb.cli.context import CliContext, djb_pass_context
from djb.cli.editable import get_djb_source_path, is_djb_editable
from djb.core.cmd_runner import CmdRunner

# Maximum characters of stderr to show when pytest collection fails
STDERR_TRUNCATE_LENGTH: Final[int] = 200
from djb.core.locking import atomic_write, file_lock
from djb.core.logging import get_logger
from djb.config.storage.utils import dump_toml, parse_toml

from tomlkit.exceptions import ParseError

logger = get_logger(__name__)

# Index file name
INDEX_FILENAME = "pytest_index.toml"


class CollectedTest(NamedTuple):
    """Represents a collected test with its metadata."""

    node_id: str  # Full pytest node ID (file::Class::method)
    file_path: Path  # Path to test file
    class_name: str | None  # Test class name (or None for module-level)
    method_name: str  # Test method/function name
    class_doc: str | None  # Class docstring (first line)
    method_doc: str | None  # Method docstring (first line)


@dataclass
class PackageTestIndex:
    """Index of tests in a package."""

    index_path: Path  # Path to pytest_index.toml
    package_path: Path
    tests: list[CollectedTest] = field(default_factory=list)


class SimilarTestPair(NamedTuple):
    """A pair of tests with similar descriptions."""

    test1: str
    test2: str
    doc1: str
    doc2: str
    similarity: float


def collect_tests(runner: CmdRunner, project_root: Path) -> dict[str, list[str]]:
    """Collect all tests using pytest --collect-only.

    Returns dict mapping test file paths to list of test node IDs.
    """
    result = runner.run(
        ["uv", "run", "pytest", "--collect-only", "-q", "--no-header"],
        cwd=project_root,
    )

    # Only warn if returncode is non-zero AND we got no tests
    # (Some collection errors don't prevent collecting other tests)
    if result.returncode != 0 and not result.stdout.strip():
        logger.warning(f"pytest collection failed: {result.stderr[:STDERR_TRUNCATE_LENGTH]}")

    tests_by_file: dict[str, list[str]] = {}
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if "::" in line and not line.startswith(" "):
            # Parse node ID: file.py::TestClass::test_method
            file_path = line.split("::")[0]
            if file_path not in tests_by_file:
                tests_by_file[file_path] = []
            tests_by_file[file_path].append(line)

    return tests_by_file


def _get_first_line(docstring: str | None) -> str | None:
    """Get the first line of a docstring, or None if empty."""
    if not docstring:
        return None
    first_line = docstring.strip().split("\n")[0].strip()
    return first_line if first_line else None


def parse_test_docstrings(file_path: Path) -> dict[str, tuple[str | None, str | None]]:
    """Parse docstrings from a test file using AST.

    Returns dict mapping "ClassName::method_name" to (class_doc, method_doc).
    For module-level functions, key is "::method_name".
    """
    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return {}

    docstrings: dict[str, tuple[str | None, str | None]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_doc = _get_first_line(ast.get_docstring(node))
            for item in node.body:
                # Check for both sync and async test methods
                if isinstance(
                    item, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and item.name.startswith("test"):
                    method_doc = _get_first_line(ast.get_docstring(item))
                    key = f"{node.name}::{item.name}"
                    docstrings[key] = (class_doc, method_doc)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
            "test"
        ):
            # Module-level test function (check it's at module level)
            if node.col_offset == 0:
                method_doc = _get_first_line(ast.get_docstring(node))
                docstrings[f"::{node.name}"] = (None, method_doc)

    return docstrings


def find_test_packages(project_root: Path, exclude_dirs: list[Path] | None = None) -> list[Path]:
    """Find all tests/ package directories in the project.

    Excludes .venv directories, common package exclusions, and any directories
    in exclude_dirs (e.g., nested workspace projects).

    Returns paths to where pytest_index.toml files should be created.
    """
    exclude_dirs = exclude_dirs or []
    index_paths = []
    for init_path in project_root.rglob("tests/__init__.py"):
        # Skip virtual environments and common exclusions
        parts = init_path.parts
        if ".venv" in parts or "node_modules" in parts:
            continue
        if "site-packages" in parts:
            continue
        # Skip paths under excluded directories
        skip = False
        for exclude_dir in exclude_dirs:
            try:
                init_path.relative_to(exclude_dir)
                skip = True
                break
            except ValueError:
                pass  # Not under this exclude_dir
        if skip:
            continue
        # Return path to pytest_index.toml in this package
        index_paths.append(init_path.parent / INDEX_FILENAME)
    return sorted(index_paths)


def build_test_items(
    project_root: Path,
    tests_by_file: dict[str, list[str]],
) -> list[CollectedTest]:
    """Build CollectedTest objects from collected tests with parsed docstrings."""
    test_items: list[CollectedTest] = []

    for file_path_str, node_ids in tests_by_file.items():
        file_path = project_root / file_path_str
        if not file_path.exists():
            continue

        docstrings = parse_test_docstrings(file_path)

        for node_id in node_ids:
            parts = node_id.split("::")
            if len(parts) == 3:
                # file.py::TestClass::test_method
                class_name = parts[1]
                method_name = parts[2]
                # Handle parametrized tests: strip [param] suffix
                if "[" in method_name:
                    method_name = method_name.split("[")[0]
                doc_key = f"{class_name}::{method_name}"
            elif len(parts) == 2:
                # file.py::test_function
                class_name = None
                method_name = parts[1]
                if "[" in method_name:
                    method_name = method_name.split("[")[0]
                doc_key = f"::{method_name}"
            else:
                continue

            class_doc, method_doc = docstrings.get(doc_key, (None, None))
            test_items.append(
                CollectedTest(
                    node_id=node_id,
                    file_path=file_path,
                    class_name=class_name,
                    method_name=method_name,
                    class_doc=class_doc,
                    method_doc=method_doc,
                )
            )

    return test_items


def group_tests_by_package(
    index_paths: list[Path],
    test_items: list[CollectedTest],
) -> list[PackageTestIndex]:
    """Group tests by their containing test package."""
    package_indexes: list[PackageTestIndex] = []

    for index_path in index_paths:
        package_path = index_path.parent
        # Find tests that belong to this package
        package_tests = [
            test
            for test in test_items
            if package_path in test.file_path.parents or test.file_path.parent == package_path
        ]
        if package_tests:
            package_indexes.append(
                PackageTestIndex(
                    index_path=index_path,
                    package_path=package_path,
                    tests=package_tests,
                )
            )

    return package_indexes


def build_test_index_data(package_index: PackageTestIndex) -> dict:
    """Build test index data structure for TOML output.

    Returns a dict with structure:
    {
        "tests": {
            "TestClassName": {
                "_doc": "Class docstring",
                "test_method_name": "Method docstring",
            },
            "_module": {
                "test_function": "Function docstring",
            }
        }
    }
    """
    # Group tests by class, then by method (dedup parametrized)
    tests_by_class: dict[str | None, dict[str, CollectedTest]] = {}
    for test in package_index.tests:
        if test.class_name not in tests_by_class:
            tests_by_class[test.class_name] = {}
        # Use method name as key to dedup parametrized tests
        if test.method_name not in tests_by_class[test.class_name]:
            tests_by_class[test.class_name][test.method_name] = test

    # Build data structure
    tests_data: dict[str, dict[str, str]] = {}

    # Process classes in sorted order
    for class_name in sorted(tests_by_class.keys(), key=lambda x: x or ""):
        methods = tests_by_class[class_name]
        if class_name:
            # Get class docstring from first test in class
            first_test = next(iter(methods.values()))
            class_entry: dict[str, str] = {}
            if first_test.class_doc:
                class_entry["_doc"] = first_test.class_doc
            # Add methods in sorted order
            for method_name in sorted(methods.keys()):
                test = methods[method_name]
                class_entry[method_name] = test.method_doc or ""
            tests_data[class_name] = class_entry
        else:
            # Module-level functions go under "_module"
            module_entry: dict[str, str] = {}
            for method_name in sorted(methods.keys()):
                test = methods[method_name]
                module_entry[method_name] = test.method_doc or ""
            if module_entry:
                tests_data["_module"] = module_entry

    return {"tests": tests_data}


def write_toml_index(index_path: Path, data: dict) -> bool:
    """Write test index to TOML file.

    Creates or updates the pytest_index.toml file with the provided data.
    Uses file locking to prevent concurrent write corruption.
    Returns True if file was created or modified.
    """
    # Generate TOML content with header comment
    header = "# Generated tests index. To regenerate: djb index tests\n\n"
    toml_content = header + dump_toml(data)

    with file_lock(index_path):
        # Check if file exists and content is the same
        if index_path.exists():
            existing_content = index_path.read_text()
            if toml_content == existing_content:
                return False

        atomic_write(index_path, toml_content)
        return True


def compute_text_similarity(text1: str, text2: str) -> float:
    """Compute similarity between two text strings using SequenceMatcher.

    Returns similarity ratio between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def find_similar_tests(
    yaml_data: dict,
    min_similarity: float = 0.8,
    start: int = 0,
    limit: int | None = None,
) -> tuple[int, list[SimilarTestPair]]:
    """Find tests with similar docstrings, with pagination.

    Compares all tests within and across classes.
    Returns (total_count, page_of_pairs) - no sorting since all pairs
    above threshold need review regardless of exact similarity.
    """
    # Collect all test docstrings with their full names
    all_tests: list[tuple[str, str]] = []

    for class_name, class_data in yaml_data.items():
        if not isinstance(class_data, dict):
            continue
        for key, value in class_data.items():
            if key == "_doc":
                continue
            if isinstance(value, str) and value:
                test_name = f"{class_name}::{key}" if class_name != "_module" else key
                all_tests.append((test_name, value))

    # Compare pairs, collecting only those in page range
    similar_pairs = []
    total = 0
    for i, (name1, doc1) in enumerate(all_tests):
        for name2, doc2 in all_tests[i + 1 :]:
            similarity = compute_text_similarity(doc1, doc2)
            if similarity >= min_similarity:
                total += 1
                # Only collect if in our page range
                if total > start and (limit is None or len(similar_pairs) < limit):
                    similar_pairs.append(
                        SimilarTestPair(
                            test1=name1,
                            test2=name2,
                            doc1=doc1,
                            doc2=doc2,
                            similarity=similarity,
                        )
                    )

    return total, similar_pairs


def parse_index_from_toml(index_path: Path) -> dict | None:
    """Parse the test index from a TOML file.

    Returns the parsed data with "tests" key, or None if file doesn't exist.
    """
    if not index_path.exists():
        return None

    try:
        content = index_path.read_text()
        return parse_toml(content)
    except (OSError, ParseError):
        return None


def get_projects_to_index(config) -> list[Path]:
    """Get list of project directories to index.

    Returns host project and djb if editable.
    """
    project_root = config.project_dir
    projects = [project_root]

    if is_djb_editable(project_root):
        djb_source = get_djb_source_path(project_root)
        if djb_source:
            djb_path = (project_root / djb_source).resolve()
            if djb_path.exists():
                projects.insert(0, djb_path)  # Index djb first

    return projects


@click.command("tests")
@click.option(
    "--check-unique",
    is_flag=True,
    help="Find tests with similar descriptions (potential duplicates).",
)
@click.option(
    "--min-similarity",
    type=float,
    default=0.8,
    show_default=True,
    help="Minimum similarity threshold for --check-unique (0.0-1.0).",
)
@click.option(
    "--start",
    type=int,
    default=0,
    help="Skip first N pairs (for --check-unique pagination).",
)
@click.option(
    "--limit",
    type=int,
    default=20,
    show_default=True,
    help="Show at most N pairs (for --check-unique pagination).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be changed without modifying files.",
)
@djb_pass_context
def tests_cmd(
    cli_ctx: CliContext,
    check_unique: bool,
    min_similarity: float,
    start: int,
    limit: int,
    dry_run: bool,
):
    """Generate test package indexes.

    Discovers tests using pytest, parses their docstrings, and generates
    a TOML-formatted index file (pytest_index.toml) in each test package.

    The index helps document test coverage and can be regenerated at any time.

    \b
    Examples:
        djb index tests              # Generate indexes
        djb index tests --dry-run    # Preview changes
        djb index tests --check-unique    # Find similar tests
    """
    config = cli_ctx.config
    projects = get_projects_to_index(config)

    # For check modes, collect tests from source to ensure we check current state
    if check_unique:
        all_test_data: dict = {}
        for proj_root in projects:
            # Collect tests via pytest
            tests_by_file = collect_tests(cli_ctx.runner, proj_root)
            if not tests_by_file:
                continue

            # Parse docstrings and build test items
            test_items = build_test_items(proj_root, tests_by_file)

            # Find test packages and group tests
            index_paths = find_test_packages(proj_root)
            package_indexes = group_tests_by_package(index_paths, test_items)

            # Build test data from each package
            for pkg_idx in package_indexes:
                index_data = build_test_index_data(pkg_idx)
                if "tests" in index_data:
                    # Prefix with relative path for uniqueness
                    rel_path = pkg_idx.index_path.relative_to(proj_root)
                    for key, value in index_data["tests"].items():
                        prefixed_key = f"{rel_path.parent}::{key}"
                        all_test_data[prefixed_key] = value

        if not all_test_data:
            logger.warning("No tests found in the project.")
            return

        if check_unique:
            total, page = find_similar_tests(all_test_data, min_similarity, start, limit)
            if page:
                end_idx = start + len(page)
                logger.warning(
                    f"Found {total} pairs with similar descriptions (showing {start + 1}-{end_idx}):"
                )
                for pair in page:
                    logger.info(f"  {pair.similarity:.0%} similar:")
                    logger.info(f"    {pair.test1}")
                    logger.info(f'      "{pair.doc1}"')
                    logger.info(f"    {pair.test2}")
                    logger.info(f'      "{pair.doc2}"')
            else:
                logger.done("No tests with similar descriptions found")

        return

    # Generate indexes
    # Track processed directories to exclude from subsequent projects
    processed_dirs: list[Path] = []

    for proj_root in projects:
        logger.info(f"Collecting tests from {proj_root.name}...")

        # Collect tests via pytest
        tests_by_file = collect_tests(cli_ctx.runner, proj_root)
        if not tests_by_file:
            logger.info(f"  No tests found in {proj_root.name}")
            processed_dirs.append(proj_root)
            continue

        # Parse docstrings and build test items
        test_items = build_test_items(proj_root, tests_by_file)

        # Find test packages, excluding already-processed directories
        index_paths = find_test_packages(proj_root, exclude_dirs=processed_dirs)

        # Build package indexes
        package_indexes = group_tests_by_package(index_paths, test_items)

        # Mark this project as processed
        processed_dirs.append(proj_root)

        # Update files
        updated_count = 0
        for pkg_idx in package_indexes:
            index_data = build_test_index_data(pkg_idx)
            if dry_run:
                rel_path = pkg_idx.index_path.relative_to(proj_root)
                logger.info(f"  Would update: {rel_path}")
            else:
                if write_toml_index(pkg_idx.index_path, index_data):
                    rel_path = pkg_idx.index_path.relative_to(proj_root)
                    logger.done(f"  Updated: {rel_path}")
                    updated_count += 1

        if not dry_run:
            logger.info(f"  Updated {updated_count} test package indexes")
