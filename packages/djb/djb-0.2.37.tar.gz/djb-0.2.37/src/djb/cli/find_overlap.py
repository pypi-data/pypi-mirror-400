"""Find tests with overlapping coverage for potential consolidation."""

from __future__ import annotations

import json
import tempfile
from itertools import combinations
from pathlib import Path
from typing import Final

import click

from djb.core.cmd_runner import CmdRunner

# Minimum Jaccard similarity to report overlapping tests (0.95 = 95%)
DEFAULT_MIN_SIMILARITY: Final[float] = 0.95

# Similarity threshold for identifying perfect overlaps for parametrization
PERFECT_OVERLAP_THRESHOLD: Final[float] = 0.999

# Log progress every N tests during coverage collection
COVERAGE_PROGRESS_INTERVAL: Final[int] = 50

# Maximum number of test pairs to output in detailed mode
MAX_PAIRS_OUTPUT: Final[int] = 50

from djb.cli.utils.pyproject import has_pytest_cov
from djb.core.logging import get_logger

logger = get_logger(__name__)


def collect_per_test_coverage(
    project_root: Path,
    runner: CmdRunner,
    packages: list[str] | None = None,
) -> dict[str, set[str]]:
    """Collect coverage data for each test individually.

    Args:
        project_root: Root directory of the project.
        packages: List of package paths to analyze (e.g., ["src/djb/cli"]).
                  Defaults to ["src"] if not specified.

    Returns a dict mapping test node IDs to sets of covered lines (file:line format).
    """
    if not has_pytest_cov(runner, project_root):
        raise click.ClickException("pytest-cov is required. Install with: uv add pytest-cov")

    # Default to src if no packages specified
    if not packages:
        packages = ["src"]

    # First, collect all test IDs
    result = runner.run(
        ["uv", "run", "pytest", "--collect-only", "-q"],
        cwd=project_root,
    )
    if result.returncode != 0:
        raise click.ClickException(f"Failed to collect tests: {result.stderr}")

    test_ids = [
        line.strip()
        for line in result.stdout.strip().split("\n")
        if "::" in line and not line.startswith(" ")
    ]

    logger.info(f"Collecting coverage for {len(test_ids)} tests...")
    if packages != ["src"]:
        logger.info(f"  Packages: {', '.join(packages)}")

    coverage_data: dict[str, set[str]] = {}

    # Build --cov arguments for each package
    cov_args = []
    for pkg in packages:
        cov_args.append(f"--cov={project_root / pkg}")

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, test_id in enumerate(test_ids):
            if (i + 1) % COVERAGE_PROGRESS_INTERVAL == 0:
                logger.info(f"  Progress: {i + 1}/{len(test_ids)}")

            cov_file = Path(tmpdir) / f"cov_{i}.json"
            cmd = [
                "uv",
                "run",
                "pytest",
                test_id,
                *cov_args,
                "--cov-report=json",
                f"--cov-report=json:{cov_file}",
                "-q",
                "--no-header",
            ]
            runner.run(cmd, cwd=project_root)

            if cov_file.exists():
                try:
                    with open(cov_file) as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping malformed coverage file {cov_file}: {e}")
                    continue
                covered = set()
                for filename, file_data in data.get("files", {}).items():
                    # Skip test files
                    if "test_" in filename or "conftest" in filename:
                        continue
                    for line in file_data.get("executed_lines", []):
                        covered.add(f"{filename}:{line}")
                coverage_data[test_id] = covered

    return coverage_data


def compute_jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union else 0.0


def find_overlap_candidates(
    coverage_data: dict[str, set[str]], min_similarity: float = DEFAULT_MIN_SIMILARITY
) -> list[tuple[str, str, float]]:
    """Find pairs of tests in the same class with high coverage overlap."""
    # Group tests by class
    class_tests: dict[str, list[str]] = {}
    for test_id in coverage_data:
        # Extract class name from test_id (e.g., "file.py::TestClass::test_method")
        parts = test_id.split("::")
        if len(parts) >= 2:
            class_name = parts[1] if len(parts) >= 2 else ""
            file_class = f"{parts[0]}::{class_name}"
            if file_class not in class_tests:
                class_tests[file_class] = []
            class_tests[file_class].append(test_id)

    # Find high-overlap pairs within each class
    high_overlap: list[tuple[str, str, float]] = []
    for class_name, tests in class_tests.items():
        if len(tests) < 2:
            continue
        for t1, t2 in combinations(tests, 2):
            cov1 = coverage_data.get(t1, set())
            cov2 = coverage_data.get(t2, set())
            similarity = compute_jaccard_similarity(cov1, cov2)
            if similarity >= min_similarity:
                high_overlap.append((t1, t2, similarity))

    return sorted(high_overlap, key=lambda x: (-x[2], x[0]))


def group_parametrization_candidates(
    overlapping_pairs: list[tuple[str, str, float]],
) -> dict[str, list[str]]:
    """Group tests that can be parametrized together.

    Uses union-find to group tests with identical coverage.
    """
    if not overlapping_pairs:
        return {}

    # Filter to only 100% overlap pairs
    perfect_pairs = [
        (t1, t2) for t1, t2, sim in overlapping_pairs if sim >= PERFECT_OVERLAP_THRESHOLD
    ]

    # Union-find
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x: str, y: str) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for t1, t2 in perfect_pairs:
        union(t1, t2)

    # Group by root
    groups: dict[str, list[str]] = {}
    for test in parent:
        root = find(test)
        if root not in groups:
            groups[root] = []
        groups[root].append(test)

    # Only return groups with 2+ tests
    return {k: sorted(v) for k, v in groups.items() if len(v) >= 2}


def run_find_overlap(
    project_root: Path,
    runner: CmdRunner,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    show_pairs: bool = False,
    packages: list[str] | None = None,
) -> None:
    """Find tests with overlapping coverage for potential consolidation.

    Args:
        project_root: Root directory of the project.
        min_similarity: Minimum Jaccard similarity to report (0-1).
        show_pairs: If True, show all overlapping pairs instead of groups.
        packages: List of package paths to analyze (e.g., ["src/djb/cli"]).

    Collects per-test coverage data and identifies tests in the same class
    that cover the same code paths. These are candidates for consolidation
    using @pytest.mark.parametrize.
    """
    logger.info(f"Analyzing test coverage overlap in {project_root}")

    coverage_data = collect_per_test_coverage(project_root, runner, packages)
    logger.info(f"Collected coverage for {len(coverage_data)} tests")

    overlapping = find_overlap_candidates(coverage_data, min_similarity)
    logger.info(f"Found {len(overlapping)} test pairs with ≥{min_similarity:.0%} overlap")

    if show_pairs:
        logger.section("Test Pairs with High Coverage Overlap")
        for t1, t2, sim in overlapping[:MAX_PAIRS_OUTPUT]:  # Limit output
            logger.info(f"  {sim:.1%}: {t1}")
            logger.info(f"         {t2}")
            logger.info("")
        if len(overlapping) > MAX_PAIRS_OUTPUT:
            logger.info(f"  ... and {len(overlapping) - MAX_PAIRS_OUTPUT} more pairs")
    else:
        groups = group_parametrization_candidates(overlapping)

        if not groups:
            logger.info("No parametrization candidates found (need 100% overlap).")
            return

        logger.section("Parametrization Candidates")
        logger.info("Tests with 100% identical coverage that could use @pytest.mark.parametrize:")

        total_tests = 0
        for i, (_, tests) in enumerate(sorted(groups.items(), key=lambda x: -len(x[1])), 1):
            # Get the test class name
            class_name = tests[0].split("::")[1] if "::" in tests[0] else "Unknown"
            logger.info(f"{i}. {class_name} ({len(tests)} tests -> 1 parametrized):")
            for test in tests:
                method = test.split("::")[-1]
                logger.info(f"   - {method}")
            logger.info("")
            total_tests += len(tests)

        savings = total_tests - len(groups)
        logger.info(f"Total: {total_tests} tests could become {len(groups)} parametrized tests")
        logger.info(f"Potential reduction: {savings} tests")
