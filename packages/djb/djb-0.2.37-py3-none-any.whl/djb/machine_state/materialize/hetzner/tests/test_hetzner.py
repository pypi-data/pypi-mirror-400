"""Unit tests for Hetzner MachineStates.

These tests mock the HetznerCloudProvider and config to test state behavior.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from djb.config import DjbConfig, HetznerConfig, K8sConfig
from djb.machine_state.materialize.hetzner import (
    HetznerServerExists,
    HetznerServerNameSet,
    HetznerServerRunning,
    HetznerSSHKeyResolved,
    HetznerVPSMaterialized,
)
from djb.machine_state.materialize.hetzner.helpers import generate_server_name
from djb.machine_state.materialize.hetzner.states import HetznerMaterializeOptions
from djb.machine_state.materialize.ssh_key import extract_email_from_public_key
from djb.types import K8sProvider, Mode


# =============================================================================
# Test Fixtures
# =============================================================================


def make_mock_secrets() -> MagicMock:
    """Create a mock SecretsManager for testing."""
    mock_secrets = MagicMock()
    mock_secrets.load_secrets.return_value = {
        "hetzner": {"api_token": "test_token_xxx"},
    }
    return mock_secrets


def make_mock_server(
    name: str = "testproject-staging",
    ip: str = "116.203.1.1",
    status: str = "running",
    server_id: int = 12345,
) -> MagicMock:
    """Create a mock ServerInfo for testing."""
    mock_server = MagicMock()
    mock_server.name = name
    mock_server.ip = ip
    mock_server.status = status
    mock_server.id = server_id
    return mock_server


# =============================================================================
# HetznerSSHKeyResolved Tests
# =============================================================================


class TestHetznerSSHKeyResolved:
    """Tests for HetznerSSHKeyResolved state."""

    def test_describe(self, mock_machine_context) -> None:
        """describe() returns expected string."""
        state = HetznerSSHKeyResolved()
        ctx = mock_machine_context(secrets=make_mock_secrets())

        assert state.describe(ctx) == "Hetzner SSH key"

    def test_check_true_when_ssh_key_set(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns True when ssh_key_name is set."""
        state = HetznerSSHKeyResolved()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(ssh_key_name="my-ssh-key"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is True

    def test_check_false_when_ssh_key_not_set(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns False when ssh_key_name is None."""
        state = HetznerSSHKeyResolved()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(ssh_key_name=None),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is False

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_satisfy_resolves_single_key(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """satisfy() auto-selects single SSH key."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_ssh_keys_with_details.return_value = [
            ("my-only-key", "ssh-ed25519 AAAA... test@example.com")
        ]

        state = HetznerSSHKeyResolved()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(ssh_key_name=None),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        config.set.assert_called_with("hetzner.ssh_key_name", "my-only-key")


# =============================================================================
# HetznerServerNameSet Tests
# =============================================================================


class TestHetznerServerNameSet:
    """Tests for HetznerServerNameSet state."""

    def test_describe(self, mock_machine_context) -> None:
        """describe() returns expected string."""
        state = HetznerServerNameSet()
        ctx = mock_machine_context(secrets=make_mock_secrets())

        assert state.describe(ctx) == "Hetzner server name"

    def test_check_true_when_server_name_set(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns True when server_name is set."""
        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is True

    def test_check_false_when_server_name_not_set(
        self, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns False when server_name is None."""
        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name=None),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is False

    def test_check_false_when_force_create(self, mock_djb_config, mock_machine_context) -> None:
        """check() returns False when force_create is True."""
        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="existing-server"),
            )
        )
        options = HetznerMaterializeOptions(force_create=True)
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets(), options=options)

        assert state.check(ctx) is False

    def test_satisfy_generates_staging_name(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() generates name with mode suffix for staging."""
        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                project_name="myapp",
                mode=Mode.STAGING,
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        config.set.assert_called_with("hetzner.server_name", "myapp-staging")

    def test_satisfy_generates_production_name(self, mock_djb_config, mock_machine_context) -> None:
        """satisfy() generates name without suffix for production."""
        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                project_name="myapp",
                mode=Mode.PRODUCTION,
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        config.set.assert_called_with("hetzner.server_name", "myapp")

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    @patch("djb.machine_state.materialize.hetzner.states.time")
    def test_satisfy_generates_unique_name_when_force_create_and_server_exists(
        self,
        mock_time: MagicMock,
        mock_create_provider: MagicMock,
        mock_djb_config,
        mock_machine_context,
    ) -> None:
        """satisfy() appends timestamp when force_create and server exists in Hetzner."""
        mock_time.time.return_value = 1704067200  # 2024-01-01 00:00:00
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = make_mock_server(name="myapp-staging")

        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                project_name="myapp",
                mode=Mode.STAGING,
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
            )
        )
        options = HetznerMaterializeOptions(force_create=True)
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets(), options=options)

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        mock_provider.get_server.assert_called_once_with("myapp-staging")
        config.set.assert_called_with("hetzner.server_name", "myapp-staging-1704067200")

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_satisfy_uses_base_name_when_force_create_and_server_not_exists(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """satisfy() uses base name when force_create but no server exists in Hetzner."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = None  # Server doesn't exist

        state = HetznerServerNameSet()
        config = mock_djb_config(
            DjbConfig(
                project_name="myapp",
                mode=Mode.STAGING,
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
            )
        )
        options = HetznerMaterializeOptions(force_create=True)
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets(), options=options)

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        mock_provider.get_server.assert_called_once_with("myapp-staging")
        config.set.assert_called_with("hetzner.server_name", "myapp-staging")


# =============================================================================
# HetznerServerExists Tests
# =============================================================================


class TestHetznerServerExists:
    """Tests for HetznerServerExists state."""

    def test_describe_with_name(self, mock_djb_config, mock_machine_context) -> None:
        """describe() includes server name when set."""
        state = HetznerServerExists()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.describe(ctx) == "Hetzner server 'testproject-staging'"

    def test_describe_without_name(self, mock_djb_config, mock_machine_context) -> None:
        """describe() uses generic description when name not set."""
        state = HetznerServerExists()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name=None),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.describe(ctx) == "Hetzner server"

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_check_true_when_server_exists(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns True when server exists in Hetzner Cloud."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = make_mock_server(ip="116.203.1.1")

        state = HetznerServerExists()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER, host="116.203.1.1"),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is True

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_check_false_when_server_not_found(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns False when server doesn't exist."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = None

        state = HetznerServerExists()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is False

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_satisfy_creates_server(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """satisfy() creates server via Hetzner API."""
        mock_provider = mock_create_provider.return_value
        # First call (check) returns None, second call (satisfy) returns the new server
        mock_provider.get_server.return_value = None
        mock_provider.create_server.return_value = make_mock_server()

        state = HetznerServerExists()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging", ssh_key_name="my-ssh-key"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        mock_provider.create_server.assert_called_once_with(
            name="testproject-staging",
            server_type="cx23",
            location="nbg1",
            image="ubuntu-24.04",
            ssh_key_name="my-ssh-key",
        )


# =============================================================================
# HetznerServerRunning Tests
# =============================================================================


class TestHetznerServerRunning:
    """Tests for HetznerServerRunning state."""

    def test_describe_with_name(self, mock_djb_config, mock_machine_context) -> None:
        """describe() includes server name when set."""
        state = HetznerServerRunning()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.describe(ctx) == "Hetzner server 'testproject-staging' running"

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_check_true_when_running(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns True when server status is 'running'."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = make_mock_server(status="running")

        state = HetznerServerRunning()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is True

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_check_false_when_not_running(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """check() returns False when server status is not 'running'."""
        mock_provider = mock_create_provider.return_value
        mock_provider.get_server.return_value = make_mock_server(status="initializing")

        state = HetznerServerRunning()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        assert state.check(ctx) is False

    @patch("djb.machine_state.materialize.hetzner.states.create_hetzner_provider")
    def test_satisfy_waits_for_server(
        self, mock_create_provider: MagicMock, mock_djb_config, mock_machine_context
    ) -> None:
        """satisfy() calls wait_for_server with timeout."""
        mock_provider = mock_create_provider.return_value
        mock_provider.wait_for_server.return_value = make_mock_server()

        state = HetznerServerRunning()
        config = mock_djb_config(
            DjbConfig(
                k8s=K8sConfig(provider=K8sProvider.HETZNER),
                hetzner=HetznerConfig(server_name="testproject-staging"),
            )
        )
        ctx = mock_machine_context(config=config, secrets=make_mock_secrets())

        task = state.satisfy(ctx)
        result = task.run()

        assert result.success is True
        mock_provider.wait_for_server.assert_called_once_with("testproject-staging", timeout=300)


# =============================================================================
# HetznerVPSMaterialized Composite Tests
# =============================================================================


class TestHetznerVPSMaterialized:
    """Tests for HetznerVPSMaterialized composite state."""

    def test_has_substates(self) -> None:
        """Composite state has expected substates."""
        assert "ssh_key_resolved" in HetznerVPSMaterialized._substates
        assert "server_name_set" in HetznerVPSMaterialized._substates
        assert "server_exists" in HetznerVPSMaterialized._substates
        assert "server_running" in HetznerVPSMaterialized._substates

    def test_describe(self, mock_machine_context) -> None:
        """describe() derives from class name."""
        state = HetznerVPSMaterialized()
        ctx = mock_machine_context(secrets=make_mock_secrets())

        # Derived from class name by metaclass (lowercased, spaces inserted)
        assert state.describe(ctx) == "Hetzner VPS materialized"


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestGenerateServerName:
    """Tests for generate_server_name helper."""

    def test_staging_mode_appends_mode(self, mock_djb_config) -> None:
        """Staging mode appends -staging suffix."""
        config = mock_djb_config(DjbConfig(project_name="myapp", mode=Mode.STAGING))

        result = generate_server_name(config)

        assert result == "myapp-staging"

    def test_production_mode_no_suffix(self, mock_djb_config) -> None:
        """Production mode uses project name only."""
        config = mock_djb_config(DjbConfig(project_name="myapp", mode=Mode.PRODUCTION))

        result = generate_server_name(config)

        assert result == "myapp"

    def test_development_mode_appends_mode(self, mock_djb_config) -> None:
        """Development mode appends -development suffix."""
        config = mock_djb_config(DjbConfig(project_name="myapp", mode=Mode.DEVELOPMENT))

        result = generate_server_name(config)

        assert result == "myapp-development"


class TestExtractEmailFromPublicKey:
    """Tests for extract_email_from_public_key helper."""

    def test_extracts_email_from_valid_key(self) -> None:
        """Extracts email from SSH public key comment."""
        public_key = "ssh-ed25519 AAAA... user@example.com"

        result = extract_email_from_public_key(public_key)

        assert result == "user@example.com"

    def test_returns_none_for_no_comment(self) -> None:
        """Returns None when no comment in public key."""
        public_key = "ssh-ed25519 AAAA..."

        result = extract_email_from_public_key(public_key)

        assert result is None

    def test_returns_none_for_non_email_comment(self) -> None:
        """Returns None when comment is not an email."""
        public_key = "ssh-ed25519 AAAA... my-laptop-key"

        result = extract_email_from_public_key(public_key)

        assert result is None

    def test_returns_none_for_none(self) -> None:
        """Returns None for None input."""
        result = extract_email_from_public_key(None)

        assert result is None

    def test_normalizes_to_lowercase(self) -> None:
        """Returns email in lowercase."""
        public_key = "ssh-ed25519 AAAA... User@Example.COM"

        result = extract_email_from_public_key(public_key)

        assert result == "user@example.com"
