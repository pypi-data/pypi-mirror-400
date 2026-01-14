"""Unit tests for djb.secrets.protected module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import click
import pytest

pytestmark = pytest.mark.e2e_marker

from djb.cli.context import CliContext
from djb.secrets import (
    GPG_INTERACTIVE_TIMEOUT,
    GpgTimeoutError,
    ProtectedFileError,
    is_age_key_protected,
    protect_age_key,
    protected_age_key,
    unprotect_age_key,
)


# GPG functions are imported at module level in protected.py, so we patch
# them at djb.secrets.protected (where they're used), not djb.secrets.gpg.
PROTECTED_MODULE = "djb.secrets.protected"


class TestIsAgeKeyProtected:
    """Tests for is_age_key_protected."""

    def test_returns_true_when_gpg_file_exists(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """is_age_key_protected returns True when .gpg file exists and is encrypted."""
        make_age_key(protected=True, gpg_content="encrypted content")

        with patch(f"{PROTECTED_MODULE}.is_gpg_encrypted", return_value=True):
            assert is_age_key_protected(tmp_path, mock_cli_ctx.runner) is True

    def test_returns_false_when_gpg_file_missing(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """is_age_key_protected returns False when .gpg file doesn't exist."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()

        assert is_age_key_protected(tmp_path, mock_cli_ctx.runner) is False

    def test_returns_false_when_file_not_encrypted(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """is_age_key_protected returns False when file exists but isn't GPG encrypted."""
        make_age_key(protected=True, gpg_content="not actually encrypted")

        with patch(f"{PROTECTED_MODULE}.is_gpg_encrypted", return_value=False):
            assert is_age_key_protected(tmp_path, mock_cli_ctx.runner) is False


class TestProtectAgeKey:
    """Tests for protect_age_key."""

    def test_encrypts_plaintext_key(self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext):
        """protect_age_key encrypts existing plaintext key."""
        key_file = make_age_key()

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=True):
            with patch(f"{PROTECTED_MODULE}.gpg_encrypt_file") as mock_encrypt:
                result = protect_age_key(tmp_path, mock_cli_ctx.runner)

                assert result is True
                mock_encrypt.assert_called_once()
                # Key file should be deleted after encryption
                assert not key_file.exists()

    def test_returns_false_when_already_protected(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """protect_age_key returns False when key is already protected."""
        make_age_key(protected=True)

        result = protect_age_key(tmp_path, mock_cli_ctx.runner)
        assert result is False

    def test_returns_false_when_no_key_exists(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """protect_age_key returns False when no key file exists."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()

        result = protect_age_key(tmp_path, mock_cli_ctx.runner)
        assert result is False

    def test_raises_when_gpg_not_installed(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """protect_age_key raises ProtectedFileError when GPG not installed."""
        make_age_key()

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=False):
            with pytest.raises(ProtectedFileError, match="GPG is not installed"):
                protect_age_key(tmp_path, mock_cli_ctx.runner)


class TestUnprotectAgeKey:
    """Tests for unprotect_age_key."""

    def test_decrypts_protected_key(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """unprotect_age_key decrypts GPG-protected key."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()
        gpg_file = age_dir / "keys.txt.gpg"
        gpg_file.write_text("encrypted")
        key_file = age_dir / "keys.txt"

        with patch(f"{PROTECTED_MODULE}.gpg_decrypt_file") as mock_decrypt:
            # Simulate decryption creating the key file
            def create_key_file(*args, **kwargs):
                key_file.write_text("AGE-SECRET-KEY-...")

            mock_decrypt.side_effect = create_key_file

            result = unprotect_age_key(tmp_path, mock_cli_ctx.runner)

            assert result is True
            mock_decrypt.assert_called_once()
            # GPG file should be deleted after decryption
            assert not gpg_file.exists()

    def test_returns_false_when_not_protected(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """unprotect_age_key returns False when key is not protected."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()

        result = unprotect_age_key(tmp_path, mock_cli_ctx.runner)
        assert result is False


class TestProtectedAgeKeyContextManager:
    """Tests for protected_age_key context manager."""

    def test_yields_plaintext_path_when_not_protected(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """protected_age_key yields plaintext key path when key is not GPG-protected."""
        key_file = make_age_key()

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=False):
            with protected_age_key(tmp_path, mock_cli_ctx.runner) as yielded_path:
                assert yielded_path == key_file
                assert key_file.exists()

    def test_raises_when_no_key_exists(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """protected_age_key raises ProtectedFileError when no key exists."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()

        with pytest.raises(ProtectedFileError, match="Age key not found"):
            with protected_age_key(tmp_path, mock_cli_ctx.runner):
                pass

    def test_decrypts_and_reencrypts_protected_key(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """protected_age_key decrypts key, yields path, then re-encrypts on exit."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()
        key_file = age_dir / "keys.txt"
        gpg_file = age_dir / "keys.txt.gpg"
        gpg_file.write_text("encrypted")

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=True):
            with patch(f"{PROTECTED_MODULE}.gpg_decrypt_file") as mock_decrypt:
                with patch(f"{PROTECTED_MODULE}.gpg_encrypt_file") as mock_encrypt:
                    # Simulate decryption creating the key file
                    def create_key_file(*args, **kwargs):
                        key_file.write_text("AGE-SECRET-KEY-...")

                    mock_decrypt.side_effect = create_key_file

                    with protected_age_key(tmp_path, mock_cli_ctx.runner) as yielded_path:
                        assert yielded_path == key_file
                        assert key_file.exists()
                        mock_decrypt.assert_called_once()

                    # After context exit, should re-encrypt
                    mock_encrypt.assert_called_once()

    def test_warns_and_encrypts_plaintext_key_on_exit(
        self, tmp_path: Path, make_age_key, mock_cli_ctx: CliContext
    ):
        """protected_age_key warns about plaintext key and encrypts on exit when GPG available."""
        key_file = make_age_key()

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=True):
            with patch(f"{PROTECTED_MODULE}.gpg_encrypt_file") as mock_encrypt:
                with patch("djb.secrets.protected.logger") as mock_logger:
                    with protected_age_key(tmp_path, mock_cli_ctx.runner) as yielded_path:
                        assert yielded_path == key_file

                    # Should warn about plaintext key
                    mock_logger.warning.assert_called()
                    # Should encrypt on exit
                    mock_encrypt.assert_called_once()

    def test_raises_click_exception_on_gpg_timeout(self, tmp_path: Path, mock_cli_ctx: CliContext):
        """protected_age_key raises ClickException with friendly message when GPG times out."""
        age_dir = tmp_path / ".age"
        age_dir.mkdir()
        # Note: keys.txt doesn't exist, only the encrypted version
        gpg_file = age_dir / "keys.txt.gpg"
        gpg_file.write_text("encrypted")

        with patch(f"{PROTECTED_MODULE}.check_gpg_installed", return_value=True):
            with patch(f"{PROTECTED_MODULE}.gpg_decrypt_file") as mock_decrypt:
                mock_decrypt.side_effect = GpgTimeoutError(
                    timeout=GPG_INTERACTIVE_TIMEOUT, operation="GPG decryption"
                )

                with pytest.raises(click.ClickException) as exc_info:
                    with protected_age_key(tmp_path, mock_cli_ctx.runner):
                        pass

                # Should have user-friendly message
                assert "timed out" in str(exc_info.value.message)
                assert "passphrase" in str(exc_info.value.message)
