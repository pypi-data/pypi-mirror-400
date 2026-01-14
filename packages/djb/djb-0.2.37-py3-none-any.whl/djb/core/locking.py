"""Cross-platform file locking utilities.

Provides atomic read-modify-write patterns for safe concurrent file access.
Uses filelock library for cross-platform locking.

Usage:
    from djb.core.locking import get_lock_for_path, atomic_write, FileLockTimeout

    lock = get_lock_for_path(path)
    with lock:
        content = path.read_text()
        modified = process(content)
        atomic_write(path, modified)

Exports:
    FileLockTimeout - Raised when unable to acquire file lock within timeout
    get_lock_for_path - Get or create a FileLock for the given path
    atomic_write - Write content atomically using temp file + rename
    locked_write - Convenience function combining lock + atomic write
    file_lock - Context manager for file locking (lock files persist after release)
    LOCK_TIMEOUT_SECONDS - Default timeout for lock acquisition (5.0 seconds)
"""

from __future__ import annotations

import os
import secrets
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from filelock import BaseFileLock, FileLock, Timeout

# Module-level cache for lock objects (one lock per file path)
# FileLock() returns a BaseFileLock (the base class), not FileLock (the subclass)
_file_locks: dict[Path, BaseFileLock] = {}

LOCK_TIMEOUT_SECONDS = 5.0


class FileLockTimeout(Exception):
    """Raised when unable to acquire file lock within timeout."""

    pass


def get_lock_for_path(path: Path, timeout: float = LOCK_TIMEOUT_SECONDS) -> BaseFileLock:
    """Get or create a FileLock for the given path.

    Uses a module-level cache to ensure the same lock object is used
    for the same file path across all function calls.

    Args:
        path: Path to the file to lock
        timeout: Lock acquisition timeout in seconds

    Returns:
        FileLock instance for path.with_suffix(path.suffix + ".lock")
    """
    path = path.resolve()  # Normalize to absolute path
    if path not in _file_locks:
        lock_path = path.with_suffix(path.suffix + ".lock")
        _file_locks[path] = FileLock(str(lock_path), timeout=timeout)
    return _file_locks[path]


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write content atomically using temp file + rename.

    This prevents partial writes from corrupting the file. The rename
    operation is atomic on POSIX systems, so the file is either fully
    written or not changed at all.

    Uses a unique temp file name (with PID and random suffix) to avoid
    conflicts when multiple processes write concurrently.

    Args:
        path: Path to the file to write
        content: Content to write
        encoding: Text encoding to use (default: utf-8)
    """
    # Use PID and random suffix to ensure unique temp file per process
    suffix = f".{os.getpid()}.{secrets.token_hex(4)}.tmp"
    tmp_path = path.with_suffix(path.suffix + suffix)
    try:
        tmp_path.write_text(content, encoding=encoding)
        tmp_path.rename(path)  # Atomic on POSIX
    finally:
        # Clean up temp file if rename failed
        if tmp_path.exists():
            tmp_path.unlink()


def locked_write(
    path: Path, content: str, timeout: float = LOCK_TIMEOUT_SECONDS, encoding: str = "utf-8"
) -> None:
    """Write content with locking and atomic write.

    Convenience function combining lock acquisition and atomic write.
    Uses file_lock internally for cross-process synchronization.

    Args:
        path: Path to the file to write
        content: Content to write
        timeout: Lock acquisition timeout
        encoding: Text encoding to use (default: utf-8)

    Raises:
        FileLockTimeout: If lock cannot be acquired within timeout
    """
    with file_lock(path, timeout):
        atomic_write(path, content, encoding=encoding)


@contextmanager
def file_lock(path: Path, timeout: float = LOCK_TIMEOUT_SECONDS) -> Iterator[None]:
    """Context manager for file locking.

    Uses filelock for cross-process synchronization. Lock files persist after
    release to avoid race conditions when multiple processes compete for the
    same lock.

    Args:
        path: Path to the file to lock
        timeout: Lock acquisition timeout in seconds

    Yields:
        None (the lock is held for the duration of the context)

    Raises:
        FileLockTimeout: If lock cannot be acquired within timeout
    """
    path = path.resolve()
    lock = get_lock_for_path(path, timeout)

    try:
        lock.acquire()
    except Timeout:
        raise FileLockTimeout(f"Could not acquire lock for {path} within {timeout}s")

    try:
        yield
    finally:
        lock.release()
        # NOTE: Lock files are intentionally NOT deleted after release.
        # Deleting lock files creates a race condition where:
        # 1. Process A releases lock, then deletes lock file
        # 2. Process B acquires lock on existing inode
        # 3. Process A deletes the file (B's inode detaches)
        # 4. Process C creates NEW lock file with new inode
        # 5. B and C both think they have exclusive access -> lost updates
        # See: https://github.com/tox-dev/filelock/issues/31


# Re-export Timeout for use in try/except blocks
__all__ = [
    "FileLockTimeout",
    "Timeout",
    "get_lock_for_path",
    "atomic_write",
    "locked_write",
    "file_lock",
    "LOCK_TIMEOUT_SECONDS",
]
