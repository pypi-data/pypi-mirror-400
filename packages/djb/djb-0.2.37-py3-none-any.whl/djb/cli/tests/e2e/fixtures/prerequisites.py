"""Prerequisite checking fixtures for E2E tests.

These fixtures check for required external tools and skip tests if not available.
"""

from __future__ import annotations

import subprocess  # noqa: TID251 - checking tool availability

import pytest

from djb.secrets import check_gpg_installed


def check_age_installed() -> bool:
    """Check if age is installed."""
    try:
        result = subprocess.run(["age", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_sops_installed() -> bool:
    """Check if SOPS is installed."""
    try:
        result = subprocess.run(["sops", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_postgres_available() -> bool:
    """Check if PostgreSQL is available locally."""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture(scope="session")
def require_gpg():
    """Skip test if GPG is not installed."""
    if not check_gpg_installed():
        pytest.skip("GPG not installed (brew install gnupg)")


@pytest.fixture(scope="session")
def require_age():
    """Skip test if age is not installed."""
    if not check_age_installed():
        pytest.skip("age not installed (brew install age)")


@pytest.fixture(scope="session")
def require_sops():
    """Skip test if SOPS is not installed."""
    if not check_sops_installed():
        pytest.skip("SOPS not installed (brew install sops)")


@pytest.fixture(scope="session")
def require_postgres():
    """Skip test if PostgreSQL is not available."""
    if not check_postgres_available():
        pytest.skip("PostgreSQL not available")
