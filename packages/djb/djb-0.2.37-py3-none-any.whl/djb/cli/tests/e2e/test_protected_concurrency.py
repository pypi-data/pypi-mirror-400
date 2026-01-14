"""Concurrency tests for file locking mechanisms.

Tests verify that file locking serializes access when multiple threads
attempt to access shared resources simultaneously. This prevents race
conditions that could corrupt files during concurrent operations.

Design notes:
- Uses fcntl.LOCK_EX for exclusive locking (djb.core.locking)
- Python's GIL does not protect file operations; file locking is required
- These tests use real files because mock_filesystem can't test file locking
- protected_age_key can only be called from main thread (signal handler limitation)
  so we test the underlying file locking mechanism directly instead

Signal handler limitation:
The protected_age_key context manager registers signal handlers for SIGINT/SIGTERM
cleanup, which can only be done from the main thread. Therefore, multi-threaded
tests must test the underlying file locking mechanism directly rather than
the protected_age_key context manager itself.
"""

from __future__ import annotations

import fcntl
import os
import sys
import threading
import time
from pathlib import Path

import pytest

from djb.core.cmd_runner import CmdRunner
from djb.secrets.protected import protected_age_key

pytestmark = pytest.mark.e2e_marker


# Skip on Windows since fcntl is not available
@pytest.mark.skipif(sys.platform == "win32", reason="fcntl not available on Windows")
class TestConcurrentFileLocking:
    """Test concurrent file locking behavior.

    These tests verify that fcntl.LOCK_EX file locking serializes
    access when multiple threads attempt to lock the same file.
    This is the underlying mechanism used by protected_age_key.

    Note: protected_age_key cannot be tested directly with threads
    because it registers signal handlers, which only work in the
    main thread. These tests verify the locking behavior directly.
    """

    @pytest.fixture
    def lock_file_setup(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create a test directory with a lock file and data file.

        Returns:
            Tuple of (lock_path, data_path).
        """
        lock_path = tmp_path / "test.lock"
        data_path = tmp_path / "data.txt"
        data_path.write_text("initial content")
        return lock_path, data_path

    def test_concurrent_access_serialized(self, lock_file_setup: tuple[Path, Path]) -> None:
        """Concurrent access with file locking serializes execution.

        Multiple threads acquiring the same lock should execute serially,
        not overlapping, because the lock prevents concurrent access.
        This test verifies that execution times don't overlap.

        Uses fcntl.LOCK_EX (exclusive lock) - same mechanism as protected_age_key.
        """
        lock_path, data_path = lock_file_setup
        access_times: list[tuple[float, float]] = []
        times_lock = threading.Lock()
        hold_duration = 0.1  # 100ms - long enough to detect overlap

        def access_with_lock(n: int) -> None:
            # Create/open lock file and acquire exclusive lock
            lock_fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX)  # Blocking exclusive lock
                start = time.time()

                # Simulate work while holding lock
                content = data_path.read_text()
                assert "content" in content, f"Thread {n}: Data corrupted"
                time.sleep(hold_duration)

                end = time.time()
                fcntl.flock(lock_fd, fcntl.LOCK_UN)  # Release lock
            finally:
                os.close(lock_fd)

            with times_lock:
                access_times.append((start, end))

        # Launch 3 threads concurrently
        threads = [threading.Thread(target=access_with_lock, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify non-overlapping execution (serialization)
        # Sort by start time to check sequential order
        sorted_times = sorted(access_times, key=lambda x: x[0])
        for i in range(len(sorted_times) - 1):
            current_end = sorted_times[i][1]
            next_start = sorted_times[i + 1][0]
            # Allow small tolerance for timing imprecision
            assert current_end <= next_start + 0.01, (
                f"Accesses should not overlap: thread {i} ended at {current_end:.3f}, "
                f"thread {i+1} started at {next_start:.3f}"
            )

    def test_concurrent_writes_no_corruption(self, lock_file_setup: tuple[Path, Path]) -> None:
        """Concurrent writes with locking shouldn't corrupt the file.

        Multiple threads writing to a file with proper locking should
        not corrupt the file contents. After all threads complete, the
        file should contain valid content.

        This verifies the locking mechanism used by protected_age_key.
        """
        lock_path, data_path = lock_file_setup
        errors: list[Exception] = []
        errors_lock = threading.Lock()

        def write_with_lock(n: int) -> None:
            try:
                lock_fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX)

                    # Read, modify, write
                    content = data_path.read_text()
                    data_path.write_text(f"thread-{n}: {content}")
                    time.sleep(0.01)  # Brief hold

                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                finally:
                    os.close(lock_fd)
            except Exception as e:
                with errors_lock:
                    errors.append(e)

        # Launch 5 threads for higher contention
        threads = [threading.Thread(target=write_with_lock, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should have occurred
        assert not errors, f"Errors during concurrent access: {errors}"

        # File should still be valid (not corrupted)
        final_content = data_path.read_text()
        assert "content" in final_content, "Data file corrupted after concurrent writes"

    def test_lock_prevents_simultaneous_access(self, lock_file_setup: tuple[Path, Path]) -> None:
        """When one thread holds the lock, others wait.

        This test verifies the blocking behavior of the lock: when one thread
        holds the lock, another thread attempting to acquire it will block
        until the first thread releases it.

        Uses coordination events to ensure thread 2 starts while thread 1
        holds the lock.
        """
        lock_path, _data_path = lock_file_setup
        hold_duration = 0.2  # 200ms
        results: dict[int, tuple[float, float]] = {}
        results_lock = threading.Lock()

        # Use an event to coordinate: thread 1 signals when it has the lock
        lock_acquired = threading.Event()

        def access_first() -> None:
            """First thread: acquire lock, signal, hold, release."""
            lock_fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                start = time.time()
                lock_acquired.set()  # Signal that we have the lock
                time.sleep(hold_duration)
                end = time.time()
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)

            with results_lock:
                results[1] = (start, end)

        def access_second() -> None:
            """Second thread: wait for first to acquire, then try to acquire."""
            lock_acquired.wait(timeout=5.0)  # Wait until first has the lock
            time.sleep(0.02)  # Small delay to ensure we try after lock is held

            lock_fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
            try:
                # This should block until thread 1 releases
                start = time.time()
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
                end = time.time()
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)

            with results_lock:
                results[2] = (start, end)

        thread1 = threading.Thread(target=access_first)
        thread2 = threading.Thread(target=access_second)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Thread 2 should have acquired the lock after thread 1 finished
        assert 1 in results and 2 in results, "Both threads should complete"
        t1_end = results[1][1]
        t2_end = results[2][1]

        # Thread 2's lock acquisition should complete after thread 1 releases
        assert t2_end >= t1_end - 0.01, (
            f"Thread 2 should block until thread 1 releases lock. "
            f"Thread 1 ended at {t1_end:.3f}, thread 2 ended at {t2_end:.3f}"
        )


class TestProtectedAgeKeyMainThread:
    """Tests for protected_age_key that run in the main thread.

    These tests verify protected_age_key behavior from the main thread
    where signal handlers can be registered. Concurrency is tested using
    the simpler file locking tests above.
    """

    @pytest.fixture
    def age_key_setup(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create a project directory with a plaintext age key.

        The key is left unprotected (no GPG encryption) to simplify testing.
        This simulates the scenario where GPG is not installed or the key
        was just generated.

        Returns:
            Tuple of (project_dir, key_path).
        """
        project_dir = tmp_path / "test-project"
        age_dir = project_dir / ".age"
        age_dir.mkdir(parents=True)

        key_path = age_dir / "keys.txt"
        # Create a realistic-looking age private key (test-only, not secure)
        key_content = """\
# created: 2024-01-01T00:00:00Z
# public key: age1testpublickey12345678901234567890123456789012345678901234
AGE-SECRET-KEY-1TESTSECRETKEY1234567890123456789012345678901234567890123456
"""
        key_path.write_text(key_content)

        return project_dir, key_path

    def test_protected_age_key_basic_access(
        self, age_key_setup: tuple[Path, Path], make_cmd_runner: CmdRunner
    ) -> None:
        """protected_age_key provides access to plaintext key.

        Basic test that the context manager works correctly for
        single-threaded access.
        """
        project_dir, key_path = age_key_setup
        original_content = key_path.read_text()

        with protected_age_key(project_dir, make_cmd_runner) as key:
            content = key.read_text()
            assert "AGE-SECRET-KEY-" in content
            assert content == original_content

    def test_protected_age_key_creates_lock_file(
        self, age_key_setup: tuple[Path, Path], make_cmd_runner: CmdRunner
    ) -> None:
        """protected_age_key creates a lock file in .age directory.

        The lock file is used to coordinate access between processes/threads.
        """
        project_dir, key_path = age_key_setup
        lock_path = key_path.parent / ".age.lock"

        # Lock file doesn't exist before access
        assert not lock_path.exists()

        with protected_age_key(project_dir, make_cmd_runner):
            # Lock file should exist during access
            assert lock_path.exists()

        # Lock file remains after access (but is unlocked)
        assert lock_path.exists()
