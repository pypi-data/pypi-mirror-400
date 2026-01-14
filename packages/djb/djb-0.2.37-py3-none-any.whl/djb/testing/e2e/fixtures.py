"""E2E testing fixtures.

These fixtures provide real I/O for E2E tests. They override unit test defaults.
Import in your E2E conftest.py to enable real directory and command operations.

Fixtures:
    project_dir - Returns tmp_path for real file I/O (overrides unit test default)
    make_pyproject - Factory to create pyproject.toml files
    make_cli_ctx - Real CliContext for E2E tests
    cli_runner - Click CLI test runner
    make_cmd_runner - Real CmdRunner for E2E tests
    make_age_key - Factory for creating age key pairs
    alice_key - Pre-made age key pair for Alice
    bob_key - Pre-made age key pair for Bob
    make_djb_config - Factory for creating DjbConfig with custom overrides
    make_editable_pyproject - Function to generate editable pyproject.toml content

Classes:
    AgePathAndPublicKey - NamedTuple with key file path and public key

Constants:
    EDITABLE_PYPROJECT_TEMPLATE - Template for editable pyproject.toml
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from djb.cli.context import CliContext
from djb.config import DjbConfig
from djb.config.fields.machine_state import MachineStateConfig
from djb.config.fields.secrets import SecretsConfig
from djb.config.storage.io.external import GitConfigIO
from djb.machine_state import SearchStrategy
from djb.core.cmd_runner import CmdRunner
from djb.secrets import generate_age_key
from djb.testing.fixtures import (
    DEFAULT_CLOUDFLARE_CONFIG,
    DEFAULT_HEROKU_CONFIG,
    DEFAULT_HETZNER_CONFIG,
    DEFAULT_K8S_CONFIG,
)
from djb.types import Mode, Platform


# =============================================================================
# Project Directory Fixture
# =============================================================================


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Project directory for E2E tests.

    Returns tmp_path for E2E tests that need real file I/O.
    This overrides the unit test fixture in djb.testing.fixtures.
    """
    return tmp_path


# =============================================================================
# Pyproject Factory
# =============================================================================


@pytest.fixture
def make_pyproject(project_dir: Path) -> Callable[..., Path]:
    """Factory to create pyproject.toml.

    Args:
        name: Project name (default: "test-project")
        version: Project version (default: "0.1.0")
        dependencies: List of dependencies (default: ["django>=5.0"])
        tool_djb: Optional [tool.djb] section content as dict

    Returns:
        Path to the created pyproject.toml

    Example:
        pyproject = make_pyproject()
        pyproject = make_pyproject(dependencies=["gdal==3.10.0"])
        pyproject = make_pyproject(tool_djb={"project_name": "myapp"})
    """

    def _make_pyproject(
        *,
        name: str = "test-project",
        version: str = "0.1.0",
        dependencies: list[str] | None = None,
        tool_djb: dict[str, str] | None = None,
    ) -> Path:
        deps = dependencies if dependencies is not None else ["django>=5.0"]
        deps_str = ",\n    ".join(f'"{d}"' for d in deps)

        content = f"""\
[project]
name = "{name}"
version = "{version}"
dependencies = [
    {deps_str},
]
"""
        if tool_djb:
            tool_djb_lines = "\n".join(f'{k} = "{v}"' for k, v in tool_djb.items())
            content += f"\n[tool.djb]\n{tool_djb_lines}\n"

        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(content)
        return pyproject

    return _make_pyproject


# =============================================================================
# CLI Context and Runner Fixtures
# =============================================================================


@pytest.fixture
def make_cli_ctx() -> CliContext:
    """Create a real CliContext for E2E tests.

    This is the base context fixture. The context has a real runner (via
    cached_property) that executes real commands.

    Use this for integration/E2E tests that need actual command execution.

    Example:
        def test_something(make_cli_ctx):
            result = make_cli_ctx.runner.run(["echo", "hello"])
            assert result.returncode == 0
    """
    return CliContext()


@pytest.fixture
def make_cmd_runner(make_cli_ctx: CliContext) -> CmdRunner:
    """Create a CmdRunner for E2E tests that need real command execution.

    Use mock_cmd_runner in unit-tests that don't need real command execution.
    Prefer using make_cli_ctx.runner directly.

    Example:
        def test_something(make_cmd_runner):
            result = make_cmd_runner.run(["echo", "hello"])
            assert result.returncode == 0
    """
    return make_cli_ctx.runner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Click CLI test runner.

    Returns a CliRunner instance for invoking Click commands
    in tests. The CliRunner captures stdout/stderr and provides
    access to exit codes and output.

    Example:
        def test_health_help(cli_runner):
            result = cli_runner.invoke(djb_cli, ["health", "--help"])
            assert result.exit_code == 0
    """
    return CliRunner()


# =============================================================================
# Age Key Fixtures
# =============================================================================


class AgePathAndPublicKey(NamedTuple):
    """Path to an age key file and its public key.

    Note: This is distinct from djb.secrets.AgeKeyPair which contains
    the actual public_key and private_key strings (key content).
    """

    key_path: Path
    public_key: str


@pytest.fixture
def make_age_key(tmp_path: Path) -> Callable[[str], AgePathAndPublicKey]:
    """Factory fixture to create age key pairs.

    Creates age keys in a structured directory under tmp_path/.age/{name}/keys.txt.
    Each call with a different name creates a separate key pair.

    Returns a factory function that takes a name and returns an AgePathAndPublicKey.

    Pytest:
        Uses pytest's `tmp_path` fixture internally, so keys are created in the
        same temporary directory available to the test function.

    Example:
        def test_with_keys(tmp_path, make_age_key):
            # make_age_key uses the same tmp_path as the test
            alice_key_path, alice_public_key = make_age_key("alice")
            bob_key_path, bob_public_key = make_age_key("bob")
    """
    runner = CmdRunner()  # Non-verbose runner for key generation

    def _make_key(name: str) -> AgePathAndPublicKey:
        key_dir = tmp_path / ".age" / name
        key_dir.mkdir(parents=True, exist_ok=True)
        key_path = key_dir / "keys.txt"
        public_key, _ = generate_age_key(runner, key_path)
        return AgePathAndPublicKey(key_path, public_key)

    return _make_key


@pytest.fixture
def alice_key(make_age_key: Callable[[str], AgePathAndPublicKey]) -> AgePathAndPublicKey:
    """Create Alice's age key pair.

    Returns an AgePathAndPublicKey for Alice.
    Useful for tests that need a pre-made key without calling make_age_key directly.

    Pytest:
        Depends on `make_age_key` fixture, which in turn uses `tmp_path`.

    Example:
        def test_encryption(alice_key):
            key_path, public_key = alice_key
            # ... use key for encryption
    """
    return make_age_key("alice")


@pytest.fixture
def bob_key(make_age_key: Callable[[str], AgePathAndPublicKey]) -> AgePathAndPublicKey:
    """Create Bob's age key pair.

    Returns an AgePathAndPublicKey for Bob.
    Useful for tests that need two different keys (e.g., testing key rotation).

    Pytest:
        Depends on `make_age_key` fixture, which in turn uses `tmp_path`.

    Example:
        def test_rotation(alice_key, bob_key):
            alice_path, alice_public = alice_key
            bob_path, bob_public = bob_key
            # ... test key rotation
    """
    return make_age_key("bob")


# =============================================================================
# DjbConfig Fixture
# =============================================================================


@pytest.fixture
def make_djb_config(project_dir: Path) -> Callable[[DjbConfig | None], DjbConfig]:
    """Factory fixture for creating DjbConfig with custom overrides.

    Depends on project_dir fixture (which is tmp_path for E2E tests).
    Returns a factory function that accepts an optional DjbConfig for overrides.

    The config is NOT automatically saved. For CLI tests that need config
    persisted so get_djb_config() returns the same values, call config.save():

        config = make_djb_config()
        config.save()  # Persists to .djb/local.toml and .djb/project.toml

    Example:
        def test_storage_read(make_djb_config):
            config = make_djb_config()  # Uses test defaults, not saved
            io = LocalConfigIO(config)
            ...

        def test_cli_command(make_djb_config, cli_runner):
            config = make_djb_config()
            config.save()  # Save so CLI command can read it
            result = cli_runner.invoke(djb_cli, ["health"])
    """

    def _make_config(overrides: DjbConfig | None = None) -> DjbConfig:
        defaults = DjbConfig(
            project_dir=project_dir,
            mode=Mode.DEVELOPMENT,
            config_class="djb.config.DjbConfig",
            project_name="test-project",
            platform=Platform.HEROKU,
            name="Test User",
            email="test@example.com",
            log_level="info",
            verbose=False,
            quiet=False,
            yes=False,
            secrets=SecretsConfig(encrypt=True),
            hetzner=DEFAULT_HETZNER_CONFIG,
            heroku=DEFAULT_HEROKU_CONFIG,
            k8s=DEFAULT_K8S_CONFIG,
            cloudflare=DEFAULT_CLOUDFLARE_CONFIG,
            machine_state=MachineStateConfig(search_strategy=SearchStrategy.AUTO),
        )
        config = DjbConfig._load(env={}, overrides_dict=defaults.to_overrides())

        if overrides:
            config = config.augment(overrides)
        return config

    return _make_config


# =============================================================================
# Editable Pyproject
# =============================================================================

# Template for editable pyproject.toml (host project with djb in editable mode)
EDITABLE_PYPROJECT_TEMPLATE = """\
[project]
name = "myproject"

[tool.uv.workspace]
members = ["{path}"]

[tool.uv.sources]
djb = {{ workspace = true, editable = true }}
"""


def make_editable_pyproject(djb_path: str = "djb") -> str:
    """Generate editable pyproject.toml content with given djb path."""
    return EDITABLE_PYPROJECT_TEMPLATE.format(path=djb_path)


# =============================================================================
# Git Config Isolation
# =============================================================================


@pytest.fixture(autouse=True)
def isolate_git_config(monkeypatch):
    """Isolate tests from system git config (autouse).

    Patches GitConfigIO to return test values for known keys (name, email)
    and None for everything else. This ensures tests never expose the
    user's actual git config while providing values that init and other
    commands expect.

    This fixture is autouse=True, so it applies to all E2E tests that
    import from djb.testing.e2e.
    """
    # Provide test values for known config keys
    test_values = {
        "name": "Test User",
        "email": "test@example.com",
    }

    def _get_value(_self, key: str):
        return test_values.get(key)

    monkeypatch.setattr(GitConfigIO, "_get_value", _get_value)


__all__ = [
    # Project directory
    "project_dir",
    # Pyproject factory
    "make_pyproject",
    # CLI context and runner
    "make_cli_ctx",
    "make_cmd_runner",
    "cli_runner",
    # Age keys
    "AgePathAndPublicKey",
    "make_age_key",
    "alice_key",
    "bob_key",
    # Config
    "make_djb_config",
    # Editable pyproject
    "EDITABLE_PYPROJECT_TEMPLATE",
    "make_editable_pyproject",
    # Git isolation
    "isolate_git_config",
]
