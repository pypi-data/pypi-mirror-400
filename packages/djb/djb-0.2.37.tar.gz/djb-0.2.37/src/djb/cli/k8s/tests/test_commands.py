"""Unit tests for djb deploy k8s commands.

These tests don't require Docker and test command structure, help text,
and argument validation.
"""

from __future__ import annotations

from click.testing import CliRunner

from djb.cli.djb import djb_cli


class TestDeployK8sLocal:
    """Tests for `djb deploy k8s local` subcommands (Skaffold-based)."""

    def test_local_help(self, cli_runner: CliRunner) -> None:
        """Test that local help is displayed."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "--help"])
        assert result.exit_code == 0
        assert "Manage local Kubernetes development with Skaffold" in result.output
        assert "cluster" in result.output
        assert "dev" in result.output
        assert "build" in result.output
        assert "shell" in result.output

    def test_cluster_help(self, cli_runner: CliRunner) -> None:
        """Test that cluster subcommand help is displayed."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "cluster", "--help"])
        assert result.exit_code == 0
        assert "Manage local Kubernetes cluster lifecycle" in result.output
        assert "create" in result.output
        assert "delete" in result.output
        assert "status" in result.output

    def test_cluster_create_help(self, cli_runner: CliRunner) -> None:
        """Test cluster create command options."""
        result = cli_runner.invoke(
            djb_cli, ["deploy", "k8s", "local", "cluster", "create", "--help"]
        )
        assert result.exit_code == 0
        assert "--type" in result.output
        assert "k3d" in result.output
        assert "microk8s" in result.output

    def test_dev_help(self, cli_runner: CliRunner) -> None:
        """Test dev command options."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "local", "dev", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output
        assert "--trigger" in result.output
        assert "notify" in result.output
        assert "polling" in result.output


class TestDeployK8sTerraform:
    """Tests for `djb deploy k8s terraform` command."""

    def test_terraform_help(self, cli_runner: CliRunner) -> None:
        """Test that terraform help is displayed."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "terraform", "--help"])
        assert result.exit_code == 0
        assert "Provision Kubernetes infrastructure" in result.output
        assert "--host" in result.output
        assert "--email" in result.output
        assert "--no-tls" in result.output
        assert "--no-cloudnativepg" in result.output
        assert "--microk8s" in result.output

    def test_terraform_hetzner_options(self, cli_runner: CliRunner) -> None:
        """Test that Hetzner-related options are in terraform help."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "terraform", "--help"])
        assert result.exit_code == 0
        assert "--provider" in result.output
        assert "hetzner" in result.output
        assert "--server-type" in result.output
        assert "--location" in result.output
        assert "--image" in result.output
        assert "--ssh-key-name" in result.output

    def test_terraform_host_and_hetzner_mutually_exclusive(self, cli_runner: CliRunner) -> None:
        """Test that --host and --provider hetzner cannot be used together."""
        result = cli_runner.invoke(
            djb_cli,
            ["deploy", "k8s", "terraform", "--host", "root@server", "--provider", "hetzner"],
        )
        assert result.exit_code != 0
        assert "Cannot use --host with --provider hetzner" in result.output


class TestDeployK8sMaterialize:
    """Tests for `djb deploy k8s materialize` command."""

    def test_materialize_help(self, cli_runner: CliRunner) -> None:
        """Test that materialize help is displayed."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize", "--help"])
        assert result.exit_code == 0
        assert "Create cloud VPS for K8s deployment" in result.output
        assert "--provider" in result.output
        assert "--create" in result.output
        assert "--server-type" in result.output
        assert "--location" in result.output
        assert "--image" in result.output
        assert "--ssh-key-name" in result.output

    def test_materialize_requires_provider(self, cli_runner: CliRunner) -> None:
        """Test that materialize requires --provider option."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_materialize_hetzner_provider(self, cli_runner: CliRunner) -> None:
        """Test that hetzner is a valid provider choice."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "materialize", "--help"])
        assert result.exit_code == 0
        assert "hetzner" in result.output


class TestDeployK8sMainCommand:
    """Tests for `djb deploy k8s` main deployment command."""

    def test_k8s_help(self, cli_runner: CliRunner) -> None:
        """Test that k8s help is displayed."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "--help"])
        assert result.exit_code == 0
        assert "Deploy to Kubernetes" in result.output
        assert "--host" in result.output
        assert "--skip-build" in result.output
        assert "--skip-migrate" in result.output
        # Note: --domain was removed; domains are now configured via k8s.domain_names in config

    def test_k8s_subcommands_available(self, cli_runner: CliRunner) -> None:
        """Test that subcommands are registered."""
        result = cli_runner.invoke(djb_cli, ["deploy", "k8s", "--help"])
        assert result.exit_code == 0
        assert "local" in result.output
        assert "materialize" in result.output
        assert "terraform" in result.output
