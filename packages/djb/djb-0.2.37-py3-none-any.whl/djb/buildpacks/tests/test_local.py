"""Unit tests for LocalBuildpackChain.

Note: Tests requiring file I/O are in e2e/test_local_chain.py
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from djb.buildpacks.constants import BuildpackError
from djb.buildpacks.local import LocalBuildpackChain


class TestLocalBuildpackChainImageExists:
    """Tests for LocalBuildpackChain.image_exists()."""

    def test_image_exists_returns_true(self, mock_cmd_runner: MagicMock) -> None:
        """image_exists() returns True when docker inspect succeeds."""
        mock_cmd_runner.check.return_value = True
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
        )

        assert chain.image_exists("k3d-registry.localhost:5000/test:latest") is True

    def test_image_exists_returns_false(self, mock_cmd_runner: MagicMock) -> None:
        """image_exists() returns False when docker inspect fails."""
        mock_cmd_runner.check.return_value = False
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
        )

        assert chain.image_exists("k3d-registry.localhost:5000/test:latest") is False

    def test_image_exists_uses_docker_inspect(self, mock_cmd_runner: MagicMock) -> None:
        """image_exists() uses docker image inspect."""
        mock_cmd_runner.check.return_value = True
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
        )

        chain.image_exists("k3d-registry.localhost:5000/test:latest")

        mock_cmd_runner.check.assert_called_once()
        call_args = mock_cmd_runner.check.call_args[0][0]
        assert call_args == [
            "docker",
            "image",
            "inspect",
            "k3d-registry.localhost:5000/test:latest",
        ]


class TestLocalBuildpackChainBuild:
    """Tests for LocalBuildpackChain.build().

    Note: Tests requiring pyproject.toml are in e2e/test_local_chain.py
    """

    def test_build_empty_buildpacks_raises(self, mock_cmd_runner: MagicMock) -> None:
        """build() raises BuildpackError for empty buildpack list."""
        chain = LocalBuildpackChain(
            registry="k3d-registry.localhost:5000",
            runner=mock_cmd_runner,
        )

        with pytest.raises(BuildpackError, match="No buildpacks specified"):
            chain.build([])
