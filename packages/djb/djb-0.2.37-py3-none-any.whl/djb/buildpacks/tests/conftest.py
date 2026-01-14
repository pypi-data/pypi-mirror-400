"""Shared fixtures for buildpacks unit tests.

Note: Fixtures needing file I/O are in e2e/conftest.py
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from djb.testing.fixtures import mock_cmd_runner as mock_cmd_runner  # noqa: F401


@pytest.fixture
def mock_ssh() -> MagicMock:
    """Mock SSHClient for remote buildpack tests."""
    ssh = MagicMock()
    # Default: commands succeed
    ssh.run.return_value = (0, "", "")
    return ssh
