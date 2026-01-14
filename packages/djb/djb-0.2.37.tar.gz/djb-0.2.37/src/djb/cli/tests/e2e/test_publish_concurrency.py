"""Concurrency tests for publish.py file operations.

Tests verify that file locking prevents race conditions when
multiple processes access pyproject.toml concurrently.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pytest

from djb.cli.publish import set_version
from djb.config.storage.utils import parse_toml

pytestmark = pytest.mark.e2e_marker


@pytest.fixture
def package_root(tmp_path: Path) -> Path:
    """Create a test package with pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[project]
name = "test-pkg"
version = "0.1.0"
"""
    )

    # Create _version.py in expected location
    src_dir = tmp_path / "src" / "test_pkg"
    src_dir.mkdir(parents=True)
    version_file = src_dir / "_version.py"
    version_file.write_text('__version__ = "0.1.0"\n')

    return tmp_path


def _update_version_process(args: tuple[str, str, str]) -> None:
    """Update version in a subprocess. Must be top-level for pickling."""
    path_str, pkg_name, version = args
    path = Path(path_str)
    set_version(path, pkg_name, version)


class TestConcurrentSetVersion:
    """Test concurrent version updates don't corrupt pyproject.toml."""

    def test_concurrent_version_updates_preserve_valid_toml(self, package_root: Path) -> None:
        """Concurrent version updates should not corrupt the file."""
        versions = ["0.2.0", "0.3.0", "0.4.0", "0.5.0", "0.6.0"]

        with ProcessPoolExecutor(max_workers=5) as executor:
            args = [(str(package_root), "test-pkg", v) for v in versions]
            futures = [executor.submit(_update_version_process, arg) for arg in args]
            for f in as_completed(futures):
                f.result()

        # File should be valid TOML
        pyproject = package_root / "pyproject.toml"
        content = pyproject.read_text()
        data = parse_toml(content)

        # Version should be one of the versions we set
        project = data["project"]
        assert project["version"] in versions  # type: ignore[index]  # tomlkit stub
        assert project["name"] == "test-pkg"  # type: ignore[index]  # tomlkit stub

    def test_rapid_sequential_updates(self, package_root: Path) -> None:
        """Rapid sequential updates should all complete without corruption."""
        num_updates = 10

        for i in range(num_updates):
            set_version(package_root, "test-pkg", f"0.{i}.0")

        # Final version should be the last one set
        pyproject = package_root / "pyproject.toml"
        data = parse_toml(pyproject.read_text())
        project = data["project"]
        assert project["version"] == f"0.{num_updates - 1}.0"  # type: ignore[index]  # tomlkit stub
