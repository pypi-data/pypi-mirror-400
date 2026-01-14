"""Concurrency tests for indexer.py file operations.

Tests verify that file locking prevents race conditions when
multiple processes write to the test index file concurrently.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pytest

from djb.cli.indexer import write_toml_index
from djb.config.storage.utils import parse_toml

pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def index_path(tmp_path: Path) -> Path:
    """Return path to test index file."""
    path = tmp_path / "pytest_index.toml"
    path.write_text("")  # Ensure file exists before concurrent writes
    return path


def _write_index_process(args: tuple[str, int]) -> bool:
    """Write index in a subprocess. Must be top-level for pickling."""
    path_str, n = args
    path = Path(path_str)
    data = {
        "tests": {
            f"TestClass{n}": {
                "_doc": f"Test class {n}",
                "test_method": f"Test method {n}",
            }
        }
    }
    return write_toml_index(path, data)


class TestConcurrentWriteIndex:
    """Test concurrent index file writes."""

    def test_concurrent_writes_preserve_valid_toml(self, index_path: Path) -> None:
        """Concurrent writes should not corrupt the file."""
        num_writes = 10

        with ProcessPoolExecutor(max_workers=5) as executor:
            args = [(str(index_path), i) for i in range(num_writes)]
            futures = [executor.submit(_write_index_process, arg) for arg in args]
            for f in as_completed(futures):
                f.result()

        # File should be valid TOML
        content = index_path.read_text()
        data = parse_toml(content)

        # Should have exactly one TestClass entry (the last one written)
        assert "tests" in data
        assert len(data["tests"]) == 1  # type: ignore[arg-type]  # tomlkit stub limitation

    def test_concurrent_writes_all_complete(self, index_path: Path) -> None:
        """All concurrent writes should complete without raising exceptions."""
        num_writes = 20

        with ProcessPoolExecutor(max_workers=10) as executor:
            args = [(str(index_path), i) for i in range(num_writes)]
            futures = [executor.submit(_write_index_process, arg) for arg in args]
            results = []
            for f in as_completed(futures):
                # Should not raise
                results.append(f.result())

        # All futures completed without raising - success

    def test_identical_writes_return_false(self, index_path: Path) -> None:
        """Writing identical content should return False (no change)."""
        data = {
            "tests": {
                "TestClass": {
                    "_doc": "Test class",
                    "test_method": "Test method",
                }
            }
        }

        # First write should return True
        assert write_toml_index(index_path, data) is True

        # Subsequent identical writes should return False
        assert write_toml_index(index_path, data) is False
        assert write_toml_index(index_path, data) is False

    def test_different_content_returns_true(self, index_path: Path) -> None:
        """Writing different content should return True."""
        data1 = {"tests": {"TestClass1": {"test_a": "desc"}}}
        data2 = {"tests": {"TestClass2": {"test_b": "desc"}}}

        assert write_toml_index(index_path, data1) is True
        assert write_toml_index(index_path, data2) is True
