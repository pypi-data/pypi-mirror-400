"""Shared fixtures for E2E tests in djb.core module."""

from __future__ import annotations

import pytest

from djb.core.cmd_runner import CmdRunner


@pytest.fixture
def runner():
    """Provide a non-verbose CmdRunner for E2E testing."""
    return CmdRunner(verbose=False)


@pytest.fixture
def verbose_runner():
    """Provide a verbose CmdRunner for testing output streaming."""
    return CmdRunner(verbose=True)
