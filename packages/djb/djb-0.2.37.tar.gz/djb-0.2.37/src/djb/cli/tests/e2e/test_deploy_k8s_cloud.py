"""E2E tests for djb deploy k8s cloud-related commands.

Tests the Hetzner K8s deployment commands while mocking cloud APIs.
These tests use real file system operations for secrets and config.

Commands tested:
- djb deploy k8s materialize --provider hetzner
- djb deploy k8s domain add/list/remove
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from djb.cli.djb import djb_cli
from djb.cli.tests.e2e.fixtures.project import ProjectWithSecrets
from djb.k8s.cloud import ServerInfo

if TYPE_CHECKING:
    from click.testing import CliRunner
    from collections.abc import Callable

pytestmark = pytest.mark.e2e_marker


class TestMaterializeHetzner:
    """E2E tests for `djb deploy k8s materialize --provider hetzner`."""

    def test_materialize_creates_server(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_hetzner_provider: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Materialize creates a new Hetzner server when no server exists."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-y",
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "Server materialized" in result.output or "1.2.3.4" in result.output
        mock_hetzner_provider.create_server.assert_called_once()
        mock_hetzner_provider.wait_for_server.assert_called_once()

    def test_materialize_reuses_existing_server_from_hetzner(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_hetzner_provider: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Materialize returns existing server if it already exists in Hetzner."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Server already exists in Hetzner (but not in config)
        mock_hetzner_provider.get_server.return_value = ServerInfo(
            name="myproject", ip="5.6.7.8", id=999, status="running"
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-y",
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
            ],
        )

        assert result.exit_code == 0
        assert "5.6.7.8" in result.output or "myproject" in result.output
        mock_hetzner_provider.create_server.assert_not_called()

    def test_materialize_verifies_existing_config(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_hetzner_provider: MagicMock,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Materialize verifies and returns existing server from config."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Configure existing server in .djb/project.toml
        make_config_file(
            {
                "project_name": "myproject",
                "hetzner": {
                    "default_server_type": "cx23",
                    "default_location": "nbg1",
                    "default_image": "ubuntu-24.04",
                    "server_name": "existing-server",
                },
                "k8s": {
                    "provider": "hetzner",
                    "host": "5.6.7.8",
                    "domain_names": {"example.com": {"manager": "manual"}},
                },
            },
            config_type="project",
        )

        # Server exists in Hetzner
        mock_hetzner_provider.get_server.return_value = ServerInfo(
            name="existing-server", ip="5.6.7.8", id=999, status="running"
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
            ],
        )

        assert result.exit_code == 0
        assert "5.6.7.8" in result.output or "verified" in result.output.lower()
        mock_hetzner_provider.create_server.assert_not_called()

    def test_materialize_force_create_replaces_config(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_hetzner_provider: MagicMock,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Materialize --create creates new server and logs restore commands."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Pre-configure an existing server
        make_config_file(
            {
                "project_name": "myproject",
                "hetzner": {
                    "default_server_type": "cx23",
                    "default_location": "nbg1",
                    "default_image": "ubuntu-24.04",
                    "server_name": "myproject-old",
                },
                "k8s": {"provider": "hetzner", "host": "1.1.1.1"},
            },
            config_type="project",
        )

        # Mock: no server with generated name exists in Hetzner
        mock_hetzner_provider.get_server.return_value = None
        mock_hetzner_provider.create_server.return_value = ServerInfo(
            name="myproject", ip="2.2.2.2", id=99999, status="running"
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-y",
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
                "--create",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Server created with new config (2.2.2.2)
        assert "2.2.2.2" in result.output
        mock_hetzner_provider.create_server.assert_called_once()

    def test_materialize_force_create_handles_name_collision(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_hetzner_provider: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Materialize --create generates unique name if collision."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Mock: server with name already exists in Hetzner
        # Return existing server on first call, None on subsequent (for unique name)
        mock_hetzner_provider.get_server.side_effect = [
            ServerInfo(name="myproject", ip="1.1.1.1", id=11111, status="running"),
            None,  # Unique timestamped name doesn't exist
            ServerInfo(name="myproject-1736000000", ip="2.2.2.2", id=22222, status="running"),
        ]
        mock_hetzner_provider.create_server.return_value = ServerInfo(
            name="myproject-1736000000", ip="2.2.2.2", id=22222, status="running"
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "-y",
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
                "--create",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        # Verify create_server was called (not reusing existing)
        mock_hetzner_provider.create_server.assert_called_once()
        # Server materialized with the new IP
        assert "2.2.2.2" in result.output

    def test_materialize_missing_api_token(
        self,
        cli_runner: CliRunner,
        project_dir: Path,
        make_config_file: Callable[..., Path],
    ) -> None:
        """Materialize shows helpful error when API token is missing."""
        # Create project without secrets
        make_config_file(
            {
                "project_name": "myproject",
                "hetzner": {
                    "default_server_type": "cx23",
                    "default_location": "nbg1",
                    "default_image": "ubuntu-24.04",
                },
                "k8s": {"provider": "hetzner"},
            },
            config_type="project",
        )

        # Create pyproject.toml
        (project_dir / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\nversion = "0.1.0"\n\n'
            '[tool.djb]\nproject_name = "myproject"\n'
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "deploy",
                "k8s",
                "materialize",
                "--provider",
                "hetzner",
            ],
        )

        assert result.exit_code != 0
        # Should mention secrets or hetzner api_token
        assert (
            "secrets" in result.output.lower()
            or "api_token" in result.output.lower()
            or "hetzner" in result.output.lower()
        )


class TestDomainCommands:
    """E2E tests for djb domain subcommands."""

    def test_domain_sync_configures_dns(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_cloudflare_provider: MagicMock,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain sync configures Cloudflare DNS for all configured domains."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Add server IP to config with new dict format
        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "hetzner": {
                    "default_server_type": "cx23",
                    "default_location": "nbg1",
                    "default_image": "ubuntu-24.04",
                },
                "k8s": {
                    "host": "1.2.3.4",
                    "domain_names": {"example.com": {"manager": "cloudflare"}},
                },
                "cloudflare": {"ttl": 300, "proxied": False},
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "sync",
            ],
        )

        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "sync complete" in result.output.lower() or "example.com" in result.output
        mock_cloudflare_provider.set_a_record.assert_called()

    def test_domain_sync_dry_run(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        mock_cloudflare_provider: MagicMock,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain sync --dry-run previews changes without making API calls."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {
                    "host": "1.2.3.4",
                    "domain_names": {"example.com": {"manager": "cloudflare"}},
                },
                "cloudflare": {"ttl": 300, "proxied": False},
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "sync",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "would" in result.output.lower() or "dry run" in result.output.lower()
        mock_cloudflare_provider.set_a_record.assert_not_called()

    def test_domain_sync_no_server_ip(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain sync errors when no server IP is available."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Config without server_ip
        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {"domain_names": {"example.com": {"manager": "cloudflare"}}},
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "sync",
            ],
        )

        assert result.exit_code != 0
        assert "no server ip" in result.output.lower() or "provision" in result.output.lower()

    def test_domain_list(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain list shows configured domains with managers."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {
                    "domain_names": {
                        "example.com": {"manager": "cloudflare"},
                        "other.com": {"manager": "manual"},
                    }
                },
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "list",
            ],
        )

        assert result.exit_code == 0
        assert "example.com" in result.output
        assert "other.com" in result.output
        assert "cloudflare" in result.output
        assert "manual" in result.output

    def test_domain_remove(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain remove updates config to remove a domain."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {
                    "domain_names": {
                        "example.com": {"manager": "cloudflare"},
                        "other.com": {"manager": "cloudflare"},
                    }
                },
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "remove",
                "example.com",
            ],
        )

        assert result.exit_code == 0
        assert "removed" in result.output.lower()

    def test_domain_remove_not_found(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain remove errors when domain is not in config."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {"domain_names": {"example.com": {"manager": "cloudflare"}}},
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "remove",
                "nonexistent.com",
            ],
        )

        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_domain_sync_no_domains_configured(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain sync shows info when no domains are configured."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        # Config without domains
        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {"host": "1.2.3.4"},
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "sync",
            ],
        )

        assert result.exit_code == 0
        assert "no domains" in result.output.lower()

    def test_domain_add_new_domain(
        self,
        cli_runner: CliRunner,
        k8s_project: ProjectWithSecrets,
        make_config_file: Callable[..., Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Domain add creates a new domain entry in config."""
        project_dir, key_path = k8s_project
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_path))

        make_config_file(
            {
                "project_name": "myproject",
                "platform": "k8s",
                "k8s": {
                    "host": "1.2.3.4",
                    "domain_names": {"example.com": {"manager": "cloudflare"}},
                },
            },
            config_type="project",
        )

        result = cli_runner.invoke(
            djb_cli,
            [
                "--project-dir",
                str(project_dir),
                "domain",
                "add",
                "extra.com",
                "--manager",
                "cloudflare",
            ],
        )

        assert result.exit_code == 0
        assert "added" in result.output.lower()
        assert "extra.com" in result.output
