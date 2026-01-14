"""
djb.cli.tests - Test utilities for djb CLI unit tests.

Unit tests use mocking instead of real file I/O. For E2E tests with real
directories, see djb.cli.tests.e2e.

Unit Test Fixtures (auto-discovered by pytest from conftest.py):
    cli_runner - Click CliRunner for invoking CLI commands
    mock_cmd_runner - Mock for CmdRunner (provides .run)
    djb_config - DjbConfig instance with fake project_dir (no real directories)
    mock_fs - Unified mock filesystem for file operations
    mock_hook_io - Mock I/O for pre-commit hook installation tests

Shared Fixtures (from djb.testing):
    pty_stdin - Creates a PTY and replaces stdin for interactive input testing

Auto-enabled fixtures (applied to all tests automatically):
    configure_logging - Initializes djb CLI logging system (session-scoped)
    mock_gpg_operations - Mocks GPG encrypt/decrypt while keeping orchestration logic

Constants:
    DJB_PYPROJECT_CONTENT - Common pyproject.toml content for testing
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
    DEFAULT_HETZNER_CONFIG - Default HetznerConfig for unit tests
    DEFAULT_HEROKU_CONFIG - Default HerokuConfig for unit tests
    DEFAULT_K8S_CONFIG - Default K8sConfig for unit tests
    DEFAULT_CLOUDFLARE_CONFIG - Default CloudflareConfig for unit tests
"""

from __future__ import annotations

# Unit test fixtures (no I/O)
from djb.testing import (
    DEFAULT_CLOUDFLARE_CONFIG,
    DEFAULT_HEROKU_CONFIG,
    DEFAULT_HETZNER_CONFIG,
    DEFAULT_K8S_CONFIG,
    DJB_PYPROJECT_CONTENT,
    FAKE_PROJECT_DIR,
    configure_logging,
    mock_fs,
    pty_stdin,
)

from .conftest import (
    cli_runner,
    djb_config,
    mock_cmd_runner,
    mock_gpg_operations,
    mock_hook_io,
)

__all__ = [
    # Constants
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    "FAKE_PROJECT_DIR",
    # Shared fixtures (from djb.testing)
    "configure_logging",
    "mock_fs",
    "pty_stdin",
    # Unit test fixtures
    "cli_runner",
    "djb_config",
    "mock_cmd_runner",
    "mock_gpg_operations",
    "mock_hook_io",
]
