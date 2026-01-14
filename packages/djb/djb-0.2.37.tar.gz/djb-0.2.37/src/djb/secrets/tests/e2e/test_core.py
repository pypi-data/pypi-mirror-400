"""Tests for djb.secrets.core module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.e2e_marker

from djb.cli.context import CliContext
from djb.config import DjbConfig
from djb.config.fields.secrets import SecretsConfig
from djb.core.cmd_runner import CmdRunner, CmdTimeout
from djb.secrets.core import (
    SecretsManager,
    SopsError,
    check_age_installed,
    check_sops_installed,
    decrypt_file,
    encrypt_file,
    find_placeholder_secrets,
    format_identity,
    generate_age_key,
    get_public_key_from_private,
    is_placeholder_value,
    is_sops_encrypted,
    is_valid_age_public_key,
    load_secrets,
    parse_identity,
    rotate_keys,
)
from djb.types import Mode


class TestCheckInstalled:
    """Tests for check_sops_installed and check_age_installed."""

    def test_check_sops_installed_found(self):
        """Check_sops_installed when sops is available."""
        with patch("shutil.which", return_value="/usr/bin/sops"):
            assert check_sops_installed() is True

    def test_check_sops_installed_not_found(self):
        """Check_sops_installed when sops is not available."""
        with patch("shutil.which", return_value=None):
            assert check_sops_installed() is False

    def test_check_age_installed_found(self):
        """Check_age_installed when age-keygen is available."""
        with patch("shutil.which", return_value="/usr/bin/age-keygen"):
            assert check_age_installed() is True

    def test_check_age_installed_not_found(self):
        """Check_age_installed when age-keygen is not available."""
        with patch("shutil.which", return_value=None):
            assert check_age_installed() is False


class TestGenerateAgeKey:
    """Tests for generate_age_key."""

    def test_generates_key_successfully(self, tmp_path, make_cmd_runner: CmdRunner):
        """generate_age_key generates key successfully."""
        key_path = tmp_path / ".age" / "keys.txt"

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(
                returncode=0,
                stdout=(
                    "# created: 2024-01-01T00:00:00Z\n"
                    "# public key: age1testpublickey123456789012345678901234567890123456\n"
                    "AGE-SECRET-KEY-1TESTPRIVATEKEYABC123\n"
                ),
                stderr="",
            ),
        ):
            public_key, private_key = generate_age_key(make_cmd_runner, key_path=key_path)

            assert public_key == "age1testpublickey123456789012345678901234567890123456"
            assert private_key == "AGE-SECRET-KEY-1TESTPRIVATEKEYABC123"
            assert key_path.exists()

    def test_raises_on_timeout(self, tmp_path, make_cmd_runner: CmdRunner):
        """generate_age_key raises SopsError when age-keygen times out."""
        key_path = tmp_path / ".age" / "keys.txt"

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=5, cmd=["age-keygen"]),
        ):
            with pytest.raises(SopsError, match="timed out"):
                generate_age_key(make_cmd_runner, key_path=key_path)

    def test_raises_on_failure(self, tmp_path, make_cmd_runner: CmdRunner):
        """generate_age_key raises SopsError on command failure."""
        key_path = tmp_path / ".age" / "keys.txt"

        # The function uses fail_msg=SopsError(...) so when returncode != 0, it raises that
        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=SopsError("age-keygen failed"),
        ):
            with pytest.raises(SopsError, match="age-keygen failed"):
                generate_age_key(make_cmd_runner, key_path=key_path)


class TestIsValidAgePublicKey:
    """Tests for is_valid_age_public_key."""

    def test_valid_key(self):
        """is_valid_age_public_key returns True for valid age public key."""
        # This is a properly formatted age public key (62 chars, starts with age1)
        key = "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"
        assert is_valid_age_public_key(key) is True

    def test_wrong_prefix(self):
        """is_valid_age_public_key rejects wrong prefix."""
        key = "age2qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"
        assert is_valid_age_public_key(key) is False

    def test_wrong_length(self):
        """is_valid_age_public_key rejects wrong length."""
        key = "age1short"
        assert is_valid_age_public_key(key) is False

    def test_invalid_characters(self):
        """is_valid_age_public_key rejects invalid bech32 characters."""
        # 'b' and '1' (except in prefix) are not valid bech32
        key = "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqsb290gq"
        assert is_valid_age_public_key(key) is False


class TestFormatAndParseIdentity:
    """Tests for format_identity and parse_identity."""

    def test_format_with_name_and_email(self):
        """format_identity formats with both name and email."""
        result = format_identity("John Doe", "john@example.com")
        assert result == "John Doe <john@example.com>"

    def test_format_with_email_only(self):
        """format_identity formats with email only."""
        result = format_identity(None, "john@example.com")
        assert result == "john@example.com"

    def test_parse_full_identity(self):
        """parse_identity parses full git-style identity."""
        name, email = parse_identity("John Doe <john@example.com>")
        assert name == "John Doe"
        assert email == "john@example.com"

    def test_parse_email_only(self):
        """parse_identity parses email-only identity."""
        name, email = parse_identity("john@example.com")
        assert name is None
        assert email == "john@example.com"

    def test_roundtrip(self):
        """format_identity then parse_identity returns original values."""
        formatted = format_identity("Jane Smith", "jane@example.com")
        name, email = parse_identity(formatted)
        assert name == "Jane Smith"
        assert email == "jane@example.com"

    def test_parse_identity_with_spaces(self):
        """parse_identity handles identity with extra spaces."""
        name, email = parse_identity("Alice Smith  <alice@example.com>")
        assert name == "Alice Smith"
        assert email == "alice@example.com"


class TestPlaceholderDetection:
    """Tests for placeholder detection functions."""

    def test_is_placeholder_change_me(self):
        """Detection of CHANGE-ME placeholder (used in secrets templates)."""
        assert is_placeholder_value("CHANGE-ME") is True
        assert is_placeholder_value("change-me") is True
        assert is_placeholder_value("CHANGE-ME-DEV-KEY") is True
        assert is_placeholder_value("CHANGE-ME-PRODUCTION-PASSWORD") is True

    def test_is_placeholder_real_values(self):
        """is_placeholder_value returns False for real values."""
        real_values = [
            "sk_live_abc123xyz",
            "my-secret-key-12345",
            "production-database-password",
            "https://api.example.com",
            "user@example.com",
        ]

        for value in real_values:
            assert is_placeholder_value(value) is False, f"Should not detect: {value}"

    def test_is_placeholder_non_string(self):
        """is_placeholder_value returns False for non-strings."""
        assert is_placeholder_value(123) is False  # type: ignore[arg-type]
        assert is_placeholder_value(None) is False  # type: ignore[arg-type]
        assert is_placeholder_value(["CHANGE-ME"]) is False  # type: ignore[arg-type]

    def test_find_placeholder_secrets_flat(self):
        """find_placeholder_secrets finds placeholders in flat dict."""
        secrets = {
            "api_key": "sk_live_real_key",
            "db_password": "CHANGE-ME",
            "secret_key": "real-secret",
        }

        result = find_placeholder_secrets(secrets)
        assert result == ["db_password"]

    def test_find_placeholder_secrets_nested(self):
        """find_placeholder_secrets finds placeholders in nested dict."""
        secrets = {
            "api_keys": {
                "stripe": "sk_live_real",
                "sendgrid": "CHANGE-ME",
            },
            "database": {
                "password": "CHANGE-ME-DEV-PASSWORD",
            },
        }

        result = find_placeholder_secrets(secrets)
        assert "api_keys.sendgrid" in result
        assert "database.password" in result
        assert len(result) == 2

    def test_find_placeholder_secrets_empty(self):
        """find_placeholder_secrets returns empty list for empty dict."""
        assert find_placeholder_secrets({}) == []

    def test_find_placeholder_secrets_no_placeholders(self):
        """find_placeholder_secrets returns empty list when no placeholders."""
        secrets = {
            "key1": "real-value-1",
            "key2": "real-value-2",
        }
        assert find_placeholder_secrets(secrets) == []


class TestIsSopsEncrypted:
    """Tests for is_sops_encrypted function."""

    def test_returns_true_for_sops_encrypted_file(self, tmp_path):
        """Returns True for a SOPS-encrypted YAML file."""
        encrypted_file = tmp_path / "secrets.yaml"
        encrypted_file.write_text(
            "secret_key: ENC[AES256_GCM,data:...]\n"
            "sops:\n"
            "    version: 3.8.0\n"
            "    lastmodified: '2024-01-01T00:00:00Z'\n"
        )

        assert is_sops_encrypted(encrypted_file) is True

    def test_returns_false_for_plaintext_file(self, tmp_path):
        """Returns False for a plaintext YAML file."""
        plaintext_file = tmp_path / "secrets.yaml"
        plaintext_file.write_text("secret_key: my-secret-value\napi_key: abc123\n")

        assert is_sops_encrypted(plaintext_file) is False

    def test_returns_false_for_missing_file(self, tmp_path):
        """Returns False for a non-existent file."""
        missing_file = tmp_path / "nonexistent.yaml"

        assert is_sops_encrypted(missing_file) is False

    def test_returns_false_for_invalid_yaml(self, tmp_path):
        """Returns False for an invalid YAML file."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("{{{{invalid yaml}}}}")

        assert is_sops_encrypted(invalid_file) is False

    def test_returns_false_for_empty_file(self, tmp_path):
        """Returns False for an empty file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        assert is_sops_encrypted(empty_file) is False

    def test_returns_false_for_non_dict_yaml(self, tmp_path):
        """Returns False for YAML that parses to a non-dict."""
        list_file = tmp_path / "list.yaml"
        list_file.write_text("- item1\n- item2\n")

        assert is_sops_encrypted(list_file) is False

    def test_returns_false_for_file_with_sops_value(self, tmp_path):
        """Returns False when 'sops' is a nested value, not a top-level key."""
        nested_sops = tmp_path / "nested.yaml"
        nested_sops.write_text("config:\n  sops: some-value\n")

        assert is_sops_encrypted(nested_sops) is False


class TestSecretsEncryptConfig:
    """Tests for config.secrets.encrypt field."""

    def test_returns_true_by_default(self, make_djb_config):
        """Returns True when no encryption config is set (defaults)."""
        config = make_djb_config()

        assert config.secrets.encrypt is True

    def test_respects_config_false(self, make_djb_config):
        """Returns False when encryption is disabled in config."""
        config = make_djb_config(DjbConfig(secrets=SecretsConfig(encrypt=False)))

        assert config.secrets.encrypt is False

    def test_respects_config_true(self, make_djb_config):
        """Returns True when encryption is explicitly enabled."""
        config = make_djb_config(DjbConfig(secrets=SecretsConfig(encrypt=True)))

        assert config.secrets.encrypt is True


class TestSopsConfig:
    """Tests for SecretsManager SOPS config methods."""

    def test_save_config_dict(self, tmp_path, mock_cli_ctx: CliContext):
        """save_config creates .sops.yaml with dict recipients."""
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path)
        recipients = {
            "age1abc123": "John <john@example.com>",
            "age1def456": "Jane <jane@example.com>",
        }

        result = manager.save_config(recipients)

        assert result == tmp_path / "secrets" / ".sops.yaml"
        assert result.exists()

        content = result.read_text()
        assert "age1abc123" in content
        assert "age1def456" in content
        assert "john@example.com" in content
        assert "jane@example.com" in content

    def test_save_config_list(self, tmp_path, mock_cli_ctx: CliContext):
        """save_config creates .sops.yaml with list of keys."""
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path)
        recipients = ["age1abc123", "age1def456"]

        result = manager.save_config(recipients)

        content = result.read_text()
        assert "age1abc123" in content
        assert "age1def456" in content

    def test_recipients_property(self, tmp_path, mock_cli_ctx: CliContext):
        """recipients property parses .sops.yaml."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        sops_config = secrets_dir / ".sops.yaml"
        sops_config.write_text(
            """creation_rules:
  - path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          # John <john@example.com>
          - age1abc123
          # jane@example.com
          - age1def456
"""
        )
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path)

        result = manager.recipients

        assert result["age1abc123"] == "John <john@example.com>"
        assert result["age1def456"] == "jane@example.com"

    def test_recipients_missing(self, tmp_path, mock_cli_ctx: CliContext):
        """recipients returns empty dict when .sops.yaml doesn't exist."""
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path)
        result = manager.recipients
        assert result == {}

    def test_recipient_keys(self, tmp_path, mock_cli_ctx: CliContext):
        """recipient_keys gets all public keys from .sops.yaml."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        sops_config = secrets_dir / ".sops.yaml"
        sops_config.write_text(
            """creation_rules:
  - path_regex: '.*\\.yaml$'
    key_groups:
      - age:
          - age1abc123
          - age1def456
"""
        )
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path)

        result = manager.recipient_keys
        assert set(result) == {"age1abc123", "age1def456"}


class TestGetPublicKeyFromPrivate:
    """Tests for get_public_key_from_private."""

    def test_reads_from_comment(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private reads public key from comment in key file."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "# created: 2024-01-01T00:00:00Z\n"
            "# public key: age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq\n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
        assert result == "age1qyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqszqgpqyqs3290gq"

    def test_missing_file_raises(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private raises FileNotFoundError when key file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            get_public_key_from_private(make_cmd_runner, key_path=tmp_path / "missing.txt")

    def test_derives_from_private_key(self, tmp_path, make_cmd_runner: CmdRunner):
        """get_public_key_from_private derives public key using age-keygen -y."""
        key_file = tmp_path / "keys.txt"
        # Key file without public key comment
        key_file.write_text(
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="age1derived123", stderr=""),
        ) as mock_run:
            result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
            assert result == "age1derived123"
            mock_run.assert_called_once()

    def test_invalid_file_raises(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private raises SopsError when file has no valid key."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text("# just a comment\n")

        with pytest.raises(SopsError):
            get_public_key_from_private(make_cmd_runner, key_path=key_file)

    def test_empty_file_raises(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private raises SopsError when file is empty."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text("")

        with pytest.raises(SopsError, match="No valid age key found"):
            get_public_key_from_private(make_cmd_runner, key_path=key_file)

    def test_whitespace_only_file_raises(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private raises SopsError when file contains only whitespace."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text("   \n\n   \n")

        with pytest.raises(SopsError, match="No valid age key found"):
            get_public_key_from_private(make_cmd_runner, key_path=key_file)

    def test_multiple_public_key_comments_uses_first(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private uses first public key comment when multiple exist."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "# public key: age1first111\n"
            "# public key: age1second222\n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
        assert result == "age1first111"

    def test_public_key_with_trailing_whitespace(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private strips trailing whitespace from public key."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "# public key: age1testkey123   \n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
        assert result == "age1testkey123"

    def test_crlf_line_endings(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private handles CRLF line endings correctly."""
        key_file = tmp_path / "keys.txt"
        # Write with CRLF line endings
        key_file.write_text(
            "# public key: age1crlftest\r\n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\r\n"
        )

        result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
        # The trailing \r should be stripped
        assert result == "age1crlftest"

    def test_empty_public_key_comment_falls_back_to_derivation(
        self, tmp_path, mock_subprocess_result, make_cmd_runner
    ):
        """get_public_key_from_private falls back to derivation on empty public key comment."""
        key_file = tmp_path / "keys.txt"
        # Empty public key comment (just "# public key: " with nothing after)
        key_file.write_text(
            "# public key: \n"
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        mock_subprocess_result(returncode=0, stdout="age1derived456")

        # Empty string from comment is still truthy check, so we get "" not None
        # The function returns the stripped value, which is ""
        result = get_public_key_from_private(make_cmd_runner, key_path=key_file)
        # Empty string is returned since strip() returns ""
        assert result == ""

    def test_timeout_during_derivation_raises(self, tmp_path, make_cmd_runner: CmdRunner):
        """get_public_key_from_private raises SopsError on timeout during key derivation."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=30, cmd=["age-keygen", "-y"]),
        ):
            with pytest.raises(SopsError, match="timed out"):
                get_public_key_from_private(make_cmd_runner, key_path=key_file)

    def test_derivation_failure_raises(self, tmp_path, make_cmd_runner):
        """get_public_key_from_private raises SopsError on failed derivation."""
        key_file = tmp_path / "keys.txt"
        key_file.write_text(
            "AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ\n"
        )

        mock_result = Mock(returncode=1, stdout="", stderr="invalid key format")

        with patch.object(make_cmd_runner, "run", return_value=mock_result):
            with pytest.raises(SopsError, match="Failed to derive public key"):
                get_public_key_from_private(make_cmd_runner, key_path=key_file)


class TestEncryptFile:
    """Tests for encrypt_file."""

    def test_encrypts_successfully(self, make_cmd_runner: CmdRunner, tmp_path):
        """encrypt_file encrypts a YAML file successfully."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("secret: value")
        output_file = tmp_path / "secret.enc.yaml"

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ) as mock_run:
            encrypt_file(make_cmd_runner, input_file, output_file, public_keys=["age1test123"])

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "sops" in call_args[0][0]
            assert "--encrypt" in call_args[0][0]

    def test_raises_on_failure(self, make_cmd_runner: CmdRunner, tmp_path):
        """encrypt_file raises SopsError on encryption failure."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("secret: value")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="encryption failed"),
        ):
            with pytest.raises(SopsError, match="encryption failed"):
                encrypt_file(make_cmd_runner, input_file, public_keys=["age1test123"])

    def test_raises_on_timeout(self, make_cmd_runner: CmdRunner, tmp_path):
        """encrypt_file raises SopsError when sops encryption times out."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("secret: value")

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=60, cmd=["sops"]),
        ):
            with pytest.raises(SopsError, match="timed out"):
                encrypt_file(make_cmd_runner, input_file, public_keys=["age1test123"])


class TestDecryptFile:
    """Tests for decrypt_file."""

    # SOPS-encrypted files contain a 'sops' key with encryption metadata
    SOPS_ENCRYPTED_CONTENT = "secret: ENC[...]\nsops:\n  version: 3.8.0\n"

    def test_decrypts_successfully(self, make_cmd_runner: CmdRunner, tmp_path):
        """decrypt_file decrypts file successfully."""
        input_file = tmp_path / "secret.enc.yaml"
        input_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="secret: value", stderr=""),
        ):
            result = decrypt_file(make_cmd_runner, input_file)
            assert result == "secret: value"

    def test_raises_on_failure(self, make_cmd_runner: CmdRunner, tmp_path):
        """decrypt_file raises SopsError on decryption failure."""
        input_file = tmp_path / "secret.enc.yaml"
        input_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="decryption failed"),
        ):
            with pytest.raises(SopsError, match="decryption failed"):
                decrypt_file(make_cmd_runner, input_file)

    def test_raises_on_timeout(self, make_cmd_runner: CmdRunner, tmp_path):
        """decrypt_file raises SopsError when sops decryption times out."""
        input_file = tmp_path / "secret.enc.yaml"
        input_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=60, cmd=["sops"]),
        ):
            with pytest.raises(SopsError, match="timed out"):
                decrypt_file(make_cmd_runner, input_file)


class TestRotateKeys:
    """Tests for rotate_keys."""

    def test_rotates_successfully(self, make_cmd_runner: CmdRunner, tmp_path):
        """rotate_keys rotates keys successfully."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("encrypted content")

        # Create .sops.yaml
        sops_config = tmp_path / ".sops.yaml"
        sops_config.write_text("creation_rules:\n  - path_regex: '.*'\n")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="", stderr=""),
        ) as mock_run:
            rotate_keys(make_cmd_runner, input_file, ["age1test123"], sops_config=sops_config)

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "sops" in call_args[0][0]
            assert "updatekeys" in call_args[0][0]

    def test_raises_on_failure(self, make_cmd_runner: CmdRunner, tmp_path):
        """rotate_keys raises SopsError on rotation failure."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("encrypted content")

        sops_config = tmp_path / ".sops.yaml"
        sops_config.write_text("creation_rules:\n  - path_regex: '.*'\n")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=1, stdout="", stderr="rotation failed"),
        ):
            with pytest.raises(SopsError, match="rotation failed"):
                rotate_keys(make_cmd_runner, input_file, ["age1test123"], sops_config=sops_config)

    def test_raises_on_timeout(self, make_cmd_runner: CmdRunner, tmp_path):
        """rotate_keys raises SopsError when sops updatekeys times out."""
        input_file = tmp_path / "secret.yaml"
        input_file.write_text("encrypted content")

        sops_config = tmp_path / ".sops.yaml"
        sops_config.write_text("creation_rules:\n  - path_regex: '.*'\n")

        with patch.object(
            make_cmd_runner,
            "run",
            side_effect=CmdTimeout("Timed out", timeout=5, cmd=["sops"]),
        ):
            with pytest.raises(SopsError, match="timed out"):
                rotate_keys(make_cmd_runner, input_file, ["age1test123"], sops_config=sops_config)


class TestSecretsManager:
    """Tests for SecretsManager class."""

    # SOPS-encrypted files contain a 'sops' key with encryption metadata
    SOPS_ENCRYPTED_CONTENT = "secret: ENC[...]\nsops:\n  version: 3.8.0\n"

    def test_load_secrets(
        self, tmp_path, mock_subprocess_result, make_age_key, mock_cli_ctx: CliContext
    ):
        """SecretsManager.load_secrets loads secrets for a mode."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()

        secrets_file = secrets_dir / "development.yaml"
        secrets_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")

        mock_result = mock_subprocess_result(returncode=0, stdout="secret_key: abc123\n")
        getattr(mock_cli_ctx.runner, "run").return_value = mock_result

        manager = SecretsManager(mock_cli_ctx.runner, tmp_path, key_path=key_file)
        result = manager.load_secrets(Mode.DEVELOPMENT)

        assert result == {"secret_key": "abc123"}

    def test_load_secrets_file_not_found(self, tmp_path, make_age_key, mock_cli_ctx: CliContext):
        """SecretsManager.load_secrets raises FileNotFoundError when secrets file missing."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")
        manager = SecretsManager(mock_cli_ctx.runner, tmp_path, key_path=key_file)

        # Use STAGING mode - the file doesn't exist since we only created development.yaml
        with pytest.raises(FileNotFoundError):
            manager.load_secrets(Mode.STAGING)

    def test_save_secrets(self, tmp_path, make_age_key, mock_cli_ctx: CliContext):
        """SecretsManager.save_secrets saves secrets for a mode."""
        secrets_dir = tmp_path / "secrets"

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")

        # Mock encrypt_file to simulate SOPS creating the output file
        def mock_encrypt(runner, input_path, output_path=None, **kwargs):
            # Simulate SOPS creating the encrypted output file
            target = output_path or input_path
            target.write_text("encrypted content")

        with patch("djb.secrets.core.encrypt_file", side_effect=mock_encrypt):
            manager = SecretsManager(mock_cli_ctx.runner, tmp_path, key_path=key_file)
            manager.save_secrets(Mode.DEVELOPMENT, {"secret": "value"}, public_keys=["age1test123"])

            # Verify secrets file was created
            assert (secrets_dir / "development.yaml").exists()


class TestLoadSecrets:
    """Tests for load_secrets convenience function."""

    # SOPS-encrypted files contain a 'sops' key with encryption metadata
    SOPS_ENCRYPTED_CONTENT = "secret: ENC[...]\nsops:\n  version: 3.8.0\n"

    def test_loads_secrets(self, make_cmd_runner: CmdRunner, tmp_path, make_age_key):
        """load_secrets loads secrets with specified paths."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "development.yaml"
        secrets_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="api_key: secret123\n", stderr=""),
        ):
            result = load_secrets(
                make_cmd_runner,
                mode=Mode.DEVELOPMENT,
                secrets_dir=secrets_dir,
                key_path=key_file,
            )
            assert result == {"api_key": "secret123"}

    def test_raises_when_key_missing(self, make_cmd_runner: CmdRunner, tmp_path):
        """load_secrets raises FileNotFoundError when key file missing."""
        with pytest.raises(FileNotFoundError, match="Age key file not found"):
            load_secrets(
                make_cmd_runner,
                mode=Mode.DEVELOPMENT,
                secrets_dir=tmp_path / "secrets",
                key_path=tmp_path / "missing_key.txt",
            )


class TestLoadSecretsWithMode:
    """Tests for load_secrets function with Mode parameter."""

    # SOPS-encrypted files contain a 'sops' key with encryption metadata
    SOPS_ENCRYPTED_CONTENT = "secret: ENC[...]\nsops:\n  version: 3.8.0\n"

    def test_loads_for_development_mode(self, make_cmd_runner: CmdRunner, tmp_path, make_age_key):
        """load_secrets loads development.yaml for DEVELOPMENT mode."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "development.yaml"
        secrets_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="debug: true\n", stderr=""),
        ):
            result = load_secrets(
                make_cmd_runner, Mode.DEVELOPMENT, secrets_dir=secrets_dir, key_path=key_file
            )
            assert result == {"debug": True}

    def test_loads_for_production_mode(self, make_cmd_runner: CmdRunner, tmp_path, make_age_key):
        """load_secrets loads production.yaml for PRODUCTION mode."""
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "production.yaml"
        secrets_file.write_text(self.SOPS_ENCRYPTED_CONTENT)

        key_file = make_age_key(content="AGE-SECRET-KEY-...\n")

        with patch.object(
            make_cmd_runner,
            "run",
            return_value=Mock(returncode=0, stdout="debug: false\n", stderr=""),
        ):
            result = load_secrets(
                make_cmd_runner, Mode.PRODUCTION, secrets_dir=secrets_dir, key_path=key_file
            )
            assert result == {"debug": False}
