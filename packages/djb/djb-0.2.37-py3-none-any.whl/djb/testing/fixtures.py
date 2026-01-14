"""
Shared test fixtures for djb unit tests.

This module provides reusable pytest fixtures for unit tests that mock I/O.
For E2E tests that need real I/O, use djb.testing.e2e instead.

Fixtures:
    configure_logging - Initializes djb CLI logging system (session-scoped, autouse)
    project_dir - Returns FAKE_PROJECT_DIR for unit tests (override in E2E)
    pty_stdin - Creates a PTY and temporarily replaces stdin for interactive input testing
    mock_cli_ctx - CliContext with mocked runner for unit tests
    mock_cmd_runner - Mock CmdRunner.run for unit tests
    require_docker - Skip test if Docker is not available (E2E)
    mock_fs - Unified mock filesystem for testing file operations without real I/O

Classes:
    MockFilesystem - Unified mock filesystem class (use mock_fs fixture or instantiate directly)

Functions:
    is_docker_available() - Check if Docker daemon is running

Constants:
    FAKE_PROJECT_DIR - Default fake project directory for unit tests
    DEFAULT_HETZNER_CONFIG - Default HetznerConfig for unit tests
    DEFAULT_HEROKU_CONFIG - Default HerokuConfig for unit tests
    DEFAULT_K8S_CONFIG - Default K8sConfig for unit tests
    DEFAULT_CLOUDFLARE_CONFIG - Default CloudflareConfig for unit tests
    DJB_PYPROJECT_CONTENT - Common pyproject.toml content for testing djb package

Usage:
    Import the fixtures you need in your conftest.py:

        from djb.testing.fixtures import configure_logging, pty_stdin

    For E2E tests, import from djb.testing.e2e:

        from djb.testing.e2e import cli_runner, make_djb_config
"""

from __future__ import annotations

import io
import os
import pty
import subprocess
import sys
import types
from collections.abc import Generator
from contextlib import ExitStack, contextmanager, nullcontext
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, Mock, patch

import pytest

if TYPE_CHECKING:
    pass

from djb.config import (
    CloudflareConfig,
    HerokuConfig,
    HetznerConfig,
    HetznerImage,
    HetznerLocation,
    HetznerServerType,
    K8sBackendConfig,
    K8sConfig,
)
from djb.config.storage.utils import clear_toml_cache
from djb.cli.context import CliContext
from djb.config import DjbConfig
from djb.core.cmd_runner import CmdRunner, RunResult
from djb.core.logging import setup_logging
from djb.machine_state.types import MachineContext
from djb.types import K8sClusterType, K8sProvider, Mode, Platform


# =============================================================================
# Mock Context Classes
# =============================================================================


@dataclass
class MockCliContext:
    """CliContext wrapper with properly typed mock accessors for unit tests.

    This class wraps a real CliContext and provides typed access to the
    mock methods. Use this instead of CliContext in test signatures
    to avoid type errors when accessing mock attributes.

    The `runner` attribute is the real CmdRunner (for passing to constructors),
    while `run_mock` and `check_mock` provide typed Mock access.

    Attributes:
        runner: The real CmdRunner (with mocked methods) for passing to constructors.
        config: The underlying DjbConfig.
        run_mock: Typed Mock for runner.run - use for return_value, side_effect, etc.
        check_mock: Typed Mock for runner.check.

    Example:
        def test_something(mock_cli_ctx: MockCliContext) -> None:
            # Set up mock behavior via typed accessors
            mock_cli_ctx.run_mock.return_value = Mock(returncode=0, stdout="output")
            mock_cli_ctx.run_mock.side_effect = [Mock(...), Mock(...)]

            # Pass runner to constructors (type-compatible with CmdRunner)
            provider = MyProvider(mock_cli_ctx.runner, mock_cli_ctx.config)

            # Assert on mock calls
            assert mock_cli_ctx.run_mock.call_count >= 1
    """

    runner: CmdRunner
    config: DjbConfig
    run_mock: Mock
    check_mock: Mock


# =============================================================================
# Shared Testing Fixtures
# =============================================================================


@pytest.fixture
def project_dir() -> Path:
    """Default project directory for unit tests.

    Returns FAKE_PROJECT_DIR for unit tests that mock file I/O.

    E2E tests should use the override defined in djb.testing.e2e.fixtures
    which returns tmp_path for real file I/O. Import it in your
    tests/e2e/conftest.py:

        from djb.testing.e2e.fixtures import project_dir  # noqa: F401
    """
    return FAKE_PROJECT_DIR


@pytest.fixture
def mock_cli_ctx() -> Generator[MockCliContext, None, None]:
    """Create a MockCliContext with mocked runner for unit tests.

    The runner's methods (run, check) are mocked with proper type hints.
    Use this for unit tests that should not execute real commands.

    Access mocks via typed accessors:
        - `ctx.run_mock` - Mock object for runner.run method
        - `ctx.check_mock` - Mock object for runner.check method
        - `ctx.runner` - Real CmdRunner (pass to constructors)

    Example:
        def test_something(mock_cli_ctx: MockCliContext) -> None:
            mock_cli_ctx.run_mock.return_value = Mock(returncode=0, stdout="output", stderr="")
            provider = MyProvider(mock_cli_ctx.runner, mock_cli_ctx.config)
            assert mock_cli_ctx.run_mock.call_count >= 1
    """
    cli_ctx = CliContext()
    with (
        patch.object(CmdRunner, "run") as mock_run,
        patch.object(CmdRunner, "check") as mock_check,
    ):
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_check.return_value = True
        yield MockCliContext(
            runner=cli_ctx.runner,
            config=cli_ctx.config,
            run_mock=mock_run,
            check_mock=mock_check,
        )


@pytest.fixture
def mock_cmd_runner():
    """Mock CmdRunner.run for testing CLI modules.

    Returns a namespace with .run and .check Mock objects.

    Modes:
        Full mock (default): All commands return mock results.
        Selective mock: Call mock_cmd_runner.run.only_mock(patterns) to only
            mock matching commands; non-matching commands execute for real.

    Attributes:
        run: Mock object for configuring return values and asserting calls.
        check: Mock object for the check method.

    The mock replicates real run() behavior: raises fail_msg if returncode != 0
    and fail_msg is an Exception.

    Examples::

        # Check that a command was called
        def test_calls_uv(mock_cmd_runner):
            do_something(mock_cmd_runner)
            assert mock_cmd_runner.run.call_count == 1
            assert mock_cmd_runner.run.call_args.args[0] == ["uv", "sync"]

        # Configure a failure response
        def test_handles_failure(mock_cmd_runner):
            mock_cmd_runner.run.return_value = Mock(returncode=1, stderr="error")
            result = do_something(mock_cmd_runner)
            assert result.exit_code == 1

        # Sequential return values
        def test_retry_logic(mock_cmd_runner):
            mock_cmd_runner.run.side_effect_values.extend([
                Mock(returncode=1, stderr="fail"),  # First call fails
                Mock(returncode=0, stdout="ok"),    # Retry succeeds
            ])
            assert do_something_with_retry(mock_cmd_runner) == "ok"

        # Custom side_effect function
        def test_dynamic_response(mock_cmd_runner):
            def side_effect(cmd, *args, **kwargs):
                if "heroku" in cmd[0]:
                    return Mock(returncode=0, stdout="heroku ok")
                return Mock(returncode=1, stderr="unknown")
            mock_cmd_runner.run.side_effect = side_effect

        # Selective mocking: mock heroku, run git for real
        def test_e2e_with_selective_mock(mock_cmd_runner, cli_runner):
            mock_cmd_runner.run.only_mock(["heroku"])
            result = cli_runner.invoke(cli, ["deploy"])
            assert result.exit_code == 0
    """
    # Store original for selective mode fallthrough
    original_run = CmdRunner.run

    # List for sequential return values
    side_effect_values: list[RunResult] = []

    # State for selective mode (closure variables)
    selective_patterns: list[str] | None = None
    selective_result: RunResult | None = None

    # Mock for tracking calls
    mock_run = Mock()
    mock_run.return_value = RunResult(0, "", "")
    mock_run.side_effect_values = side_effect_values

    def run_side_effect(_cmd: list[str], *_args, **kwargs) -> RunResult:
        """Side effect for direct calls to mock_cmd_runner.run(...)."""
        # Get result from sequential values or return_value
        if side_effect_values:
            result = side_effect_values.pop(0)
        else:
            result = mock_run.return_value

        # Handle fail_msg (replicate CmdRunner behavior)
        if result.returncode != 0:
            fail_msg = kwargs.get("fail_msg")
            if isinstance(fail_msg, Exception):
                raise fail_msg
        return result

    mock_run.side_effect = run_side_effect

    def only_mock(patterns: list[str], default_result: RunResult | None = None) -> None:
        """Enable selective mocking - only mock commands matching patterns."""
        nonlocal selective_patterns, selective_result
        selective_patterns = patterns
        selective_result = default_result or RunResult(0, "", "")

    # Attach only_mock method to the mock
    mock_run.only_mock = only_mock

    def patched_run(runner_self: CmdRunner, cmd: list[str], *args, **kwargs) -> RunResult:
        """Patched CmdRunner.run that delegates to mock or original."""
        nonlocal selective_patterns, selective_result
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd

        # Selective mode: check if command matches any pattern (prefix match)
        if selective_patterns is not None and selective_result is not None:
            for pattern in selective_patterns:
                if cmd_str.startswith(pattern):
                    # Match - record call and return mock result
                    mock_run(cmd, *args, **kwargs)
                    return selective_result
            # No match - call original (real execution)
            return original_run(runner_self, cmd, *args, **kwargs)

        # Full mock mode: call mock (which triggers run_side_effect)
        return mock_run(cmd, *args, **kwargs)

    mock_check = Mock()
    mock_check.return_value = True

    with (
        patch.object(CmdRunner, "run", patched_run),
        patch.object(CmdRunner, "check", mock_check),
    ):
        yield types.SimpleNamespace(run=mock_run, check=mock_check)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Configure logging for all CLI tests (session-scoped).

    This fixture runs once per test session to initialize the djb CLI
    logging system. Session scope is safe since logging is inherently
    global and idempotent.
    """
    setup_logging()


# =============================================================================
# PTY Fixtures
# =============================================================================


@pytest.fixture
def pty_stdin():
    """Fixture that creates a PTY and temporarily replaces stdin.

    This fixture properly saves and restores stdin state between tests,
    avoiding pollution that can occur with manual save/restore.

    Yields the master fd which can be written to simulate user input.

    Example:
        def test_interactive_input(pty_stdin):
            os.write(pty_stdin, b"yes\\n")
            # ... code that reads from stdin
    """
    # Create PTY pair
    master_fd, slave_fd = pty.openpty()

    # Save original stdin state
    original_stdin_fd = os.dup(0)

    # Replace stdin with slave end of PTY
    os.dup2(slave_fd, 0)
    os.close(slave_fd)  # Close original fd since we dup2ed it
    sys.stdin = os.fdopen(0, "r", closefd=False)

    yield master_fd

    # Restore original stdin
    # First, close the current sys.stdin without closing fd 0
    sys.stdin.close()
    # Restore fd 0 to original
    os.dup2(original_stdin_fd, 0)
    os.close(original_stdin_fd)
    # Recreate sys.stdin from restored fd 0
    sys.stdin = os.fdopen(0, "r", closefd=False)
    # Close master end
    os.close(master_fd)


# =============================================================================
# Docker Fixtures (E2E)
# =============================================================================


def is_docker_available() -> bool:
    """Check if Docker is available and daemon is running.

    Returns:
        True if Docker daemon is accessible, False otherwise.

    Example:
        if is_docker_available():
            # Run Docker-dependent code
            ...
    """
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture
def require_docker() -> None:
    """Skip test if Docker is not available.

    Use this fixture in E2E tests that require Docker to be running.

    Example:
        def test_build_image(require_docker, make_cmd_runner):
            # This test will be skipped if Docker is not available
            ...
    """
    if not is_docker_available():
        pytest.skip("Docker not available (install Docker or start Docker daemon)")


# =============================================================================
# Test Constants
# =============================================================================

# Default fake project directory for unit tests
FAKE_PROJECT_DIR = Path("/fake/test-project")

# Default HetznerConfig for unit tests (matches resolution defaults)
DEFAULT_HETZNER_CONFIG = HetznerConfig(
    default_server_type=HetznerServerType.CX23.value,
    default_location=HetznerLocation.NBG1.value,
    default_image=HetznerImage.UBUNTU_24_04.value,
    server_name=None,
    ssh_key_name=None,
)

# Default HerokuConfig for unit tests
DEFAULT_HEROKU_CONFIG = HerokuConfig(domain_names={})

# Default K8sConfig for unit tests
DEFAULT_K8S_BACKEND_CONFIG = K8sBackendConfig(
    managed_dockerfile=True,
    remote_build=True,
    buildpacks=["python:3.14-slim"],
    buildpack_registry="localhost:32000",
)
DEFAULT_K8S_CONFIG = K8sConfig(
    domain_names={},
    backend=DEFAULT_K8S_BACKEND_CONFIG,
    db_name="",
    cluster_name=None,
    host=None,
    no_cloudnativepg=False,
    no_tls=False,
)

# Default CloudflareConfig for unit tests
DEFAULT_CLOUDFLARE_CONFIG = CloudflareConfig(
    auto_dns=True,
    ttl=60,
    proxied=False,
)

# Common pyproject.toml content for testing djb package
DJB_PYPROJECT_CONTENT = '[project]\nname = "djb"\nversion = "0.1.0"\n'


# =============================================================================
# Mock Filesystem Fixture
# =============================================================================


@dataclass
class MockFilesystem:
    """Unified mock filesystem for unit testing file operations.

    Consolidates common file mocking patterns into a single class:
    - Track virtual files (Path -> content mapping)
    - Track virtual directories
    - Log all read/write operations for assertions
    - Mock Path methods: read_text, exists, is_dir, is_file, mkdir, chmod
    - Optionally mock file locking (atomic_write)

    Attributes:
        files: Dict mapping Path objects to file contents
        dirs: Set of Path objects representing directories
        read_log: List of paths that were read (for assertions)
        write_log: List of (path, content) tuples written
        chmod_calls: List of (path, mode) tuples for chmod operations
        cwd: Optional fake current working directory

    Example:
        def test_reads_config(mock_fs):
            mock_fs.files[Path("/project/config.toml")] = "key = 'value'"
            mock_fs.dirs.add(Path("/project"))

            with mock_fs.apply():
                content = Path("/project/config.toml").read_text()
                assert content == "key = 'value'"

            mock_fs.assert_read(Path("/project/config.toml"))

    Example with factory fixture:
        @pytest.fixture
        def mock_fs():
            return MockFilesystem()

        def test_writes_file(mock_fs):
            mock_fs.dirs.add(Path("/project"))

            with mock_fs.apply(mock_locking=True):
                atomic_write(Path("/project/out.txt"), "content")

            mock_fs.assert_written(Path("/project/out.txt"), "content")
    """

    files: dict[Path, str] = field(default_factory=dict)
    dirs: set[Path] = field(default_factory=set)
    read_log: list[Path] = field(default_factory=list)
    write_log: list[tuple[Path, str]] = field(default_factory=list)
    chmod_calls: list[tuple[Path, int]] = field(default_factory=list)
    cwd: Path | None = None

    def add_file(self, path: Path | str, content: str = "") -> None:
        """Add a virtual file with content."""
        p = Path(path) if isinstance(path, str) else path
        self.files[p] = content

    def add_dir(self, path: Path | str) -> None:
        """Add a virtual directory."""
        p = Path(path) if isinstance(path, str) else path
        self.dirs.add(p)

    def clear_logs(self) -> None:
        """Clear read/write/chmod logs while preserving files/dirs."""
        self.read_log.clear()
        self.write_log.clear()
        self.chmod_calls.clear()

    def assert_read(self, path: Path | str) -> None:
        """Assert that a file was read."""
        p = Path(path) if isinstance(path, str) else path
        assert (
            p in self.read_log
        ), f"Expected {p} to be read, but it wasn't. Read log: {self.read_log}"

    def assert_not_read(self, path: Path | str) -> None:
        """Assert that a file was NOT read."""
        p = Path(path) if isinstance(path, str) else path
        assert p not in self.read_log, f"Expected {p} NOT to be read, but it was"

    def assert_written(self, path: Path | str, content: str | None = None) -> None:
        """Assert that a file was written, optionally with specific content."""
        p = Path(path) if isinstance(path, str) else path
        written_paths = [wp for wp, _ in self.write_log]
        assert (
            p in written_paths
        ), f"Expected {p} to be written, but it wasn't. Write log: {written_paths}"

        if content is not None:
            for wp, wc in self.write_log:
                if wp == p:
                    assert wc == content, f"Expected content '{content}', got '{wc}'"
                    return

    def assert_not_written(self, path: Path | str) -> None:
        """Assert that a file was NOT written."""
        p = Path(path) if isinstance(path, str) else path
        written_paths = [wp for wp, _ in self.write_log]
        assert p not in written_paths, f"Expected {p} NOT to be written, but it was"

    def get_written_content(self, path: Path | str) -> str | None:
        """Get the content that was written to a path, or None if not written."""
        p = Path(path) if isinstance(path, str) else path
        for wp, wc in reversed(self.write_log):  # Get most recent write
            if wp == p:
                return wc
        return None

    @contextmanager
    def apply(
        self,
        *,
        mock_locking: bool = False,
        locking_module: str = "djb.cli.editable",
    ) -> Generator[None, None, None]:
        """Apply the mock filesystem as a context manager.

        Args:
            mock_locking: If True, also mock file_lock and atomic_write
            locking_module: Module path where locking functions are imported

        Example:
            with mock_fs.apply():
                content = Path("/fake/file.txt").read_text()

            with mock_fs.apply(mock_locking=True):
                atomic_write(Path("/fake/out.txt"), "data")
        """
        mock_self = self  # Capture for closures

        def mock_read_text(path_self: Path, *args: Any, **kwargs: Any) -> str:
            mock_self.read_log.append(path_self)
            if path_self in mock_self.files:
                return mock_self.files[path_self]
            raise FileNotFoundError(path_self)

        def mock_exists(path_self: Path) -> bool:
            return path_self in mock_self.files or path_self in mock_self.dirs

        def mock_is_dir(path_self: Path) -> bool:
            return path_self in mock_self.dirs

        def mock_is_file(path_self: Path) -> bool:
            return path_self in mock_self.files

        def mock_mkdir(path_self: Path, *args: Any, **kwargs: Any) -> None:
            mock_self.dirs.add(path_self)

        def mock_chmod(path_self: Path, mode: int) -> None:
            mock_self.chmod_calls.append((path_self, mode))

        def mock_stat(path_self: Path, *args: Any, **kwargs: Any) -> os.stat_result:
            """Return a fake stat result for mocked files."""
            if path_self not in mock_self.files and path_self not in mock_self.dirs:
                raise FileNotFoundError(f"No such file or directory: {path_self}")
            # Return a fake stat result with mtime=0 (good enough for caching)
            return os.stat_result((0o644, 0, 0, 1, 0, 0, 0, 0, 0.0, 0))

        def mock_resolve(path_self: Path, *args: Any, **kwargs: Any) -> Path:
            """Return the path as-is (mock files don't need real resolution)."""
            return path_self

        def mock_write_text(path_self: Path, content: str, *args: Any, **kwargs: Any) -> None:
            mock_self.write_log.append((path_self, content))
            mock_self.files[path_self] = content

        def fake_atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            mock_self.write_log.append((path, content))
            mock_self.files[path] = content

        def mock_open(
            file: Path | str, mode: str = "r", *args: Any, **kwargs: Any
        ) -> io.BytesIO | io.StringIO:
            p = Path(file) if isinstance(file, str) else file
            mock_self.read_log.append(p)
            if p not in mock_self.files:
                raise FileNotFoundError(p)
            content = mock_self.files[p]
            if "b" in mode:
                return io.BytesIO(content.encode())
            return io.StringIO(content)

        # Build list of patches
        patches = [
            patch.object(Path, "read_text", mock_read_text),
            patch.object(Path, "exists", mock_exists),
            patch.object(Path, "is_dir", mock_is_dir),
            patch.object(Path, "is_file", mock_is_file),
            patch.object(Path, "mkdir", mock_mkdir),
            patch.object(Path, "chmod", mock_chmod),
            patch.object(Path, "stat", mock_stat),
            patch.object(Path, "resolve", mock_resolve),
            patch.object(Path, "write_text", mock_write_text),
            patch("builtins.open", mock_open),
        ]

        # Optionally mock cwd
        if mock_self.cwd is not None:
            patches.append(patch("pathlib.Path.cwd", return_value=mock_self.cwd))

        # Optionally mock file locking
        if mock_locking:
            patches.append(patch(f"{locking_module}.file_lock", return_value=nullcontext()))
            patches.append(patch(f"{locking_module}.atomic_write", side_effect=fake_atomic_write))

        # Apply all patches using ExitStack
        with ExitStack() as stack:
            # Clear TOML cache to avoid pollution from real files
            clear_toml_cache()
            for p in patches:
                stack.enter_context(p)
            try:
                yield
            finally:
                # Clear cache on exit too to not pollute other tests
                clear_toml_cache()


@pytest.fixture
def mock_fs() -> MockFilesystem:
    """Create a MockFilesystem instance for testing file operations.

    This fixture provides a unified way to mock Path operations without
    real I/O. Use mock_fs.apply() as a context manager to enable the mocks.

    Example:
        def test_reads_pyproject(mock_fs):
            mock_fs.add_file(Path("/project/pyproject.toml"), '[project]\\nname = "test"')
            mock_fs.add_dir(Path("/project"))

            with mock_fs.apply():
                content = (Path("/project") / "pyproject.toml").read_text()
                assert "test" in content

            mock_fs.assert_read(Path("/project/pyproject.toml"))

    Example with file locking:
        def test_writes_with_lock(mock_fs):
            mock_fs.add_dir(Path("/project"))

            with mock_fs.apply(mock_locking=True):
                from djb.cli.editable import atomic_write
                atomic_write(Path("/project/out.txt"), "content")

            mock_fs.assert_written(Path("/project/out.txt"), "content")
    """
    return MockFilesystem()


# =============================================================================
# Mock DjbConfig Fixture
# =============================================================================


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overlay into base, with overlay values winning."""
    result = dict(base)
    for key, value in overlay.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _get_unit_test_defaults() -> DjbConfig:
    """Return default DjbConfig for unit test mocks.

    This is defined as a DjbConfig for type safety when viewing/editing defaults.
    """
    return DjbConfig(
        project_name="testproject",
        project_dir=FAKE_PROJECT_DIR,
        mode=Mode.DEVELOPMENT,
        email="test@example.com",
        yes=False,
        k8s=K8sConfig(
            provider=K8sProvider.MANUAL,
            cluster_name=None,
            cluster_type=K8sClusterType.K3D,
            host=None,
            port=22,
            ssh_key=None,
            no_cloudnativepg=False,
            no_tls=False,
            cnpg_manifest_url="https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml",
            kubectl_wait_timeout_s=120,
            backend=K8sBackendConfig(managed_dockerfile=True),
        ),
        hetzner=HetznerConfig(
            ssh_key_name=None,
            server_name=None,
            default_server_type=HetznerServerType.CX23.value,
            default_location=HetznerLocation.NBG1.value,
            default_image=HetznerImage.UBUNTU_24_04.value,
        ),
    )


def _setup_mock_from_dict(mock: MagicMock, data: dict[str, Any], prefix: str = "") -> None:
    """Recursively set mock attributes from a nested dict.

    Converts string values back to enums for known enum fields.
    """
    # Map of field paths to enum types (for converting strings back to enums)
    enum_fields: dict[str, type] = {
        "mode": Mode,
        "platform": Platform,
        "k8s.provider": K8sProvider,
        "k8s.cluster_type": K8sClusterType,
    }

    for key, value in data.items():
        full_path = f"{prefix}{key}"
        if isinstance(value, dict):
            # Create a nested mock for dict values
            nested_mock = getattr(mock, key)
            _setup_mock_from_dict(nested_mock, value, prefix=f"{full_path}.")
        else:
            # Convert strings back to enums for known enum fields
            if full_path in enum_fields and isinstance(value, str):
                enum_class = enum_fields[full_path]
                try:
                    value = enum_class(value)
                except ValueError:
                    # Keep as string if not a valid enum value
                    pass
            setattr(mock, key, value)


@pytest.fixture
def mock_djb_config():
    """Factory for creating mock DjbConfig for unit tests.

    Returns a factory that creates MagicMock instances with configurable
    attributes. Use for unit tests that mock I/O. For E2E tests that need
    real config objects, use make_djb_config from djb.testing.e2e instead.

    Example:
        def test_something(mock_djb_config):
            config = mock_djb_config()  # Uses defaults
            config = mock_djb_config(DjbConfig(k8s=K8sConfig(host="1.2.3.4")))
    """

    def _make_mock(overrides: DjbConfig | None = None) -> MagicMock:
        defaults = _get_unit_test_defaults()
        defaults_dict = defaults.to_dict()

        # Override defaults with fields from to_overrides() (which tracks what
        # was explicitly passed to DjbConfig, excluding None values).
        # Tests that need explicit None should set mock.field = None after creation.
        if overrides:
            overrides_dict = overrides.to_overrides()
            merged = _deep_merge(defaults_dict, overrides_dict)
        else:
            merged = defaults_dict

        # Create mock and populate from merged dict
        mock = MagicMock()
        _setup_mock_from_dict(mock, merged)

        # Add computed properties
        project_name = merged.get("project_name", "testproject")
        k8s = merged.get("k8s", {})
        cluster_name = k8s.get("cluster_name") if isinstance(k8s, dict) else None
        host = k8s.get("host") if isinstance(k8s, dict) else None

        mock.k8s.effective_cluster_name = cluster_name or f"djb-{project_name}"
        mock.k8s.is_public = host is not None

        # Create letsencrypt mock with computed effective_email property
        # This mirrors the real behavior: effective_email = letsencrypt.email or config.email
        letsencrypt_mock = MagicMock()
        letsencrypt_email = (
            merged.get("letsencrypt", {}).get("email")
            if isinstance(merged.get("letsencrypt"), dict)
            else None
        )
        letsencrypt_mock.email = letsencrypt_email
        type(letsencrypt_mock).effective_email = property(lambda self: self.email or mock.email)
        mock.letsencrypt = letsencrypt_mock

        # Add Hetzner effective properties
        hetzner = merged.get("hetzner", {})
        if isinstance(hetzner, dict):
            mock.hetzner.effective_server_type = hetzner.get("default_server_type", "cx23")
            mock.hetzner.effective_location = hetzner.get("default_location", "nbg1")
            mock.hetzner.effective_image = hetzner.get("default_image", "ubuntu-24.04")

        return mock

    return _make_mock


# =============================================================================
# Mock MachineContext Fixture
# =============================================================================


@pytest.fixture
def mock_machine_context(mock_djb_config):
    """Factory for creating MachineContext for unit tests.

    Returns a factory that creates MachineContext instances with mocked
    config, runner, and logger. Use for machine_state unit tests.

    Example:
        def test_state_check(mock_machine_context):
            ctx = mock_machine_context()  # Uses defaults
            ctx = mock_machine_context(options=TerraformOptions(force_create=True))

        def test_with_custom_config(mock_machine_context, mock_djb_config):
            config = mock_djb_config(DjbConfig(project_name="custom"))
            ctx = mock_machine_context(config=config)
    """

    def _make_context(
        *,
        config: MagicMock | None = None,
        runner: MagicMock | None = None,
        logger: MagicMock | None = None,
        secrets: MagicMock | None = None,
        options: Any = None,
    ) -> MachineContext:
        return MachineContext(
            config=config if config is not None else mock_djb_config(),
            runner=runner if runner is not None else MagicMock(),
            logger=logger if logger is not None else MagicMock(),
            secrets=secrets,
            options=options,
        )

    return _make_context


__all__ = [
    # Project directory fixtures
    "project_dir",
    # CLI testing fixtures
    "configure_logging",
    "mock_cli_ctx",
    "mock_cmd_runner",
    # PTY fixtures
    "pty_stdin",
    # Docker fixtures (E2E)
    "is_docker_available",
    "require_docker",
    # Test constants
    "FAKE_PROJECT_DIR",
    "DEFAULT_HETZNER_CONFIG",
    "DEFAULT_HEROKU_CONFIG",
    "DEFAULT_K8S_CONFIG",
    "DEFAULT_K8S_BACKEND_CONFIG",
    "DEFAULT_CLOUDFLARE_CONFIG",
    "DJB_PYPROJECT_CONTENT",
    # Mock filesystem
    "MockFilesystem",
    "mock_fs",
    # Mock config fixtures
    "mock_djb_config",
    "mock_machine_context",
]
