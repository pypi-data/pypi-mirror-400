"""Unit tests for djb.cli.find_overlap module.

All tests use FAKE_PROJECT_DIR and mock file I/O operations.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import click
import pytest

from djb.cli.find_overlap import (
    collect_per_test_coverage,
    compute_jaccard_similarity,
    find_overlap_candidates,
    group_parametrization_candidates,
    has_pytest_cov,
    run_find_overlap,
)
from djb.cli.tests import FAKE_PROJECT_DIR


class TestComputeJaccardSimilarity:
    """Tests for the compute_jaccard_similarity function."""

    def test_identical_sets(self):
        """compute_jaccard_similarity returns 1.0 for identical sets."""
        set1 = {"a", "b", "c"}
        set2 = {"a", "b", "c"}
        assert compute_jaccard_similarity(set1, set2) == 1.0

    def test_disjoint_sets(self):
        """compute_jaccard_similarity returns 0.0 for disjoint sets."""
        set1 = {"a", "b", "c"}
        set2 = {"d", "e", "f"}
        assert compute_jaccard_similarity(set1, set2) == 0.0

    def test_partial_overlap(self):
        """compute_jaccard_similarity calculates correctly for partial overlap."""
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        # Intersection: {b, c} = 2
        # Union: {a, b, c, d} = 4
        assert compute_jaccard_similarity(set1, set2) == 0.5

    @pytest.mark.parametrize(
        "set1,set2",
        [
            (set(), {"a", "b", "c"}),
            ({"a", "b", "c"}, set()),
            (set(), set()),
        ],
        ids=["empty_first", "empty_second", "both_empty"],
    )
    def test_empty_set_similarity(self, set1, set2):
        """compute_jaccard_similarity returns 0.0 for empty sets."""
        assert compute_jaccard_similarity(set1, set2) == 0.0

    def test_subset_relationship(self):
        """compute_jaccard_similarity handles subset relationships correctly."""
        set1 = {"a", "b"}
        set2 = {"a", "b", "c", "d"}
        # Intersection: 2, Union: 4
        assert compute_jaccard_similarity(set1, set2) == 0.5

    def test_single_element_sets(self):
        """compute_jaccard_similarity handles single element sets correctly."""
        set1 = {"a"}
        set2 = {"a"}
        assert compute_jaccard_similarity(set1, set2) == 1.0

        set1 = {"a"}
        set2 = {"b"}
        assert compute_jaccard_similarity(set1, set2) == 0.0


class TestFindOverlapCandidates:
    """Tests for the find_overlap_candidates function."""

    def test_empty_coverage_data(self):
        """find_overlap_candidates returns empty list for empty coverage data."""
        result = find_overlap_candidates({})
        assert result == []

    def test_single_test(self):
        """find_overlap_candidates returns empty list for single test."""
        coverage = {"test.py::TestClass::test_one": {"file.py:1", "file.py:2"}}
        result = find_overlap_candidates(coverage)
        assert result == []

    def test_tests_in_different_classes(self):
        """find_overlap_candidates does not compare tests in different classes."""
        coverage = {
            "test.py::TestClassA::test_one": {"file.py:1", "file.py:2"},
            "test.py::TestClassB::test_one": {"file.py:1", "file.py:2"},
        }
        result = find_overlap_candidates(coverage, min_similarity=0.95)
        # Different classes, no overlap reported
        assert result == []

    def test_high_overlap_same_class(self):
        """find_overlap_candidates finds high overlap in same class."""
        coverage = {
            "test.py::TestClass::test_one": {"file.py:1", "file.py:2", "file.py:3"},
            "test.py::TestClass::test_two": {"file.py:1", "file.py:2", "file.py:3"},
        }
        result = find_overlap_candidates(coverage, min_similarity=0.95)
        assert len(result) == 1
        t1, t2, sim = result[0]
        assert sim == 1.0
        assert "test_one" in t1 or "test_one" in t2
        assert "test_two" in t1 or "test_two" in t2

    def test_low_overlap_filtered_out(self):
        """find_overlap_candidates filters out low overlap pairs."""
        coverage = {
            "test.py::TestClass::test_one": {"file.py:1", "file.py:2"},
            "test.py::TestClass::test_two": {"file.py:3", "file.py:4"},
        }
        result = find_overlap_candidates(coverage, min_similarity=0.5)
        # 0% overlap, filtered out
        assert result == []

    def test_similarity_threshold(self):
        """find_overlap_candidates respects min_similarity threshold."""
        coverage = {
            "test.py::TestClass::test_one": {"a", "b", "c", "d"},
            "test.py::TestClass::test_two": {"a", "b", "c", "e"},
        }
        # Similarity = 3/5 = 0.6
        result_high = find_overlap_candidates(coverage, min_similarity=0.8)
        assert len(result_high) == 0

        result_low = find_overlap_candidates(coverage, min_similarity=0.5)
        assert len(result_low) == 1

    def test_multiple_pairs_sorted(self):
        """find_overlap_candidates sorts results by similarity descending."""
        coverage = {
            "test.py::TestClass::test_a": {"1", "2", "3", "4"},
            "test.py::TestClass::test_b": {"1", "2", "3", "4"},  # 100% with test_a
            "test.py::TestClass::test_c": {"1", "2", "3", "5"},  # 75% with test_a
        }
        result = find_overlap_candidates(coverage, min_similarity=0.5)
        assert len(result) >= 1
        # First pair should have highest similarity
        if len(result) >= 2:
            assert result[0][2] >= result[1][2]

    def test_skips_tests_without_coverage_data(self):
        """find_overlap_candidates handles tests with no coverage data."""
        coverage = {
            "test.py::TestClass::test_one": set(),
            "test.py::TestClass::test_two": {"file.py:1"},
        }
        # Empty set has 0 similarity, so with min_similarity=0.0 it's included
        result = find_overlap_candidates(coverage, min_similarity=0.0)
        assert len(result) == 1
        assert result[0][2] == 0.0

        # With any positive threshold, it's filtered out
        result = find_overlap_candidates(coverage, min_similarity=0.1)
        assert result == []


class TestGroupParametrizationCandidates:
    """Tests for the group_parametrization_candidates function."""

    def test_empty_input(self):
        """group_parametrization_candidates returns empty dict for empty list."""
        result = group_parametrization_candidates([])
        assert result == {}

    def test_no_perfect_overlap(self):
        """group_parametrization_candidates ignores pairs with <100% overlap."""
        pairs = [
            ("test::A::one", "test::A::two", 0.95),
            ("test::B::one", "test::B::two", 0.90),
        ]
        result = group_parametrization_candidates(pairs)
        assert result == {}

    def test_perfect_overlap_pair(self):
        """group_parametrization_candidates groups pairs with 100% overlap."""
        pairs = [
            ("test::A::one", "test::A::two", 1.0),
        ]
        result = group_parametrization_candidates(pairs)
        assert len(result) == 1
        group = list(result.values())[0]
        assert "test::A::one" in group
        assert "test::A::two" in group

    def test_transitive_grouping(self):
        """group_parametrization_candidates groups transitive relationships."""
        pairs = [
            ("test::A::one", "test::A::two", 1.0),
            ("test::A::two", "test::A::three", 1.0),
        ]
        result = group_parametrization_candidates(pairs)
        assert len(result) == 1
        group = list(result.values())[0]
        assert len(group) == 3
        assert "test::A::one" in group
        assert "test::A::two" in group
        assert "test::A::three" in group

    def test_separate_groups(self):
        """group_parametrization_candidates creates separate groups for unrelated pairs."""
        pairs = [
            ("test::A::one", "test::A::two", 1.0),
            ("test::B::one", "test::B::two", 1.0),
        ]
        result = group_parametrization_candidates(pairs)
        assert len(result) == 2

    def test_threshold_for_perfect_overlap(self):
        """group_parametrization_candidates considers 99.9%+ overlap as perfect."""
        pairs = [
            ("test::A::one", "test::A::two", 0.999),
            ("test::B::one", "test::B::two", 0.998),  # Below threshold
        ]
        result = group_parametrization_candidates(pairs)
        assert len(result) == 1
        group = list(result.values())[0]
        assert "test::A::one" in group


class TestHasPytestCov:
    """Tests for the has_pytest_cov function."""

    @pytest.mark.parametrize(
        "check_result,expected",
        [
            (True, True),
            (False, False),
        ],
        ids=["available", "not_available"],
    )
    def test_returns_based_on_check_result(
        self, mock_cmd_runner: MagicMock, check_result, expected
    ):
        """has_pytest_cov returns True/False based on runner.check result."""
        mock_cmd_runner.check.return_value = check_result

        result = has_pytest_cov(mock_cmd_runner, FAKE_PROJECT_DIR)

        assert result is expected
        mock_cmd_runner.check.assert_called_once()


class TestCollectPerTestCoverage:
    """Tests for the collect_per_test_coverage function.

    All file I/O (TemporaryDirectory, open, json.load, Path.exists) is mocked.
    """

    def test_raises_when_pytest_cov_not_available(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage raises ClickException when pytest-cov is not available."""
        with patch("djb.cli.find_overlap.has_pytest_cov", return_value=False):
            with pytest.raises(click.ClickException) as exc_info:
                collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        assert "pytest-cov is required" in str(exc_info.value)

    def test_raises_when_test_collection_fails(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage raises ClickException when pytest --collect-only fails."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Collection error",
        )

        with patch("djb.cli.find_overlap.has_pytest_cov", return_value=True):
            with pytest.raises(click.ClickException) as exc_info:
                collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        assert "Failed to collect tests" in str(exc_info.value)

    def test_collects_coverage_for_each_test(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage collects coverage data for each test."""
        test_ids = [
            "test_module.py::TestClass::test_one",
            "test_module.py::TestClass::test_two",
        ]
        collect_output = "\n".join(test_ids) + "\n"

        # Mock coverage JSON data
        coverage_json_one = {
            "files": {
                "src/module.py": {"executed_lines": [1, 2, 3]},
                "test_module.py": {"executed_lines": [10, 20]},  # Should be skipped
            }
        }
        coverage_json_two = {
            "files": {
                "src/module.py": {"executed_lines": [1, 2, 5]},
            }
        }
        coverage_files = [coverage_json_one, coverage_json_two]
        file_index = [0]  # Mutable to track which file to return

        def run_side_effect(cmd, *args, **kwargs):
            # First call: collect test IDs
            if "--collect-only" in cmd:
                return Mock(returncode=0, stdout=collect_output, stderr="")
            # Subsequent calls: run individual tests with coverage
            return Mock(returncode=0, stdout="", stderr="")

        mock_cmd_runner.run.side_effect = run_side_effect

        # Track Path.exists calls to return True for coverage files
        original_exists = Path.exists

        def mock_exists(self):
            if "cov_" in str(self) and str(self).endswith(".json"):
                return True
            return original_exists(self)

        def mock_open(path, *args, **kwargs):
            """Return mock file context manager."""
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            return mock_file

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
            patch.object(Path, "exists", mock_exists),
            patch("builtins.open", mock_open),
            patch("djb.cli.find_overlap.json.load") as mock_json_load,
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            def json_load_side_effect(f):
                idx = file_index[0]
                file_index[0] += 1
                return coverage_files[idx]

            mock_json_load.side_effect = json_load_side_effect

            result = collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        # Verify coverage was collected
        assert len(result) == 2
        assert test_ids[0] in result
        assert test_ids[1] in result

        # Verify test files are excluded from coverage
        for test_id, covered in result.items():
            for line in covered:
                assert "test_" not in line
                assert "conftest" not in line

    def test_uses_default_packages_when_not_specified(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage uses ['src'] as default packages."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout="test.py::test_one\n",
            stderr="",
        )

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        # Check that the coverage command includes --cov=<project>/src
        calls = mock_cmd_runner.run.call_args_list
        # Find the coverage run call (not the collect-only call)
        for call in calls:
            cmd = call[0][0]
            if "--cov-report=json" in cmd:
                cov_args = [arg for arg in cmd if arg.startswith("--cov=")]
                assert len(cov_args) == 1
                assert cov_args[0].endswith("src")

    def test_uses_custom_packages_when_specified(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage uses specified packages for coverage."""
        custom_packages = ["src/djb/cli", "src/djb/core"]

        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout="test.py::test_one\n",
            stderr="",
        )

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner, packages=custom_packages)

        # Check that the coverage command includes --cov for each package
        calls = mock_cmd_runner.run.call_args_list
        for call in calls:
            cmd = call[0][0]
            if "--cov-report=json" in cmd:
                cov_args = [arg for arg in cmd if arg.startswith("--cov=")]
                assert len(cov_args) == 2

    def test_returns_empty_for_no_tests(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage handles case when no tests are collected."""
        # Return empty output (no tests)
        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout="\n",
            stderr="",
        )

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            result = collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        assert result == {}

    def test_skips_test_with_missing_coverage_file(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage handles missing coverage file for a test."""
        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout="test.py::test_one\n",
            stderr="",
        )

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
            patch.object(Path, "exists", return_value=False),
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            result = collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        # Test should not be in results since no coverage file was created
        assert "test.py::test_one" not in result

    def test_filters_tests_with_leading_spaces(self, mock_cmd_runner: MagicMock):
        """collect_per_test_coverage filters out indented lines from test collection."""
        # pytest --collect-only can output indented lines for parametrized test details
        collect_output = (
            "test.py::test_one\n"
            "  <Module test.py>\n"  # Indented lines should be filtered
            "test.py::test_two\n"
        )

        mock_cmd_runner.run.return_value = Mock(
            returncode=0,
            stdout=collect_output,
            stderr="",
        )

        # Track Path.exists calls to return True for coverage files
        original_exists = Path.exists

        def mock_exists(self):
            if "cov_" in str(self) and str(self).endswith(".json"):
                return True
            return original_exists(self)

        def mock_open(path, *args, **kwargs):
            """Return mock file context manager."""
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            return mock_file

        with (
            patch("djb.cli.find_overlap.has_pytest_cov", return_value=True),
            patch("djb.cli.find_overlap.tempfile.TemporaryDirectory") as mock_tmpdir,
            patch.object(Path, "exists", mock_exists),
            patch("builtins.open", mock_open),
            patch("djb.cli.find_overlap.json.load", return_value={"files": {}}),
        ):
            mock_tmpdir.return_value.__enter__.return_value = "/fake/tmpdir"
            mock_tmpdir.return_value.__exit__.return_value = None

            result = collect_per_test_coverage(FAKE_PROJECT_DIR, mock_cmd_runner)

        # Should have 2 tests (no indented lines)
        assert len(result) == 2


class TestRunFindOverlap:
    """Tests for the run_find_overlap function."""

    def test_calls_collect_per_test_coverage(self, mock_cmd_runner: MagicMock):
        """run_find_overlap calls collect_per_test_coverage with correct args."""
        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
            patch("djb.cli.find_overlap.group_parametrization_candidates"),
        ):
            mock_collect.return_value = {}
            mock_find.return_value = []

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner, packages=["src/djb/cli"])

        mock_collect.assert_called_once_with(FAKE_PROJECT_DIR, mock_cmd_runner, ["src/djb/cli"])

    def test_passes_min_similarity_to_find_overlap_candidates(self, mock_cmd_runner: MagicMock):
        """run_find_overlap passes min_similarity to find_overlap_candidates."""
        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
            patch("djb.cli.find_overlap.group_parametrization_candidates"),
        ):
            mock_collect.return_value = {"test::one": {"a"}}
            mock_find.return_value = []

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner, min_similarity=0.8)

        mock_find.assert_called_once()
        args, kwargs = mock_find.call_args
        assert args[1] == 0.8  # min_similarity

    def test_show_pairs_outputs_overlapping_pairs(
        self, mock_cmd_runner: MagicMock, capsys: pytest.CaptureFixture
    ):
        """run_find_overlap with show_pairs=True outputs pairs instead of groups."""
        overlapping = [
            ("test.py::TestClass::test_one", "test.py::TestClass::test_two", 0.98),
        ]

        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
            patch("djb.cli.find_overlap.group_parametrization_candidates") as mock_group,
        ):
            mock_collect.return_value = {"test::one": {"a"}}
            mock_find.return_value = overlapping

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner, show_pairs=True)

        # group_parametrization_candidates should not be called when show_pairs=True
        mock_group.assert_not_called()
        # Should output the pairs
        captured = capsys.readouterr()
        assert "test_one" in captured.out and "test_two" in captured.out

    def test_groups_mode_outputs_parametrization_candidates(
        self, mock_cmd_runner: MagicMock, capsys: pytest.CaptureFixture
    ):
        """run_find_overlap default mode outputs grouped parametrization candidates."""
        overlapping = [
            ("test.py::TestClass::test_one", "test.py::TestClass::test_two", 1.0),
        ]
        groups = {
            "test.py::TestClass::test_one": [
                "test.py::TestClass::test_one",
                "test.py::TestClass::test_two",
            ]
        }

        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
            patch("djb.cli.find_overlap.group_parametrization_candidates") as mock_group,
        ):
            mock_collect.return_value = {"test::one": {"a"}}
            mock_find.return_value = overlapping
            mock_group.return_value = groups

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner, show_pairs=False)

        mock_group.assert_called_once_with(overlapping)
        # Should output something about parametrization
        captured = capsys.readouterr()
        assert "Parametrization" in captured.out or "parametrize" in captured.out.lower()

    def test_outputs_no_candidates_message_when_groups_empty(
        self, mock_cmd_runner: MagicMock, capsys: pytest.CaptureFixture
    ):
        """run_find_overlap outputs message when no parametrization candidates found."""
        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
            patch("djb.cli.find_overlap.group_parametrization_candidates") as mock_group,
        ):
            mock_collect.return_value = {}
            mock_find.return_value = []
            mock_group.return_value = {}

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner)

        captured = capsys.readouterr()
        assert "No parametrization candidates" in captured.out

    def test_limits_output_to_50_pairs(
        self, mock_cmd_runner: MagicMock, capsys: pytest.CaptureFixture
    ):
        """run_find_overlap limits pairs output to 50 entries."""
        # Create 60 overlapping pairs
        overlapping = [
            (f"test.py::TestClass::test_{i}", f"test.py::TestClass::test_{i+1}", 0.98)
            for i in range(60)
        ]

        with (
            patch("djb.cli.find_overlap.collect_per_test_coverage") as mock_collect,
            patch("djb.cli.find_overlap.find_overlap_candidates") as mock_find,
        ):
            mock_collect.return_value = {}
            mock_find.return_value = overlapping

            run_find_overlap(FAKE_PROJECT_DIR, mock_cmd_runner, show_pairs=True)

        # Should mention "and X more pairs"
        captured = capsys.readouterr()
        assert "10 more pairs" in captured.out
