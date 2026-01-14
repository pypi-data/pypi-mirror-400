"""Secrets isolation fixtures for E2E tests.

These fixtures provide isolated environments for tools like GPG, age, and SOPS.
"""

from __future__ import annotations

import os
import subprocess  # noqa: TID251 - E2E tests invoke real GPG commands
from collections.abc import Callable, Generator
from pathlib import Path

import pytest

from djb.cli.context import CliContext
from djb.secrets import SecretsManager

# Constants for test encryption
TEST_PASSPHRASE = "test-passphrase-12345"
TEST_SECRET_VALUE = "super-secret-test-value-abc123"

# Constants for GPG test profile
TEST_GPG_NAME = "DJB Test User"
TEST_GPG_EMAIL = "djb-test@example.com"


@pytest.fixture
def gpg_home(project_dir: Path) -> Path:
    """Create an isolated GPG home directory.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    gpg_dir = project_dir / ".gnupg"
    gpg_dir.mkdir(mode=0o700)
    return gpg_dir


@pytest.fixture
def secrets_dir(project_dir: Path) -> Path:
    """Create a secrets directory for testing.

    Uses project_dir for fixture layering; tests can override
    project_dir to customize the base directory.
    """
    dir_path = project_dir / "secrets"
    dir_path.mkdir()
    return dir_path


@pytest.fixture
def setup_sops_config(project_dir: Path, secrets_dir: Path) -> Callable[[dict[str, str]], Path]:
    """Factory fixture to create .sops.yaml configuration.

    Example:
        def test_sops(setup_sops_config, alice_key):
            _, alice_public = alice_key
            setup_sops_config({alice_public: "alice@example.com"})
    """
    runner = CliContext(verbose=False).runner

    def _setup(recipients: dict[str, str]) -> Path:
        manager = SecretsManager(runner, project_dir, secrets_dir=secrets_dir)
        return manager.save_config(recipients)

    return _setup


@pytest.fixture
def gpg_test_profile(project_dir: Path) -> Generator[dict[str, str | Path | None], None, None]:
    """Create isolated GPG profile with no-passphrase test key.

    This fixture creates a complete isolated GPG environment for E2E tests:
    1. Creates GNUPGHOME directory with proper permissions
    2. Configures GPG agent with loopback pinentry
    3. Generates a GPG key with %no-protection (no passphrase)
    4. Sets GNUPGHOME environment variable
    5. Yields profile info for tests
    6. Cleans up GPG agent and restores environment

    The no-passphrase key allows non-interactive encrypt/decrypt operations
    without needing gpg-preset-passphrase or pinentry configuration.

    Yields:
        dict with 'gnupg_home' (Path), 'email' (str), 'key_id' (str | None) keys

    Example:
        def test_gpg_encryption(gpg_test_profile, project_dir):
            # GPG operations now work without passphrase prompts
            from djb.secrets import protect_age_key
            protect_age_key(project_dir, runner)
    """
    gnupg_home = project_dir / ".gnupg"
    gnupg_home.mkdir(mode=0o700)

    # Configure GPG agent with loopback pinentry and caching
    agent_conf = gnupg_home / "gpg-agent.conf"
    agent_conf.write_text(
        "default-cache-ttl 28800\n" "max-cache-ttl 28800\n" "allow-loopback-pinentry\n"
    )
    agent_conf.chmod(0o600)

    # Generate no-passphrase key using batch mode
    # %no-protection creates a key without passphrase protection
    key_params = f"""\
%no-protection
Key-Type: eddsa
Key-Curve: ed25519
Key-Usage: sign
Subkey-Type: ecdh
Subkey-Curve: cv25519
Subkey-Usage: encrypt
Name-Real: {TEST_GPG_NAME}
Name-Email: {TEST_GPG_EMAIL}
Expire-Date: 0
%commit
"""
    params_file = gnupg_home / "key-params.txt"
    params_file.write_text(key_params)

    # Set up environment with isolated GNUPGHOME
    env = os.environ.copy()
    env["GNUPGHOME"] = str(gnupg_home)

    # Generate the key
    result = subprocess.run(
        ["gpg", "--batch", "--gen-key", str(params_file)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate test GPG key: {result.stderr}")

    # Get the key ID from the generated key
    result = subprocess.run(
        ["gpg", "--list-secret-keys", "--with-colons", TEST_GPG_EMAIL],
        env=env,
        capture_output=True,
        text=True,
    )
    key_id: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("sec:"):
            parts = line.split(":")
            if len(parts) > 4:
                key_id = parts[4]
                break

    # Store original GNUPGHOME to restore later
    original_gnupghome = os.environ.get("GNUPGHOME")
    os.environ["GNUPGHOME"] = str(gnupg_home)

    try:
        yield {
            "gnupg_home": gnupg_home,
            "email": TEST_GPG_EMAIL,
            "key_id": key_id,
        }
    finally:
        # Restore original GNUPGHOME
        if original_gnupghome:
            os.environ["GNUPGHOME"] = original_gnupghome
        else:
            os.environ.pop("GNUPGHOME", None)

        # Kill gpg-agent for this profile to clean up
        subprocess.run(
            ["gpgconf", "--homedir", str(gnupg_home), "--kill", "gpg-agent"],
            capture_output=True,
        )
