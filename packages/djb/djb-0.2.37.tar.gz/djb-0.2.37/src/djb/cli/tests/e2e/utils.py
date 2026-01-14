"""Shared test utilities for djb CLI E2E tests.

This module provides reusable helper functions for:
- GPG encryption/decryption with environment isolation
- Age/SOPS operations
- Project structure creation
- Assertion helpers
- Context managers for safe decrypt-use-cleanup cycles

All utilities are designed to avoid polluting the user's real environment
by accepting optional parameters for isolated directories and configs.
"""

from __future__ import annotations

import os
import subprocess  # noqa: TID251 - invoking gpg/age/sops/git directly
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# GPG Utilities
# =============================================================================


def gpg_encrypt(
    input_path: Path,
    output_path: Path,
    passphrase: str,
    *,
    gpg_home: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Encrypt a file using GPG symmetric encryption.

    Args:
        input_path: Path to the plaintext file to encrypt
        output_path: Path where encrypted file will be written
        passphrase: Passphrase for encryption
        gpg_home: Optional GPG home directory for isolation (avoids ~/.gnupg)

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    cmd = [
        "gpg",
        "--symmetric",
        "--batch",
        "--yes",
        "--armor",
        "--passphrase-fd",
        "0",
        "--output",
        str(output_path),
        str(input_path),
    ]

    if gpg_home:
        cmd.insert(1, "--homedir")
        cmd.insert(2, str(gpg_home))

    return subprocess.run(
        cmd,
        input=passphrase,
        capture_output=True,
        text=True,
    )


def gpg_decrypt(
    input_path: Path,
    output_path: Path,
    passphrase: str,
    *,
    gpg_home: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Decrypt a GPG-encrypted file.

    Args:
        input_path: Path to the encrypted file
        output_path: Path where decrypted file will be written
        passphrase: Passphrase for decryption
        gpg_home: Optional GPG home directory for isolation

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    cmd = [
        "gpg",
        "--decrypt",
        "--batch",
        "--yes",
        "--passphrase-fd",
        "0",
        "--output",
        str(output_path),
        str(input_path),
    ]

    if gpg_home:
        cmd.insert(1, "--homedir")
        cmd.insert(2, str(gpg_home))

    return subprocess.run(
        cmd,
        input=passphrase,
        capture_output=True,
        text=True,
    )


def gpg_encrypt_with_profile(
    input_path: Path,
    output_path: Path,
    recipient: str,
    gnupg_home: Path,
) -> subprocess.CompletedProcess[str]:
    """Encrypt a file with GPG public key using isolated profile.

    For use with gpg_test_profile fixture which creates a no-passphrase key.
    Uses public-key encryption (not symmetric).

    Args:
        input_path: Path to the plaintext file
        output_path: Path where encrypted file will be written
        recipient: Email/key ID of the recipient (e.g., TEST_GPG_EMAIL)
        gnupg_home: Path to isolated GNUPGHOME directory

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    env = os.environ.copy()
    env["GNUPGHOME"] = str(gnupg_home)

    return subprocess.run(
        [
            "gpg",
            "--encrypt",
            "--batch",
            "--yes",
            "--armor",
            "--recipient",
            recipient,
            "--output",
            str(output_path),
            str(input_path),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


def gpg_decrypt_with_profile(
    input_path: Path,
    output_path: Path,
    gnupg_home: Path,
) -> subprocess.CompletedProcess[str]:
    """Decrypt a GPG-encrypted file using isolated profile.

    For use with gpg_test_profile fixture which creates a no-passphrase key.
    No passphrase input needed because the test key has %no-protection.

    Args:
        input_path: Path to the encrypted file
        output_path: Path where decrypted file will be written
        gnupg_home: Path to isolated GNUPGHOME directory

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    env = os.environ.copy()
    env["GNUPGHOME"] = str(gnupg_home)

    return subprocess.run(
        [
            "gpg",
            "--decrypt",
            "--batch",
            "--yes",
            "--output",
            str(output_path),
            str(input_path),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


# =============================================================================
# Age/SOPS Utilities
# =============================================================================


def create_sops_config(secrets_dir: Path, public_key: str) -> Path:
    """Create a .sops.yaml config for testing.

    Args:
        secrets_dir: Directory where .sops.yaml will be created
        public_key: Age public key to use for encryption

    Returns:
        Path to the created .sops.yaml file
    """
    config_path = secrets_dir / ".sops.yaml"
    config_path.write_text(
        f"""creation_rules:
  - path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          - {public_key}
"""
    )
    return config_path


def sops_encrypt(
    file_path: Path,
    config_path: Path,
    key_path: Path,
) -> subprocess.CompletedProcess[str]:
    """Encrypt a file with SOPS.

    Args:
        file_path: Path to the file to encrypt (will be encrypted in-place)
        config_path: Path to .sops.yaml config
        key_path: Path to age key file

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    env = os.environ.copy()
    env["SOPS_AGE_KEY_FILE"] = str(key_path)

    return subprocess.run(
        [
            "sops",
            "--encrypt",
            "--config",
            str(config_path),
            "--in-place",
            str(file_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def sops_decrypt(
    file_path: Path,
    config_path: Path,
    key_path: Path,
) -> subprocess.CompletedProcess[str]:
    """Decrypt a SOPS-encrypted file (returns content in stdout).

    Args:
        file_path: Path to the encrypted file
        config_path: Path to .sops.yaml config
        key_path: Path to age key file

    Returns:
        CompletedProcess with decrypted content in stdout
    """
    env = os.environ.copy()
    env["SOPS_AGE_KEY_FILE"] = str(key_path)

    return subprocess.run(
        [
            "sops",
            "--decrypt",
            "--config",
            str(config_path),
            str(file_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def age_encrypt(
    input_path: Path,
    output_path: Path,
    public_key: str,
) -> subprocess.CompletedProcess[str]:
    """Encrypt a file with age.

    Args:
        input_path: Path to the plaintext file
        output_path: Path where encrypted file will be written
        public_key: Age public key for encryption

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    return subprocess.run(
        ["age", "-r", public_key, "-o", str(output_path), str(input_path)],
        capture_output=True,
        text=True,
    )


def age_decrypt(
    input_path: Path,
    output_path: Path,
    key_path: Path,
) -> subprocess.CompletedProcess[str]:
    """Decrypt an age-encrypted file.

    Args:
        input_path: Path to the encrypted file
        output_path: Path where decrypted file will be written
        key_path: Path to age private key file

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    return subprocess.run(
        ["age", "-d", "-i", str(key_path), "-o", str(output_path), str(input_path)],
        capture_output=True,
        text=True,
    )


# =============================================================================
# Project Setup Utilities
# =============================================================================


def add_initial_commit(project_dir: Path, message: str = "Initial commit") -> None:
    """Stage all files and create an initial commit.

    Args:
        project_dir: Git repository directory
        message: Commit message
    """
    subprocess.run(["git", "-C", str(project_dir), "add", "."], capture_output=True)
    subprocess.run(
        ["git", "-C", str(project_dir), "commit", "-m", message],
        capture_output=True,
    )


def create_pyproject_toml(
    project_dir: Path,
    name: str = "test-project",
    version: str = "0.1.0",
    *,
    include_tool_djb: bool = True,
    extra_content: str = "",
) -> None:
    """Create a pyproject.toml for testing.

    Args:
        project_dir: Project directory
        name: Project name
        version: Project version
        include_tool_djb: If True (default), include [tool.djb] section with
            project_name. Set to False for tests that need project_name to be
            derived from [project].name (e.g., testing djb init on a fresh project).
        extra_content: Additional TOML content to append
    """
    content = f"""[project]
name = "{name}"
version = "{version}"
"""
    if include_tool_djb:
        content += f"""
[tool.djb]
project_name = "{name}"
"""
    if extra_content:
        content += f"\n{extra_content}"
    (project_dir / "pyproject.toml").write_text(content)


def add_django_settings_from_startproject(
    project_dir: Path,
    package_name: str = "myproject",
) -> None:
    """Create a realistic Django settings structure using django-admin startproject.

    Unlike add_django_settings() which creates minimal fake settings, this function
    uses Django's startproject command to generate a complete, realistic settings
    module. This makes tests more accurate by testing against real Django structure.

    The generated project includes:
    - settings.py with SECRET_KEY, DEBUG, INSTALLED_APPS, MIDDLEWARE, etc.
    - urls.py with admin patterns
    - wsgi.py and asgi.py
    - __init__.py

    Args:
        project_dir: Project directory where Django package will be created
        package_name: Name of the Django package/settings directory
    """
    # Use Django's startproject to create a realistic project structure
    result = subprocess.run(
        [
            "django-admin",
            "startproject",
            package_name,
            str(project_dir),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"django-admin startproject failed: {result.stderr or result.stdout}")


def add_frontend_package(
    project_dir: Path,
    name: str = "frontend",
    version: str = "0.1.0",
) -> None:
    """Create a frontend directory with package.json.

    Args:
        project_dir: Project directory
        name: Package name for package.json
        version: Package version
    """
    frontend_dir = project_dir / "frontend"
    frontend_dir.mkdir(exist_ok=True)
    (frontend_dir / "package.json").write_text(f'{{"name": "{name}", "version": "{version}"}}')


def add_python_package(project_dir: Path, package_name: str = "myproject") -> None:
    """Create a Python package directory with __init__.py.

    Args:
        project_dir: Project directory
        package_name: Name of the Python package
    """
    pkg_dir = project_dir / package_name
    pkg_dir.mkdir(exist_ok=True)
    (pkg_dir / "__init__.py").write_text("")


# =============================================================================
# Assertion Helpers
# =============================================================================


def assert_gpg_encrypted(file_path: Path) -> None:
    """Assert that a file is GPG encrypted (ASCII-armored).

    Args:
        file_path: Path to the file to check

    Raises:
        AssertionError: If file is not GPG encrypted
    """
    content = file_path.read_text()
    assert "BEGIN PGP MESSAGE" in content, f"{file_path} is not GPG encrypted"


def assert_sops_encrypted(file_path: Path) -> None:
    """Assert that a file is SOPS encrypted.

    Args:
        file_path: Path to the file to check

    Raises:
        AssertionError: If file is not SOPS encrypted
    """
    content = file_path.read_text()
    assert "sops:" in content, f"{file_path} is not SOPS encrypted"


def assert_not_contains_secrets(file_path: Path, *secrets: str) -> None:
    """Assert that a file doesn't contain any of the given secrets in plaintext.

    Args:
        file_path: Path to the file to check
        *secrets: Secret strings that should not appear in the file

    Raises:
        AssertionError: If any secret is found in plaintext
    """
    content = file_path.read_text()
    for secret in secrets:
        assert secret not in content, f"Found plaintext secret '{secret}' in {file_path}"
