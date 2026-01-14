"""
Path utilities for secrets management.

This module provides path resolution functions used by other secrets modules.
Kept separate to avoid circular imports between core.py and protected.py.
"""

from __future__ import annotations

from pathlib import Path


def get_default_key_path(project_dir: Path) -> Path:
    """Get default path for age key file.

    The key is stored in the project root (.age/keys.txt) rather than the
    home directory, so each project has its own key.

    Args:
        project_dir: Project root directory.

    Returns:
        Path to the age key file (.age/keys.txt in project root).
    """
    return project_dir / ".age" / "keys.txt"


def get_encrypted_key_path(key_path: Path) -> Path:
    """Get the GPG-encrypted path for an age key file.

    Converts keys.txt -> keys.txt.gpg by appending .gpg suffix.

    Args:
        key_path: Path to the plaintext age key file.

    Returns:
        Path to the GPG-encrypted version of the key file.
    """
    return key_path.parent / (key_path.name + ".gpg")


def get_default_secrets_dir(project_dir: Path) -> Path:
    """Get default path for secrets directory.

    Args:
        project_dir: Project root directory.

    Returns:
        Path to the secrets directory (secrets/ in project root).
    """
    return project_dir / "secrets"
