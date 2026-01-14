"""Unit tests for RemoteBuildpackChain.

Note: Tests requiring file I/O are in e2e/test_remote_chain.py
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.remote import RemoteBuildpackChain


class TestRemoteBuildpackChainImageExists:
    """Tests for RemoteBuildpackChain.image_exists()."""

    def test_image_exists_returns_true(self, mock_ssh: MagicMock) -> None:
        """image_exists() returns True when grep succeeds."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        assert chain.image_exists("localhost:32000/test:latest") is True

    def test_image_exists_returns_false(self, mock_ssh: MagicMock) -> None:
        """image_exists() returns False when grep fails."""
        mock_ssh.run.return_value = (1, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        assert chain.image_exists("localhost:32000/test:latest") is False

    def test_image_exists_uses_microk8s_ctr(self, mock_ssh: MagicMock) -> None:
        """image_exists() uses microk8s ctr to check containerd registry."""
        mock_ssh.run.return_value = (0, "", "")
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        chain.image_exists("localhost:32000/test:latest")

        mock_ssh.run.assert_called_once()
        call_args = mock_ssh.run.call_args[0][0]
        assert "microk8s ctr image ls" in call_args
        assert "localhost:32000/test:latest" in call_args


class TestRemoteBuildpackChainBuild:
    """Tests for RemoteBuildpackChain.build().

    Note: Tests requiring pyproject.toml are in e2e/test_remote_chain.py
    """

    def test_build_empty_buildpacks_raises(self, mock_ssh: MagicMock) -> None:
        """build() raises BuildpackError for empty buildpack list."""
        chain = RemoteBuildpackChain(
            registry="localhost:32000",
            ssh=mock_ssh,
        )

        with pytest.raises(BuildpackError, match="No buildpacks specified"):
            chain.build([])
