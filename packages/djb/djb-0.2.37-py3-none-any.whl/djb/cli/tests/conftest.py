"""
Shared test fixtures for djb CLI **unit tests**.

See __init__.py for the full list of available fixtures and utilities.

Guidelines for Unit Tests vs E2E Tests:
========================================

Unit tests (cli/tests/*.py):
- Use `djb_config` fixture to get a DjbConfig instance (no real directories)
- Use `mock_fs` for unified file operation mocking
- NEVER use `tmp_path` directly - all file I/O should be mocked
- Prefer patching/mocking over creating real project directories

E2E tests (cli/tests/e2e/*.py):
- Use real project directories with `project_dir` fixture
- Use `make_config_file` to create .djb/local.toml and .djb/project.toml
- Use `make_pyproject_dir_with_git` for a complete project setup
- E2E fixtures are defined in cli/tests/e2e/fixtures/

Unit Test Fixtures:
    cli_runner - Click CliRunner for invoking CLI commands
    make_init_ctx - Factory for creating mock InitContext instances
    mock_cmd_runner - Mock for CmdRunner methods (provides .run)
    djb_config - DjbConfig instance with fake project_dir (no real directories)
    make_djb_config - Factory function for creating DjbConfig with custom overrides
    mock_project_with_git_repo - Mock a git repo structure (no real directories)
    mock_fs - Unified mock filesystem for file operations
    MockFilesystem - Class for mock_fs (can also be instantiated directly)

Shared Fixtures (from djb.testing):
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob
    pty_stdin - Creates a PTY and replaces stdin for interactive input testing

Auto-enabled fixtures (applied to all tests automatically):
    configure_logging - Initializes djb CLI logging system (session-scoped)
    mock_gpg_operations - Mocks GPG encrypt/decrypt while keeping orchestration logic

Constants:
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from djb.config import DjbConfig
from djb.core.logging import get_logger
from djb.secrets import GpgError

# Unit test fixtures (mocked I/O)
from djb.testing import (
    DEFAULT_CLOUDFLARE_CONFIG,
    DEFAULT_HEROKU_CONFIG,
    DEFAULT_HETZNER_CONFIG,
    DEFAULT_K8S_CONFIG,
    DJB_PYPROJECT_CONTENT,
    FAKE_PROJECT_DIR,
    MockFilesystem,
    configure_logging,
    mock_cli_ctx,
    mock_cmd_runner,
    mock_fs,
    pty_stdin,
)

# E2E fixtures (real I/O) - used by some tests that do need real I/O
from djb.testing.e2e import (
    EDITABLE_PYPROJECT_TEMPLATE,
    alice_key,
    bob_key,
    make_age_key,
    make_cli_ctx,
    make_cmd_runner,
    make_djb_config,
    make_editable_pyproject,
)
from djb.cli.init.shared import InitContext

# Re-export shared fixtures so they're available to tests in this package
__all__ = [
    # Fixtures from djb.testing.fixtures
    "configure_logging",
    "pty_stdin",
    "make_age_key",
    "make_cli_ctx",
    "mock_cli_ctx",
    "make_cmd_runner",
    "mock_cmd_runner",
    "alice_key",
    "bob_key",
    "make_djb_config",
    # Mock filesystem (unified replacement for mock_file_read, mock_file_exists, etc.)
    "MockFilesystem",
    "mock_fs",
    # Constants from djb.testing.fixtures
    "FAKE_PROJECT_DIR",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_editable_pyproject",
    # Local fixtures
    "cli_runner",
    "make_init_ctx",
    "mock_project_with_git_repo",
]

logger = get_logger(__name__)


# =============================================================================
# CLI Testing Fixtures
# =============================================================================


@pytest.fixture
def cli_runner() -> CliRunner:
    """Click CLI test runner.

    Returns a CliRunner instance for invoking Click commands
    in tests. The CliRunner captures stdout/stderr and provides
    access to exit codes and output.

    Example:
        def test_my_command(cli_runner):
            result = cli_runner.invoke(djb_cli, ["health"])
            assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture
def make_init_ctx(mock_cmd_runner):
    """Factory for creating mock InitContext instances.

    Returns a factory function that creates InitContext mocks with:
        - config.project_dir: The project directory (default: FAKE_PROJECT_DIR)
        - config.mode: The mode (default: None)
        - runner: The mock_cmd_runner fixture

    Example:
        def test_something(make_init_ctx):
            init_ctx = make_init_ctx()
            auto_commit_secrets(init_ctx.runner, init_ctx.config.project_dir, "test@example.com")
    """

    def _make(project_dir: Path = FAKE_PROJECT_DIR, mode: str | None = None) -> InitContext:
        mock_config = Mock()
        mock_config.project_dir = project_dir
        mock_config.mode = mode
        mock_init_ctx = Mock(spec=InitContext)
        mock_init_ctx.config = mock_config
        mock_init_ctx.runner = mock_cmd_runner
        return mock_init_ctx

    return _make


# =============================================================================
# Fake GPG Operations for Unit Testing
# =============================================================================
#
# These functions provide a mock GPG implementation that allows testing the
# orchestration logic in protected_age_key (signal handlers, file locking,
# state management) without requiring actual GPG operations.

# Markers for fake GPG encryption (distinct from real GPG)
_FAKE_GPG_MARKER = "-----BEGIN FAKE GPG MESSAGE-----\n"
_FAKE_GPG_END = "\n-----END FAKE GPG MESSAGE-----"


def _fake_gpg_encrypt_file(
    _runner: Any,
    input_path: Path,
    output_path: Path | None = None,
    _armor: bool = True,
    _recipient: str | None = None,
) -> Path:
    """Fake GPG encrypt: wraps content with a marker."""
    if output_path is None:
        output_path = input_path
    content = input_path.read_text()
    output_path.write_text(f"{_FAKE_GPG_MARKER}{content}{_FAKE_GPG_END}")
    return output_path


def _fake_gpg_decrypt_file(
    _runner: Any,
    input_path: Path,
    output_path: Path | None = None,
) -> str:
    """Fake GPG decrypt: unwraps marker, returns content."""
    content = input_path.read_text()
    if not content.startswith(_FAKE_GPG_MARKER):
        raise GpgError("Not fake-GPG encrypted")
    plaintext = content[len(_FAKE_GPG_MARKER) : -len(_FAKE_GPG_END)]
    if output_path:
        output_path.write_text(plaintext)
        output_path.chmod(0o600)
        return ""
    return plaintext


def _fake_is_gpg_encrypted(_runner: Any, file_path: Path) -> bool:
    """Check if file has fake GPG marker."""
    if not file_path.exists():
        return False
    return file_path.read_text().startswith(_FAKE_GPG_MARKER)


@pytest.fixture(autouse=True)
def mock_gpg_operations():
    """Mock GPG operations while keeping orchestration logic intact.

    This fixture enables testing of protected_age_key's full code path:
    - Signal handler registration
    - File locking
    - State management
    - Cleanup logic

    Only the actual GPG encrypt/decrypt calls are mocked. The orchestration
    code in protected.py still runs, unlike the old disable_gpg_protection
    fixture which skipped the entire GPG code path.

    The fake GPG operations use a distinct marker format so tests can
    distinguish fake-encrypted files from real GPG-encrypted files.
    """
    logger.debug("Mocking GPG operations for testing (keeping orchestration logic)")
    with (
        # Patch where functions are USED (protected.py imports them directly)
        patch("djb.secrets.protected.gpg_encrypt_file", side_effect=_fake_gpg_encrypt_file),
        patch("djb.secrets.protected.gpg_decrypt_file", side_effect=_fake_gpg_decrypt_file),
        patch("djb.secrets.protected.is_gpg_encrypted", side_effect=_fake_is_gpg_encrypted),
        # Mock get_default_gpg_email for recipient (needed by some code paths)
        patch("djb.secrets.gpg.get_default_gpg_email", return_value="test@example.com"),
    ):
        yield


# =============================================================================
# Unit Test Fixtures (no io)
# =============================================================================


@pytest.fixture
def djb_config(make_djb_config) -> Generator[DjbConfig, None, None]:
    """Create a DjbConfig for unit tests - no real directories created.

    Returns a DjbConfig instance with a fake project_dir. The fixture
    automatically patches get_djb_config to return this config, so
    ctx.obj.config in CLI commands will also use it.

    For tests needing config with specific overrides (like seed_command),
    use the make_djb_config factory fixture instead.

    Example:
        def test_something(djb_config):
            assert djb_config.project_name == "test-project"
    """
    config = make_djb_config()

    with patch("djb.cli.djb.get_djb_config", return_value=config):
        yield config


@pytest.fixture
def mock_project_with_git_repo(monkeypatch):
    """Mock a git repository structure with required config.

    Uses FAKE_PROJECT_DIR and mocks file checks instead of creating real
    directories. Sets DJB_* environment variables to avoid config file I/O.
    Mocks Path.exists to return True for .git directory.

    This is the unit test sibling of make_project_with_git_repo (for E2E tests).

    Example:
        def test_something(mock_project_with_git_repo):
            # FAKE_PROJECT_DIR is returned and .git appears to exist
            assert mock_project_with_git_repo == FAKE_PROJECT_DIR
    """
    # Mock config via environment variables instead of creating files
    monkeypatch.setenv("DJB_NAME", "Test User")
    monkeypatch.setenv("DJB_EMAIL", "test@example.com")
    # Also mock Path.cwd to return FAKE_PROJECT_DIR
    monkeypatch.setattr(Path, "cwd", lambda: FAKE_PROJECT_DIR)

    # Mock .git to exist
    original_exists = Path.exists
    original_is_dir = Path.is_dir

    def mock_exists(self):
        if ".git" in str(self):
            return True
        return original_exists(self)

    def mock_is_dir(self):
        if ".git" in str(self):
            return True
        return original_is_dir(self)

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(Path, "is_dir", mock_is_dir)

    return FAKE_PROJECT_DIR


@pytest.fixture
def mock_hook_io():
    """Mock I/O for pre-commit hook installation tests.

    Provides a mock filesystem for testing install_pre_commit_hook
    without real file I/O.

    The fixture returns a SimpleNamespace with:
        - files: dict[Path, str] - Map of path to file contents
        - dirs: set[Path] - Set of directories that "exist"
        - written_files: dict[Path, str] - Files written via atomic_write
        - chmod_calls: list[tuple[Path, int]] - chmod calls made

    Example:
        def test_installs_hook(mock_hook_io):
            mock_hook_io.dirs.add(FAKE_PROJECT_DIR / ".git")
            mock_hook_io.dirs.add(FAKE_PROJECT_DIR / ".git" / "hooks")

            install_pre_commit_hook(FAKE_PROJECT_DIR, quiet=True)

            hook = FAKE_PROJECT_DIR / ".git" / "hooks" / "pre-commit"
            assert hook in mock_hook_io.written_files
    """
    state = SimpleNamespace(
        files={},  # type: dict[Path, str]
        dirs=set(),  # type: set[Path]
        written_files={},  # type: dict[Path, str]
        chmod_calls=[],  # type: list[tuple[Path, int]]
    )

    def mock_is_dir(self: Path) -> bool:
        return self in state.dirs

    def mock_exists(self: Path) -> bool:
        return self in state.files or self in state.dirs

    def mock_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
        if self in state.files:
            return state.files[self]
        raise FileNotFoundError(self)

    def mock_mkdir(self: Path, *args: Any, **kwargs: Any) -> None:
        state.dirs.add(self)

    def mock_chmod(self: Path, mode: int) -> None:
        state.chmod_calls.append((self, mode))

    def fake_atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
        state.written_files[path] = content
        state.files[path] = content  # Also update files for subsequent reads

    with (
        patch.object(Path, "is_dir", mock_is_dir),
        patch.object(Path, "exists", mock_exists),
        patch.object(Path, "read_text", mock_read_text),
        patch.object(Path, "mkdir", mock_mkdir),
        patch.object(Path, "chmod", mock_chmod),
        patch("djb.cli.editable.file_lock", return_value=nullcontext()),
        patch("djb.cli.editable.atomic_write", side_effect=fake_atomic_write),
    ):
        yield state


# DJB_PYPROJECT_CONTENT, EDITABLE_PYPROJECT_TEMPLATE, and make_editable_pyproject
# are imported from djb.testing.fixtures and re-exported via __all__
