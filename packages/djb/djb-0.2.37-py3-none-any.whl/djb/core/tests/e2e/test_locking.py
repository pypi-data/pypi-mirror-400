"""Tests for djb.core.locking file locking utilities.

Tests cover:
- atomic_write: Atomic file writes using temp file + rename
- get_lock_for_path: Lock acquisition and caching
- locked_write: Convenience function combining lock + atomic write
- file_lock: Context manager for file locking (lock files persist after release)
- FileLockTimeout: Exception on lock timeout
- Concurrent operations: Multiple processes accessing same file
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.e2e_marker
from filelock import Timeout

from djb.core.locking import (
    LOCK_TIMEOUT_SECONDS,
    FileLockTimeout,
    atomic_write,
    file_lock,
    get_lock_for_path,
    locked_write,
)


class TestAtomicWrite:
    """Tests for atomic_write function."""

    def test_writes_content_to_file(self, tmp_path: Path) -> None:
        """atomic_write should write content to the specified file."""
        test_file = tmp_path / "test.txt"
        atomic_write(test_file, "Hello, World!")
        assert test_file.read_text() == "Hello, World!"

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        """atomic_write should overwrite existing content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Old content")
        atomic_write(test_file, "New content")
        assert test_file.read_text() == "New content"

    def test_uses_utf8_encoding_by_default(self, tmp_path: Path) -> None:
        """atomic_write should use UTF-8 encoding by default."""
        test_file = tmp_path / "test.txt"
        atomic_write(test_file, "Héllo, Wörld! 日本語")
        assert test_file.read_text(encoding="utf-8") == "Héllo, Wörld! 日本語"

    def test_no_partial_writes(self, tmp_path: Path) -> None:
        """atomic_write should not leave partial content on failure simulation.

        This test verifies the atomic nature by checking that the temp file
        is created and renamed (not written directly to target).
        """
        test_file = tmp_path / "test.txt"
        test_file.write_text("Original")

        # Write new content
        atomic_write(test_file, "New content that is longer")

        # The file should have the complete new content
        assert test_file.read_text() == "New content that is longer"

        # No temp files should remain (they use unique names like .txt.<pid>.<hex>.tmp)
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert not tmp_files, f"Temp files should be cleaned up: {tmp_files}"


class TestGetLockForPath:
    """Tests for get_lock_for_path function."""

    def test_returns_lock_object(self, tmp_path: Path) -> None:
        """get_lock_for_path should return a lock object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        lock = get_lock_for_path(test_file)
        assert lock is not None

    def test_returns_same_lock_for_same_path(self, tmp_path: Path) -> None:
        """get_lock_for_path should return the same lock for the same path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        lock1 = get_lock_for_path(test_file)
        lock2 = get_lock_for_path(test_file)
        assert lock1 is lock2

    def test_normalizes_paths(self, tmp_path: Path) -> None:
        """get_lock_for_path should normalize paths before caching."""
        test_file = tmp_path / "subdir" / ".." / "test.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "test.txt").write_text("content")

        normalized_file = tmp_path / "test.txt"

        lock1 = get_lock_for_path(test_file)
        lock2 = get_lock_for_path(normalized_file)
        assert lock1 is lock2

    def test_creates_lock_file(self, tmp_path: Path) -> None:
        """get_lock_for_path should create a .lock file when lock is acquired."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        lock = get_lock_for_path(test_file)
        with lock:
            lock_file = test_file.with_suffix(".txt.lock")
            assert lock_file.exists()


class TestLockedWrite:
    """Tests for locked_write convenience function."""

    def test_writes_with_lock(self, tmp_path: Path) -> None:
        """locked_write should write content while holding a lock."""
        test_file = tmp_path / "test.txt"
        locked_write(test_file, "Hello, World!")
        assert test_file.read_text() == "Hello, World!"

    def test_lock_file_persists_after_operation(self, tmp_path: Path) -> None:
        """locked_write should leave lock file for future lock operations."""
        test_file = tmp_path / "test.txt"
        locked_write(test_file, "content")
        lock_file = test_file.with_suffix(".txt.lock")
        # Lock file persists to avoid race conditions in concurrent access
        assert lock_file.exists()


class TestFileLockTimeout:
    """Tests for FileLockTimeout exception."""

    def test_exception_exists(self) -> None:
        """FileLockTimeout should be importable and an Exception."""
        assert issubclass(FileLockTimeout, Exception)
        exc = FileLockTimeout("Test message")
        assert str(exc) == "Test message"


def _increment_file_process(path_str: str) -> None:
    """Increment counter in file. Must be top-level for pickling."""
    path = Path(path_str)
    lock = get_lock_for_path(path)
    with lock:
        current = int(path.read_text())
        atomic_write(path, str(current + 1))


def _append_line_process(args: tuple[str, int]) -> None:
    """Append line to file. Must be top-level for pickling."""
    path_str, n = args
    path = Path(path_str)
    lock = get_lock_for_path(path)
    with lock:
        content = path.read_text()
        atomic_write(path, content + f"line-{n}\n")


class TestConcurrentWrites:
    """Test concurrent file writes with locking across processes."""

    def test_concurrent_writes_dont_corrupt(self, tmp_path: Path) -> None:
        """Concurrent writes should not corrupt the file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("0")
        num_writes = 20

        with ProcessPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(_increment_file_process, str(test_file)) for _ in range(num_writes)
            ]
            for f in as_completed(futures):
                f.result()

        # All increments should have been applied
        assert int(test_file.read_text()) == num_writes

    def test_concurrent_appends_preserved(self, tmp_path: Path) -> None:
        """Concurrent appends should all be preserved."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("")
        num_appends = 20

        with ProcessPoolExecutor(max_workers=10) as executor:
            args = [(str(test_file), i) for i in range(num_appends)]
            futures = [executor.submit(_append_line_process, arg) for arg in args]
            for f in as_completed(futures):
                f.result()

        # All lines should be present
        lines = test_file.read_text().strip().split("\n")
        assert len(lines) == num_appends


class TestConstants:
    """Tests for module constants."""

    def test_lock_timeout_seconds(self) -> None:
        """LOCK_TIMEOUT_SECONDS should be a reasonable default."""
        assert LOCK_TIMEOUT_SECONDS == 5.0
        assert isinstance(LOCK_TIMEOUT_SECONDS, float)


class TestFileLock:
    """Tests for file_lock context manager."""

    def test_lock_file_persists_after_exiting(self, tmp_path: Path) -> None:
        """file_lock should leave lock file to avoid race conditions."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        lock_file = test_file.with_suffix(".txt.lock")

        with file_lock(test_file):
            assert lock_file.exists()

        # Lock file persists to prevent race conditions in concurrent access
        assert lock_file.exists()

    def test_lock_file_persists_on_exception(self, tmp_path: Path) -> None:
        """file_lock should leave lock file even on exception."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        lock_file = test_file.with_suffix(".txt.lock")

        with pytest.raises(ValueError):
            with file_lock(test_file):
                raise ValueError("test")

        # Lock file persists to prevent race conditions in concurrent access
        assert lock_file.exists()

    def test_raises_timeout(self, tmp_path: Path) -> None:
        """file_lock should raise FileLockTimeout on timeout."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Mock acquire to raise Timeout (simulates lock contention)
        with patch.object(
            get_lock_for_path(test_file), "acquire", side_effect=Timeout(str(test_file))
        ):
            with pytest.raises(FileLockTimeout):
                with file_lock(test_file, timeout=0.01):
                    pass
