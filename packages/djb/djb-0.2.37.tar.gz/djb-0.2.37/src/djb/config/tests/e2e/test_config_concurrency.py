"""Concurrency tests for get_djb_config.

Tests verify that multiple threads calling get_djb_config() concurrently
all receive valid config instances with consistent values.

Design notes:
- Each get_djb_config() call returns a fresh instance
- Concurrent calls should all succeed without interference
- These tests verify correct behavior under concurrency

Threading notes:
- CPython's GIL provides protection for simple operations
- These tests verify current behavior works correctly under concurrency
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from djb.config import DjbConfig, get_djb_config
from djb.types import Mode

pytestmark = pytest.mark.e2e_marker


class TestConcurrentConfigLoading:
    """Test concurrent access to get_djb_config.

    These tests verify that config loading behaves correctly when
    called from multiple threads simultaneously.
    """

    def test_concurrent_calls_return_distinct_instances(
        self, make_pyproject_dir_with_git: Path
    ) -> None:
        """Each concurrent call gets a fresh config instance.

        Each get_djb_config call creates a new config instance.
        This test verifies that concurrent calls all get distinct
        (but equivalent) instances.
        """
        configs: list[DjbConfig] = []
        configs_lock = threading.Lock()

        def get_config(n: int) -> None:
            cfg = get_djb_config(
                DjbConfig(project_dir=make_pyproject_dir_with_git),
                env={},  # Isolate from environment
            )
            with configs_lock:
                configs.append(cfg)

        # Launch 5 threads
        threads = [threading.Thread(target=get_config, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(configs) == 5, "All threads should complete"

        # Each config should be a distinct object
        config_ids = [id(cfg) for cfg in configs]
        assert len(set(config_ids)) == 5, (
            "Each get_djb_config call should create a new instance. "
            f"Got {len(set(config_ids))} unique objects instead of 5"
        )

        # But all should have the same values
        first = configs[0]
        for i, cfg in enumerate(configs[1:], start=2):
            assert (
                cfg.project_name == first.project_name
            ), f"Config {i} has different project_name: {cfg.project_name} vs {first.project_name}"
            assert (
                cfg.project_dir == first.project_dir
            ), f"Config {i} has different project_dir: {cfg.project_dir} vs {first.project_dir}"

    def test_concurrent_calls_with_different_overrides(
        self, make_pyproject_dir_with_git: Path
    ) -> None:
        """Concurrent calls with different overrides don't interfere.

        Each thread can request a config with different override values,
        and each should get its own instance with the correct values.
        """
        results: dict[int, DjbConfig] = {}
        results_lock = threading.Lock()
        modes = [Mode.DEVELOPMENT, Mode.STAGING, Mode.PRODUCTION]

        def get_config_with_mode(n: int, mode: Mode) -> None:
            cfg = get_djb_config(
                DjbConfig(project_dir=make_pyproject_dir_with_git, mode=mode),
                env={},
            )
            with results_lock:
                results[n] = cfg

        # Each thread gets a config with a different mode
        threads = [
            threading.Thread(target=get_config_with_mode, args=(i, modes[i % len(modes)]))
            for i in range(6)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 6, "All threads should complete"

        # Verify each thread got the mode it requested
        for i, cfg in results.items():
            expected_mode = modes[i % len(modes)]
            assert (
                cfg.mode == expected_mode
            ), f"Thread {i} expected mode {expected_mode}, got {cfg.mode}"


class TestConfigEdgeCases:
    """Edge case tests for get_djb_config.

    Tests document expected behavior for edge cases like empty config,
    invalid inputs, and error conditions.
    """

    def test_nonexistent_project_dir_creates_minimal_config(self, project_dir: Path) -> None:
        """get_djb_config with nonexistent project_dir still creates config.

        The config system is designed to be resilient - it falls back to
        defaults when files don't exist. This documents that behavior.

        Note: The project_name will be derived from the directory name
        when no pyproject.toml exists.
        """
        nonexistent = project_dir / "does-not-exist"

        # Should not raise - falls back to defaults
        cfg = get_djb_config(
            DjbConfig(project_dir=nonexistent),
            env={},
        )

        # Config is created with the specified project_dir
        assert cfg.project_dir == nonexistent
        # project_name is derived from directory name when no pyproject.toml
        assert cfg.project_name == "does-not-exist"

    def test_empty_env_isolates_from_system(self, make_pyproject_dir_with_git: Path) -> None:
        """Passing empty env dict isolates from system environment.

        This is important for test isolation. When env={} is passed,
        no DJB_* environment variables should affect the config.
        """
        cfg = get_djb_config(
            DjbConfig(project_dir=make_pyproject_dir_with_git),
            env={},  # Explicitly empty, ignoring system env
        )

        # Should use defaults, not environment values
        assert cfg.project_name == "test-project"
        assert cfg.project_dir == make_pyproject_dir_with_git

    def test_env_override_takes_precedence(self, make_pyproject_dir_with_git: Path) -> None:
        """Environment variables override file config.

        When env contains DJB_* variables, they should take precedence
        over values in config files.
        """
        cfg = get_djb_config(
            DjbConfig(project_dir=make_pyproject_dir_with_git),
            env={"DJB_MODE": "production"},
        )

        assert (
            cfg.mode == Mode.PRODUCTION
        ), f"DJB_MODE env var should set mode to production, got {cfg.mode}"
